from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from atletico_hub.auth.models import Account, Invite, Role, Session
from atletico_hub.auth.tokens import generate_token, hash_token
from atletico_hub.players.models import Player

MAX_FAILED_LOGINS = 5
LOCKOUT_DURATION = timedelta(minutes=15)
SESSION_DURATION = timedelta(days=30)
INVITE_DURATION = timedelta(days=7)
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
# A real argon2 hash of a password nobody has: login verifies against it when the email has no account.
DUMMY_PASSWORD_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=4$gqH/hNn7sqPFshYhUW6KZQ$0SSyWC1Gm7abesE5SdAWH6+puoRvTMV/LqC4LDwXiwA"
)


class InvalidCredentialsError(Exception):
    pass


class AccountLockedError(Exception):
    pass


class InvalidSessionError(Exception):
    pass


class InvalidInviteError(Exception):
    pass


class PlayerNotFoundError(Exception):
    pass


class EmailInUseError(Exception):
    pass


class EmailRequiredError(Exception):
    pass


class InvalidPasswordError(Exception):
    pass


@dataclass(frozen=True)
class InviteInfo:
    player: Player
    account: Account | None


class AuthStore(Protocol):
    def player_by_id(self, player_id: int) -> Player | None: ...

    def add_account(self, account: Account) -> Account: ...

    def account_by_email(self, email: str) -> Account | None: ...

    def account_by_player(self, player_id: int) -> Account | None: ...

    def delete_sessions_of_account(self, account_id: int) -> None: ...

    def add_invite(self, invite: Invite) -> Invite: ...

    def invite_by_token_hash(self, token_hash: str) -> Invite | None: ...

    def delete_open_invites_of_player(self, player_id: int) -> None: ...

    def add_session(self, session: Session) -> Session: ...

    def session_by_token_hash(self, token_hash: str) -> Session | None: ...

    def delete_session(self, session: Session) -> None: ...


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...

    def verify(self, password: str, password_hash: str) -> bool: ...


class Clock(Protocol):
    def now(self) -> datetime: ...


class Transaction(Protocol):
    def commit(self) -> None: ...


class AuthService:
    def __init__(self, store: AuthStore, hasher: PasswordHasher, clock: Clock, transaction: Transaction) -> None:
        self._store = store
        self._hasher = hasher
        self._clock = clock
        self._transaction = transaction

    def login(self, email: str, password: str) -> tuple[Account, str]:
        account = self._store.account_by_email(email.strip().lower())
        if account is None:
            self._hasher.verify(password, DUMMY_PASSWORD_HASH)
            raise InvalidCredentialsError("Unknown email or wrong password")
        now = self._clock.now()
        if account.locked_until is not None and account.locked_until > now:
            raise AccountLockedError(f"Account locked until {account.locked_until.isoformat()}")
        if not self._hasher.verify(password, account.password_hash):
            self._register_failed_login(account, now)
            raise InvalidCredentialsError("Unknown email or wrong password")
        account.failed_logins = 0
        account.locked_until = None
        token = self._start_session(account, now)
        self._transaction.commit()
        return account, token

    def authenticate(self, token: str) -> Account:
        session = self._store.session_by_token_hash(hash_token(token))
        if session is None:
            raise InvalidSessionError("Unknown session")
        now = self._clock.now()
        if now >= session.last_used_at + SESSION_DURATION:
            self._store.delete_session(session)
            self._transaction.commit()
            raise InvalidSessionError("Session expired")
        session.last_used_at = now
        self._transaction.commit()
        return session.account

    def logout(self, token: str) -> None:
        session = self._store.session_by_token_hash(hash_token(token))
        if session is not None:
            self._store.delete_session(session)
            self._transaction.commit()

    def create_invite(self, player_id: int) -> tuple[str, Invite]:
        player = self._store.player_by_id(player_id)
        if player is None:
            raise PlayerNotFoundError(f"No player with id {player_id}")
        now = self._clock.now()
        self._store.delete_open_invites_of_player(player_id)
        token = generate_token()
        invite = self._store.add_invite(
            Invite(player=player, token_hash=hash_token(token), expires_at=now + INVITE_DURATION, created_at=now)
        )
        self._transaction.commit()
        return token, invite

    def open_invite(self, token: str) -> InviteInfo:
        invite = self._valid_invite(token)
        return InviteInfo(player=invite.player, account=self._store.account_by_player(invite.player.id))

    def complete_invite(self, token: str, password: str, email: str | None) -> tuple[Account, str]:
        invite = self._valid_invite(token)
        self._check_password(password)
        now = self._clock.now()
        account = self._store.account_by_player(invite.player.id)
        if account is None:
            account = self._create_account(invite.player, email, password, Role.PLAYER)
        else:
            self._reset_password(account, password)
        invite.used_at = now
        session_token = self._start_session(account, now)
        self._transaction.commit()
        return account, session_token

    def create_admin(self, player: Player, email: str, password: str) -> Account:
        self._check_password(password)
        account = self._create_account(player, email, password, Role.ADMIN)
        self._transaction.commit()
        return account

    def _valid_invite(self, token: str) -> Invite:
        invite = self._store.invite_by_token_hash(hash_token(token))
        if invite is None or invite.used_at is not None or invite.expires_at <= self._clock.now():
            raise InvalidInviteError("Invite is unknown, used, cancelled or expired")
        return invite

    def _create_account(self, player: Player, email: str | None, password: str, role: Role) -> Account:
        if email is None:
            raise EmailRequiredError("A player without an account needs an email")
        email = email.strip().lower()
        if self._store.account_by_email(email) is not None:
            raise EmailInUseError("Email is already used by another account")
        return self._store.add_account(
            Account(player=player, email=email, password_hash=self._hasher.hash(password), role=role, failed_logins=0)
        )

    def _reset_password(self, account: Account, password: str) -> None:
        account.password_hash = self._hasher.hash(password)
        account.failed_logins = 0
        account.locked_until = None
        self._store.delete_sessions_of_account(account.id)

    @staticmethod
    def _check_password(password: str) -> None:
        if not PASSWORD_MIN_LENGTH <= len(password) <= PASSWORD_MAX_LENGTH:
            raise InvalidPasswordError(
                f"A password needs {PASSWORD_MIN_LENGTH} to {PASSWORD_MAX_LENGTH} characters, got {len(password)}"
            )

    def _register_failed_login(self, account: Account, now: datetime) -> None:
        account.failed_logins += 1
        if account.failed_logins >= MAX_FAILED_LOGINS:
            account.failed_logins = 0
            account.locked_until = now + LOCKOUT_DURATION
        self._transaction.commit()

    def _start_session(self, account: Account, now: datetime) -> str:
        token = generate_token()
        self._store.add_session(
            Session(account=account, token_hash=hash_token(token), last_used_at=now, created_at=now)
        )
        return token
