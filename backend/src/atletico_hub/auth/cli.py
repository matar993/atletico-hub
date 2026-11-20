import argparse
import sys
from getpass import getpass

from sqlalchemy.orm import Session

from atletico_hub.auth.dependencies import SystemClock
from atletico_hub.auth.models import Account, Role
from atletico_hub.auth.passwords import Argon2PasswordHasher
from atletico_hub.auth.repository import AuthRepository
from atletico_hub.auth.service import (
    AccountNotFoundError,
    AuthService,
    EmailInUseError,
    InvalidPasswordError,
)
from atletico_hub.db.engine import get_session_factory
from atletico_hub.players.repository import PlayerRepository
from atletico_hub.players.service import InvalidPlayerNameError, PlayerService
from atletico_hub.users.repository import UserRepository
from atletico_hub.users.service import UserService


class _NoCommit:
    """Leaves the commit to the auth service, so the player and the account are saved together or not at all."""

    def commit(self) -> None:
        pass


def _auth_service(session: Session) -> AuthService:
    return AuthService(
        store=AuthRepository(session), hasher=Argon2PasswordHasher(), clock=SystemClock(), transaction=session
    )


def create_admin(session: Session, first_name: str, last_name: str, email: str, password: str) -> Account:
    player = PlayerService(players=PlayerRepository(session), transaction=_NoCommit()).add_player(
        first_name=first_name, last_name=last_name
    )
    return _auth_service(session).create_admin(player=player, email=email, password=password)


def promote(session: Session, email: str) -> Account:
    # The operator has the rights of the host: no acting account, but the service still cancels the invite links.
    account = AuthRepository(session).account_by_email(email.strip().lower())
    if account is None:
        raise AccountNotFoundError(f"No account with email {email.strip().lower()}")
    return UserService(users=UserRepository(session), transaction=session).change_role(account.id, Role.ADMIN)


def reset_password(session: Session, email: str, password: str) -> Account:
    return _auth_service(session).reset_password(email=email, password=password)


def _run_create_admin(session: Session) -> str:
    first_name = input("First name: ")
    last_name = input("Last name: ")
    email = input("Email: ")
    password = getpass("Password: ")
    return f"Admin created: {create_admin(session, first_name, last_name, email, password).email}"


def _run_promote(session: Session) -> str:
    return f"Admin: {promote(session, input('Email: ')).email}"


def _run_reset_password(session: Session) -> str:
    email = input("Email: ")
    password = getpass("New password: ")
    return f"Password reset: {reset_password(session, email, password).email}"


COMMANDS = {
    "create-admin": ("Create a player with an admin account", _run_create_admin),
    "promote": ("Give the admin role to the account with an email", _run_promote),
    "reset-password": ("Set a new password for the account with an email", _run_reset_password),
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="atletico-hub", description="Commands to run on the API host.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, (help_text, _) in COMMANDS.items():
        subparsers.add_parser(name, help=help_text, description=help_text)
    command = COMMANDS[parser.parse_args(argv).command][1]
    with get_session_factory()() as session:
        try:
            message = command(session)
        except (AccountNotFoundError, EmailInUseError, InvalidPasswordError, InvalidPlayerNameError) as ex:
            session.rollback()
            print(f"Error: {ex}", file=sys.stderr)
            return 1
    print(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
