from datetime import UTC, datetime, timedelta

import pytest

from atletico_hub.auth.models import Account, Role, Session
from atletico_hub.auth.service import (
    DUMMY_PASSWORD_HASH,
    AccountLockedError,
    AuthService,
    InvalidCredentialsError,
    InvalidSessionError,
)
from atletico_hub.auth.tokens import hash_token
from atletico_hub.players.models import Player

START = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


class FakeAuthStore:
    def __init__(self) -> None:
        self.accounts: list[Account] = []
        self.sessions: list[Session] = []

    def account_by_email(self, email: str) -> Account | None:
        return next((account for account in self.accounts if account.email == email), None)

    def add_session(self, session: Session) -> Session:
        self.sessions.append(session)
        return session

    def session_by_token_hash(self, token_hash: str) -> Session | None:
        return next((session for session in self.sessions if session.token_hash == token_hash), None)

    def delete_session(self, session: Session) -> None:
        self.sessions.remove(session)


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
