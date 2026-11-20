from datetime import UTC, datetime, timedelta

import pytest

from atletico_hub.auth.models import Account, Invite, Role, Session
from atletico_hub.auth.service import (
    DUMMY_PASSWORD_HASH,
    INVITE_DURATION,
    AccountLockedError,
    AuthService,
    EmailInUseError,
    EmailRequiredError,
    InvalidCredentialsError,
    InvalidInviteError,
    InvalidPasswordError,
    InvalidSessionError,
    PlayerNotFoundError,
)
from atletico_hub.auth.tokens import hash_token
from atletico_hub.players.models import Player

START = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


class FakeAuthStore:
    def __init__(self) -> None:
        self.players: list[Player] = []
        self.accounts: list[Account] = []
        self.sessions: list[Session] = []
        self.invites: list[Invite] = []

    def player_by_id(self, player_id: int) -> Player | None:
        return next((player for player in self.players if player.id == player_id), None)

    def add_account(self, account: Account) -> Account:
        self.accounts.append(account)
        return account

    def account_by_email(self, email: str) -> Account | None:
        return next((account for account in self.accounts if account.email == email), None)

    def account_by_player(self, player_id: int) -> Account | None:
        return next((account for account in self.accounts if account.player.id == player_id), None)

    def add_session(self, session: Session) -> Session:
        self.sessions.append(session)
        return session

    def session_by_token_hash(self, token_hash: str) -> Session | None:
        return next((session for session in self.sessions if session.token_hash == token_hash), None)

    def delete_session(self, session: Session) -> None:
        self.sessions.remove(session)

    def delete_sessions_of_account(self, account_id: int) -> None:
        self.sessions = [session for session in self.sessions if session.account.id != account_id]

    def add_invite(self, invite: Invite) -> Invite:
        self.invites.append(invite)
        return invite

    def invite_by_token_hash(self, token_hash: str) -> Invite | None:
        return next((invite for invite in self.invites if invite.token_hash == token_hash), None)

    def delete_open_invites_of_player(self, player_id: int) -> None:
        self.invites = [
            invite for invite in self.invites if invite.player.id != player_id or invite.used_at is not None
        ]


class FakeHasher:
    def __init__(self) -> None:
        self.verified_hashes: list[str] = []

    def hash(self, password: str) -> str:
        return f"hashed:{password}"

    def verify(self, password: str, password_hash: str) -> bool:
        self.verified_hashes.append(password_hash)
        return password_hash == f"hashed:{password}"


class FakeClock:
    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now

    def advance(self, by: timedelta) -> None:
        self._now += by


class FakeTransaction:
    def __init__(self) -> None:
        self.commits = 0

    def commit(self) -> None:
        self.commits += 1


class TestAuthService:
    def test_login_starts_a_session_and_returns_the_account_and_a_token(self) -> None:
        store = FakeAuthStore()
        store.accounts.append(
            Account(
                player=Player(first_name="Anna", last_name="Rossi"),
                email="anna@example.com",
                password_hash="hashed:secret-pass",
                role=Role.PLAYER,
                failed_logins=0,
            )
        )
        transaction = FakeTransaction()
        service = AuthService(store=store, hasher=FakeHasher(), clock=FakeClock(START), transaction=transaction)

        account, token = service.login(email="anna@example.com", password="secret-pass")

        assert account.email == "anna@example.com"
        assert [session.token_hash for session in store.sessions] == [hash_token(token)]
        assert store.sessions[0].last_used_at == START
        assert transaction.commits == 1

    def test_login_matches_the_email_without_regard_to_case_and_spaces(self) -> None:
        store = FakeAuthStore()
        store.accounts.append(
            Account(
                player=Player(first_name="Anna", last_name="Rossi"),
                email="anna@example.com",
                password_hash="hashed:secret-pass",
                role=Role.PLAYER,
                failed_logins=0,
            )
        )
        service = AuthService(store=store, hasher=FakeHasher(), clock=FakeClock(START), transaction=FakeTransaction())

        account, _ = service.login(email=" Anna@Example.COM ", password="secret-pass")

        assert account.email == "anna@example.com"

    def test_login_refuses_a_wrong_password_and_starts_no_session(self) -> None:
        store = FakeAuthStore()
        store.accounts.append(
            Account(
                player=Player(first_name="Anna", last_name="Rossi"),
                email="anna@example.com",
                password_hash="hashed:secret-pass",
                role=Role.PLAYER,
                failed_logins=0,
            )
        )
        service = AuthService(store=store, hasher=FakeHasher(), clock=FakeClock(START), transaction=FakeTransaction())

        with pytest.raises(InvalidCredentialsError):
            service.login(email="anna@example.com", password="wrong-pass")

        assert store.sessions == []
        assert store.accounts[0].failed_logins == 1

    def test_login_refuses_an_unknown_email_after_verifying_against_the_dummy_hash(self) -> None:
        hasher = FakeHasher()
        service = AuthService(
            store=FakeAuthStore(), hasher=hasher, clock=FakeClock(START), transaction=FakeTransaction()
        )

        with pytest.raises(InvalidCredentialsError):
            service.login(email="nobody@example.com", password="whatever-pass")

        assert hasher.verified_hashes == [DUMMY_PASSWORD_HASH]

    def test_login_locks_the_account_after_five_failures_even_with_the_right_password(self) -> None:
        store = FakeAuthStore()
        store.accounts.append(
            Account(
                player=Player(first_name="Anna", last_name="Rossi"),
                email="anna@example.com",
                password_hash="hashed:secret-pass",
                role=Role.PLAYER,
                failed_logins=0,
            )
        )
        service = AuthService(store=store, hasher=FakeHasher(), clock=FakeClock(START), transaction=FakeTransaction())
        for _ in range(5):
            with pytest.raises(InvalidCredentialsError):
                service.login(email="anna@example.com", password="wrong-pass")

        with pytest.raises(AccountLockedError):
            service.login(email="anna@example.com", password="secret-pass")

        assert store.sessions == []

    def test_login_works_again_after_the_lock_of_15_minutes(self) -> None:
        store = FakeAuthStore()
        store.accounts.append(
            Account(
                player=Player(first_name="Anna", last_name="Rossi"),
                email="anna@example.com",
                password_hash="hashed:secret-pass",
                role=Role.PLAYER,
                failed_logins=0,
            )
        )
        clock = FakeClock(START)
        service = AuthService(store=store, hasher=FakeHasher(), clock=clock, transaction=FakeTransaction())
        for _ in range(5):
            with pytest.raises(InvalidCredentialsError):
                service.login(email="anna@example.com", password="wrong-pass")
        clock.advance(timedelta(minutes=14))
        with pytest.raises(AccountLockedError):
            service.login(email="anna@example.com", password="secret-pass")
        clock.advance(timedelta(minutes=1))

        service.login(email="anna@example.com", password="secret-pass")

        assert len(store.sessions) == 1

    def test_login_success_resets_the_count_of_failures(self) -> None:
        store = FakeAuthStore()
        store.accounts.append(
            Account(
                player=Player(first_name="Anna", last_name="Rossi"),
                email="anna@example.com",
                password_hash="hashed:secret-pass",
                role=Role.PLAYER,
                failed_logins=0,
            )
        )
        service = AuthService(store=store, hasher=FakeHasher(), clock=FakeClock(START), transaction=FakeTransaction())
        for _ in range(4):
            with pytest.raises(InvalidCredentialsError):
                service.login(email="anna@example.com", password="wrong-pass")
        _, token = service.login(email="anna@example.com", password="secret-pass")
        service.logout(token=token)

        with pytest.raises(InvalidCredentialsError):
            service.login(email="anna@example.com", password="wrong-pass")

        assert store.accounts[0].failed_logins == 1
        assert store.accounts[0].locked_until is None

    def test_authenticate_extends_the_session_to_30_days_from_the_request(self) -> None:
        store = FakeAuthStore()
        store.accounts.append(
            Account(
                player=Player(first_name="Anna", last_name="Rossi"),
                email="anna@example.com",
                password_hash="hashed:secret-pass",
                role=Role.PLAYER,
                failed_logins=0,
            )
        )
        clock = FakeClock(START)
        service = AuthService(store=store, hasher=FakeHasher(), clock=clock, transaction=FakeTransaction())
        _, token = service.login(email="anna@example.com", password="secret-pass")
        clock.advance(timedelta(days=20))

        account = service.authenticate(token=token)
        clock.advance(timedelta(days=29))
        service.authenticate(token=token)

        assert account.email == "anna@example.com"
        assert store.sessions[0].last_used_at == START + timedelta(days=49)

    def test_authenticate_refuses_a_session_unused_for_31_days_and_removes_it(self) -> None:
        store = FakeAuthStore()
        store.accounts.append(
            Account(
                player=Player(first_name="Anna", last_name="Rossi"),
                email="anna@example.com",
                password_hash="hashed:secret-pass",
                role=Role.PLAYER,
                failed_logins=0,
            )
        )
        clock = FakeClock(START)
        service = AuthService(store=store, hasher=FakeHasher(), clock=clock, transaction=FakeTransaction())
        _, token = service.login(email="anna@example.com", password="secret-pass")
        clock.advance(timedelta(days=31))

        with pytest.raises(InvalidSessionError):
            service.authenticate(token=token)

        assert store.sessions == []

    def test_authenticate_refuses_an_unknown_token(self) -> None:
        service = AuthService(
            store=FakeAuthStore(), hasher=FakeHasher(), clock=FakeClock(START), transaction=FakeTransaction()
        )

        with pytest.raises(InvalidSessionError):
            service.authenticate(token="unknown")

    def test_logout_ends_the_session(self) -> None:
        store = FakeAuthStore()
        store.accounts.append(
            Account(
                player=Player(first_name="Anna", last_name="Rossi"),
                email="anna@example.com",
                password_hash="hashed:secret-pass",
                role=Role.PLAYER,
                failed_logins=0,
            )
        )
        service = AuthService(store=store, hasher=FakeHasher(), clock=FakeClock(START), transaction=FakeTransaction())
        _, token = service.login(email="anna@example.com", password="secret-pass")

        service.logout(token=token)

        with pytest.raises(InvalidSessionError):
            service.authenticate(token=token)

    def test_logout_ignores_an_unknown_token(self) -> None:
        transaction = FakeTransaction()
        service = AuthService(
            store=FakeAuthStore(), hasher=FakeHasher(), clock=FakeClock(START), transaction=transaction
        )

        service.logout(token="unknown")

        assert transaction.commits == 0

    def test_create_invite_stores_the_hash_with_a_7_day_expiry_and_commits(self) -> None:
        store = FakeAuthStore()
        store.players.append(Player(id=1, first_name="Anna", last_name="Rossi"))
        transaction = FakeTransaction()
        service = AuthService(store=store, hasher=FakeHasher(), clock=FakeClock(START), transaction=transaction)

        token, invite = service.create_invite(player_id=1)

        assert invite.token_hash == hash_token(token)
        assert invite.expires_at == START + INVITE_DURATION
        assert timedelta(days=7) == INVITE_DURATION
        assert store.invites == [invite]
        assert transaction.commits == 1

    def test_create_invite_refuses_an_unknown_player(self) -> None:
        service = AuthService(
            store=FakeAuthStore(), hasher=FakeHasher(), clock=FakeClock(START), transaction=FakeTransaction()
        )

        with pytest.raises(PlayerNotFoundError):
            service.create_invite(player_id=99)

    def test_create_invite_cancels_the_earlier_links_of_the_player(self) -> None:
        store = FakeAuthStore()
        store.players.append(Player(id=1, first_name="Anna", last_name="Rossi"))
        service = AuthService(store=store, hasher=FakeHasher(), clock=FakeClock(START), transaction=FakeTransaction())
        first_token, _ = service.create_invite(player_id=1)

        second_token, _ = service.create_invite(player_id=1)

        with pytest.raises(InvalidInviteError):
            service.open_invite(token=first_token)
        assert service.open_invite(token=second_token).player.id == 1

    def test_open_invite_refuses_an_unknown_token(self) -> None:
        service = AuthService(
            store=FakeAuthStore(), hasher=FakeHasher(), clock=FakeClock(START), transaction=FakeTransaction()
        )

        with pytest.raises(InvalidInviteError):
            service.open_invite(token="unknown")

    def test_open_invite_refuses_a_link_created_8_days_ago(self) -> None:
        store = FakeAuthStore()
        store.players.append(Player(id=1, first_name="Anna", last_name="Rossi"))
        clock = FakeClock(START)
        service = AuthService(store=store, hasher=FakeHasher(), clock=clock, transaction=FakeTransaction())
        token, _ = service.create_invite(player_id=1)
        clock.advance(timedelta(days=7))

        with pytest.raises(InvalidInviteError):
            service.open_invite(token=token)

    def test_open_invite_gives_the_player_and_no_account_for_a_new_player(self) -> None:
        store = FakeAuthStore()
        store.players.append(Player(id=1, first_name="Anna", last_name="Rossi"))
        service = AuthService(store=store, hasher=FakeHasher(), clock=FakeClock(START), transaction=FakeTransaction())
        token, _ = service.create_invite(player_id=1)

        info = service.open_invite(token=token)

        assert (info.player.first_name, info.account) == ("Anna", None)

    def test_open_invite_gives_the_account_of_a_player_who_has_one(self) -> None:
        store = FakeAuthStore()
        player = Player(id=1, first_name="Anna", last_name="Rossi")
        store.players.append(player)
        store.accounts.append(
            Account(id=1, player=player, email="anna@example.com", password_hash="x", role=Role.PLAYER, failed_logins=0)
        )
        service = AuthService(store=store, hasher=FakeHasher(), clock=FakeClock(START), transaction=FakeTransaction())
        token, _ = service.create_invite(player_id=1)

        info = service.open_invite(token=token)

        assert info.account is not None
        assert info.account.email == "anna@example.com"

    def test_complete_invite_creates_a_player_account_and_starts_a_session(self) -> None:
        store = FakeAuthStore()
        store.players.append(Player(id=1, first_name="Anna", last_name="Rossi"))
        hasher = FakeHasher()
        service = AuthService(store=store, hasher=hasher, clock=FakeClock(START), transaction=FakeTransaction())
        token, invite = service.create_invite(player_id=1)

        account, session_token = service.complete_invite(
            token=token, password="a password of 10", email="Anna@Example.com"
        )

        assert (account.email, account.role) == ("anna@example.com", Role.PLAYER)
        assert account.password_hash == "hashed:a password of 10"
        assert store.accounts == [account]
        assert service.authenticate(token=session_token) == account
        assert invite.used_at == START

    def test_complete_invite_cannot_be_used_twice(self) -> None:
        store = FakeAuthStore()
        store.players.append(Player(id=1, first_name="Anna", last_name="Rossi"))
        service = AuthService(store=store, hasher=FakeHasher(), clock=FakeClock(START), transaction=FakeTransaction())
        token, _ = service.create_invite(player_id=1)
        service.complete_invite(token=token, password="a password of 10", email="anna@example.com")

        with pytest.raises(InvalidInviteError):
            service.open_invite(token=token)
        with pytest.raises(InvalidInviteError):
            service.complete_invite(token=token, password="a password of 10", email="anna@example.com")

    def test_complete_invite_with_an_email_in_use_changes_nothing_and_keeps_the_link_valid(self) -> None:
        store = FakeAuthStore()
        other = Player(id=2, first_name="Mario", last_name="Verdi")
        store.players.extend([Player(id=1, first_name="Anna", last_name="Rossi"), other])
        store.accounts.append(
            Account(id=1, player=other, email="mario@example.com", password_hash="x", role=Role.PLAYER, failed_logins=0)
        )
        service = AuthService(store=store, hasher=FakeHasher(), clock=FakeClock(START), transaction=FakeTransaction())
        token, invite = service.create_invite(player_id=1)

        with pytest.raises(EmailInUseError):
            service.complete_invite(token=token, password="a password of 10", email="Mario@Example.com")

        assert len(store.accounts) == 1
        assert store.sessions == []
        assert invite.used_at is None
        assert service.open_invite(token=token).player.id == 1

    def test_complete_invite_needs_an_email_for_a_player_without_an_account(self) -> None:
        store = FakeAuthStore()
        store.players.append(Player(id=1, first_name="Anna", last_name="Rossi"))
        service = AuthService(store=store, hasher=FakeHasher(), clock=FakeClock(START), transaction=FakeTransaction())
        token, _ = service.create_invite(player_id=1)

        with pytest.raises(EmailRequiredError):
            service.complete_invite(token=token, password="a password of 10", email=None)

    def test_complete_invite_refuses_a_password_of_7_characters_and_accepts_one_without_digits(self) -> None:
        store = FakeAuthStore()
        store.players.append(Player(id=1, first_name="Anna", last_name="Rossi"))
        service = AuthService(store=store, hasher=FakeHasher(), clock=FakeClock(START), transaction=FakeTransaction())
        token, invite = service.create_invite(player_id=1)

        with pytest.raises(InvalidPasswordError):
            service.complete_invite(token=token, password="1234567", email="anna@example.com")
        assert invite.used_at is None
        account, _ = service.complete_invite(token=token, password="calcetto del martedi", email="anna@example.com")

        assert account.email == "anna@example.com"

    def test_complete_invite_refuses_a_password_of_129_characters(self) -> None:
        store = FakeAuthStore()
        store.players.append(Player(id=1, first_name="Anna", last_name="Rossi"))
        service = AuthService(store=store, hasher=FakeHasher(), clock=FakeClock(START), transaction=FakeTransaction())
        token, _ = service.create_invite(player_id=1)

        with pytest.raises(InvalidPasswordError):
            service.complete_invite(token=token, password="a" * 129, email="anna@example.com")

    def test_complete_invite_resets_the_password_and_ends_every_session(self) -> None:
        store = FakeAuthStore()
        player = Player(id=1, first_name="Anna", last_name="Rossi")
        store.players.append(player)
        store.accounts.append(
            Account(
                id=1,
                player=player,
                email="anna@example.com",
                password_hash="hashed:old-password",
                role=Role.ADMIN,
                failed_logins=0,
            )
        )
        service = AuthService(store=store, hasher=FakeHasher(), clock=FakeClock(START), transaction=FakeTransaction())
        _, first_phone = service.login(email="anna@example.com", password="old-password")
        _, second_phone = service.login(email="anna@example.com", password="old-password")
        token, _ = service.create_invite(player_id=1)

        account, third_device = service.complete_invite(token=token, password="new-password", email=None)

        with pytest.raises(InvalidSessionError):
            service.authenticate(token=first_phone)
        with pytest.raises(InvalidSessionError):
            service.authenticate(token=second_phone)
        assert service.authenticate(token=third_device) == account
        assert (account.email, account.role) == ("anna@example.com", Role.ADMIN)
        service.login(email="anna@example.com", password="new-password")
        with pytest.raises(InvalidCredentialsError):
            service.login(email="anna@example.com", password="old-password")

    def test_complete_invite_for_a_reset_clears_the_lockout(self) -> None:
        store = FakeAuthStore()
        player = Player(id=1, first_name="Anna", last_name="Rossi")
        store.players.append(player)
        store.accounts.append(
            Account(
                id=1,
                player=player,
                email="anna@example.com",
                password_hash="hashed:old-password",
                role=Role.PLAYER,
                failed_logins=0,
            )
        )
        service = AuthService(store=store, hasher=FakeHasher(), clock=FakeClock(START), transaction=FakeTransaction())
        for _ in range(5):
            with pytest.raises(InvalidCredentialsError):
                service.login(email="anna@example.com", password="wrong-pass")
        token, _ = service.create_invite(player_id=1)

        service.complete_invite(token=token, password="new-password", email=None)

        service.login(email="anna@example.com", password="new-password")
