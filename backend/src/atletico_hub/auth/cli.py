import sys
from getpass import getpass

from sqlalchemy.orm import Session

from atletico_hub.auth.dependencies import SystemClock
from atletico_hub.auth.models import Account
from atletico_hub.auth.passwords import Argon2PasswordHasher
from atletico_hub.auth.repository import AuthRepository
from atletico_hub.auth.service import AuthService, EmailInUseError, InvalidPasswordError
from atletico_hub.db.engine import get_session_factory
from atletico_hub.players.repository import PlayerRepository
from atletico_hub.players.service import InvalidPlayerNameError, PlayerService


class _NoCommit:
    """Leaves the commit to the auth service, so the player and the account are saved together or not at all."""

    def commit(self) -> None:
        pass


def create_admin(session: Session, first_name: str, last_name: str, email: str, password: str) -> Account:
    player = PlayerService(players=PlayerRepository(session), transaction=_NoCommit()).add_player(
        first_name=first_name, last_name=last_name
    )
    auth = AuthService(
        store=AuthRepository(session), hasher=Argon2PasswordHasher(), clock=SystemClock(), transaction=session
    )
    return auth.create_admin(player=player, email=email, password=password)


def main() -> int:
    first_name = input("First name: ")
    last_name = input("Last name: ")
    email = input("Email: ")
    password = getpass("Password: ")
    with get_session_factory()() as session:
        try:
            account = create_admin(session, first_name, last_name, email, password)
        except (EmailInUseError, InvalidPasswordError, InvalidPlayerNameError) as ex:
            session.rollback()
            print(f"Error: {ex}", file=sys.stderr)
            return 1
        print(f"Admin created: {account.email}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
