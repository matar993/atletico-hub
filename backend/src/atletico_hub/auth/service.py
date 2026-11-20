from datetime import datetime, timedelta
from typing import Protocol

from atletico_hub.auth.models import Account, Session
from atletico_hub.auth.tokens import generate_token, hash_token

MAX_FAILED_LOGINS = 5
LOCKOUT_DURATION = timedelta(minutes=15)
SESSION_DURATION = timedelta(days=30)
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


class AuthStore(Protocol):
    def account_by_email(self, email: str) -> Account | None: ...

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
