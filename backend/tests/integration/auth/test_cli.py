from sqlalchemy.orm import Session as DbSession

from atletico_hub.auth.cli import create_admin
from atletico_hub.auth.models import Role
from atletico_hub.auth.passwords import Argon2PasswordHasher


class TestCreateAdmin:
    def test_creates_the_player_and_an_admin_account_with_a_usable_password(self, db_session: DbSession) -> None:
        account = create_admin(db_session, "Anna", "Rossi", "anna@example.com", "secret-pass")

        assert account.role == Role.ADMIN
        assert account.player.first_name == "Anna"
        assert Argon2PasswordHasher().verify("secret-pass", account.password_hash)
