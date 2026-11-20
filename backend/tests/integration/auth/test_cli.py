from collections.abc import Callable

import pytest
from sqlalchemy.orm import Session as DbSession

from atletico_hub.auth import cli
from atletico_hub.auth.cli import create_admin, main, promote, reset_password
from atletico_hub.auth.models import Account, Invite, Role
from atletico_hub.auth.passwords import Argon2PasswordHasher
from atletico_hub.auth.service import AccountNotFoundError, InvalidPasswordError
from atletico_hub.players.models import Player


def add_player_account(db_session: DbSession, role: Role = Role.PLAYER) -> Account:
    account = Account(
        player=Player(first_name="Luca", last_name="Bianchi"),
        email="luca@example.com",
        password_hash=Argon2PasswordHasher().hash("old-password"),
        role=role,
        failed_logins=0,
    )
    db_session.add(account)
    db_session.flush()
    return account


@pytest.fixture
def on_test_session(monkeypatch: pytest.MonkeyPatch, db_session: DbSession) -> Callable[[str, str], None]:
    """Runs main() on the test session, with the answers the operator would type."""
    monkeypatch.setattr(cli, "get_session_factory", lambda: lambda: db_session)

    def answer(inputs: str, password: str) -> None:
        answers = iter(inputs.split("|"))
        monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))
        monkeypatch.setattr(cli, "getpass", lambda _prompt="": password)

    return answer


class TestCreateAdmin:
    def test_creates_the_player_and_an_admin_account_with_a_usable_password(self, db_session: DbSession) -> None:
        account = create_admin(db_session, "Anna", "Rossi", "anna@example.com", "secret-pass")

        assert account.role == Role.ADMIN
        assert account.player.first_name == "Anna"
        assert Argon2PasswordHasher().verify("secret-pass", account.password_hash)


class TestPromote:
    def test_gives_the_admin_role_and_cancels_the_open_invite_links(self, db_session: DbSession) -> None:
        luca = add_player_account(db_session)
        invite = Invite(player_id=luca.player_id, token_hash="open", expires_at=luca.created_at)
        db_session.add(invite)
        db_session.flush()

        account = promote(db_session, " Luca@Example.com ")

        assert account.role == Role.ADMIN
        assert db_session.get(Invite, invite.id) is None

    def test_refuses_an_unknown_email(self, db_session: DbSession) -> None:
        with pytest.raises(AccountNotFoundError):
            promote(db_session, "nobody@example.com")


class TestResetPassword:
    def test_sets_a_password_that_works(self, db_session: DbSession) -> None:
        luca = add_player_account(db_session, Role.ADMIN)

        reset_password(db_session, "luca@example.com", "new-password")

        assert Argon2PasswordHasher().verify("new-password", luca.password_hash)

    def test_refuses_a_short_password_and_keeps_the_old_one(self, db_session: DbSession) -> None:
        luca = add_player_account(db_session)

        with pytest.raises(InvalidPasswordError):
            reset_password(db_session, "luca@example.com", "short")

        assert Argon2PasswordHasher().verify("old-password", luca.password_hash)


class TestMain:
    def test_help_lists_the_three_subcommands(self, capsys: pytest.CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit) as exit_info:
            main(["--help"])

        output = capsys.readouterr().out
        assert exit_info.value.code == 0
        assert all(name in output for name in ("create-admin", "promote", "reset-password"))

    def test_a_missing_subcommand_is_refused(self) -> None:
        with pytest.raises(SystemExit) as exit_info:
            main([])

        assert exit_info.value.code != 0

    def test_create_admin_asks_the_inputs_and_prints_the_email(
        self, on_test_session: Callable[[str, str], None], capsys: pytest.CaptureFixture[str]
    ) -> None:
        on_test_session("Anna|Rossi|anna@example.com", "secret-pass")

        assert main(["create-admin"]) == 0

        assert capsys.readouterr().out == "Admin created: anna@example.com\n"

    def test_promote_makes_the_player_an_admin(
        self, on_test_session: Callable[[str, str], None], db_session: DbSession
    ) -> None:
        luca = add_player_account(db_session)
        on_test_session("luca@example.com", "")

        assert main(["promote"]) == 0

        assert luca.role == Role.ADMIN

    def test_promote_fails_on_an_unknown_email_and_says_why(
        self, on_test_session: Callable[[str, str], None], capsys: pytest.CaptureFixture[str]
    ) -> None:
        on_test_session("nobody@example.com", "")

        assert main(["promote"]) == 1

        assert capsys.readouterr().err == "Error: No account with email nobody@example.com\n"

    def test_reset_password_sets_the_password(
        self, on_test_session: Callable[[str, str], None], db_session: DbSession
    ) -> None:
        luca = add_player_account(db_session, Role.ADMIN)
        on_test_session("luca@example.com", "new-password")

        assert main(["reset-password"]) == 0

        assert Argon2PasswordHasher().verify("new-password", luca.password_hash)

    def test_reset_password_fails_on_a_password_of_7_characters_and_keeps_the_old_one(
        self, on_test_session: Callable[[str, str], None], db_session: DbSession, capsys: pytest.CaptureFixture[str]
    ) -> None:
        luca = add_player_account(db_session)
        on_test_session("luca@example.com", "1234567")

        assert main(["reset-password"]) == 1

        assert "Error: A password needs 8 to 128 characters, got 7" in capsys.readouterr().err
        assert Argon2PasswordHasher().verify("old-password", luca.password_hash)
