from datetime import UTC, datetime

from sqlalchemy.orm import Session as DbSession

from atletico_hub.auth.models import Account, Invite, Role, Session
from atletico_hub.auth.repository import AuthRepository
from atletico_hub.players.models import Player

NOW = datetime(2026, 1, 1, tzinfo=UTC)


class TestAuthRepository:
    def test_account_by_email_finds_the_account(self, db_session: DbSession) -> None:
        repository = AuthRepository(db_session)
        player = Player(first_name="Anna", last_name="Rossi")
        db_session.add(player)
        db_session.flush()
        repository.add_account(
            account=Account(player_id=player.id, email="anna@example.com", password_hash="hash", role=Role.PLAYER)
        )

        account = repository.account_by_email(email="anna@example.com")

        assert account is not None
        assert account.player_id == player.id
        assert account.role == Role.PLAYER
        assert repository.account_by_email(email="other@example.com") is None

    def test_account_by_player_finds_the_account(self, db_session: DbSession) -> None:
        repository = AuthRepository(db_session)
        player = Player(first_name="Anna", last_name="Rossi")
        other = Player(first_name="Luca", last_name="Bianchi")
        db_session.add_all([player, other])
        db_session.flush()
        repository.add_account(
            account=Account(player_id=player.id, email="anna@example.com", password_hash="hash", role=Role.ADMIN)
        )

        account = repository.account_by_player(player_id=player.id)

        assert account is not None
        assert account.email == "anna@example.com"
        assert repository.account_by_player(player_id=other.id) is None

    def test_session_by_token_hash_finds_the_session(self, db_session: DbSession) -> None:
        repository = AuthRepository(db_session)
        player = Player(first_name="Anna", last_name="Rossi")
        db_session.add(player)
        db_session.flush()
        account = repository.add_account(
            account=Account(player_id=player.id, email="anna@example.com", password_hash="hash", role=Role.PLAYER)
        )
        repository.add_session(session=Session(account_id=account.id, token_hash="abc", last_used_at=NOW))

        assert repository.session_by_token_hash(token_hash="abc") is not None
        assert repository.session_by_token_hash(token_hash="zzz") is None

    def test_delete_session_removes_it(self, db_session: DbSession) -> None:
        repository = AuthRepository(db_session)
        player = Player(first_name="Anna", last_name="Rossi")
        db_session.add(player)
        db_session.flush()
        account = repository.add_account(
            account=Account(player_id=player.id, email="anna@example.com", password_hash="hash", role=Role.PLAYER)
        )
        session = repository.add_session(session=Session(account_id=account.id, token_hash="abc", last_used_at=NOW))

        repository.delete_session(session=session)

        assert repository.session_by_token_hash(token_hash="abc") is None

    def test_delete_sessions_of_account_keeps_other_accounts_sessions(self, db_session: DbSession) -> None:
        repository = AuthRepository(db_session)
        player = Player(first_name="Anna", last_name="Rossi")
        other_player = Player(first_name="Luca", last_name="Bianchi")
        db_session.add_all([player, other_player])
        db_session.flush()
        account = repository.add_account(
            account=Account(player_id=player.id, email="anna@example.com", password_hash="hash", role=Role.PLAYER)
        )
        other = repository.add_account(
            account=Account(player_id=other_player.id, email="luca@example.com", password_hash="hash", role=Role.PLAYER)
        )
        repository.add_session(session=Session(account_id=account.id, token_hash="one", last_used_at=NOW))
        repository.add_session(session=Session(account_id=account.id, token_hash="two", last_used_at=NOW))
        repository.add_session(session=Session(account_id=other.id, token_hash="three", last_used_at=NOW))

        repository.delete_sessions_of_account(account_id=account.id)

        assert repository.session_by_token_hash(token_hash="one") is None
        assert repository.session_by_token_hash(token_hash="two") is None
        assert repository.session_by_token_hash(token_hash="three") is not None

    def test_invite_by_token_hash_finds_the_invite(self, db_session: DbSession) -> None:
        repository = AuthRepository(db_session)
        player = Player(first_name="Anna", last_name="Rossi")
        db_session.add(player)
        db_session.flush()
        repository.add_invite(invite=Invite(player_id=player.id, token_hash="abc", expires_at=NOW))

        invite = repository.invite_by_token_hash(token_hash="abc")

        assert invite is not None
        assert invite.used_at is None
        assert repository.invite_by_token_hash(token_hash="zzz") is None

    def test_delete_open_invites_of_player_keeps_used_and_other_invites(self, db_session: DbSession) -> None:
        repository = AuthRepository(db_session)
        player = Player(first_name="Anna", last_name="Rossi")
        other = Player(first_name="Luca", last_name="Bianchi")
        db_session.add_all([player, other])
        db_session.flush()
        repository.add_invite(invite=Invite(player_id=player.id, token_hash="open", expires_at=NOW))
        repository.add_invite(invite=Invite(player_id=player.id, token_hash="used", expires_at=NOW, used_at=NOW))
        repository.add_invite(invite=Invite(player_id=other.id, token_hash="other", expires_at=NOW))

        repository.delete_open_invites_of_player(player_id=player.id)

        assert repository.invite_by_token_hash(token_hash="open") is None
        assert repository.invite_by_token_hash(token_hash="used") is not None
        assert repository.invite_by_token_hash(token_hash="other") is not None
