from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session as DbSession

from atletico_hub.auth.models import Account, Role
from atletico_hub.auth.passwords import Argon2PasswordHasher
from atletico_hub.auth.repository import AuthRepository
from atletico_hub.auth.service import SESSION_DURATION, AuthService, InvalidSessionError
from atletico_hub.auth.settings import AuthSettings
from atletico_hub.db.session import get_session

CSRF_HEADER = "X-Requested-With"
CSRF_VALUE = "atletico-hub"
SESSION_COOKIE = "atletico_session"
WRITE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


def get_auth_settings() -> AuthSettings:
    return AuthSettings()


def get_auth_service(session: Annotated[DbSession, Depends(get_session)]) -> AuthService:
    return AuthService(
        store=AuthRepository(session), hasher=Argon2PasswordHasher(), clock=SystemClock(), transaction=session
    )


def set_session_cookie(response: Response, token: str, settings: AuthSettings) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=int(SESSION_DURATION.total_seconds()),
        path="/",
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )


def require_csrf_header(request: Request) -> None:
    if request.method in WRITE_METHODS and request.headers.get(CSRF_HEADER) != CSRF_VALUE:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=f"Missing header {CSRF_HEADER}: {CSRF_VALUE}")


def current_account(
    request: Request,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[AuthSettings, Depends(get_auth_settings)],
) -> Account:
    token = request.cookies.get(SESSION_COOKIE)
    if token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not signed in")
    try:
        account = service.authenticate(token)
    except InvalidSessionError as ex:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not signed in") from ex
    set_session_cookie(response, token, settings)
    return account


def require_admin(account: Annotated[Account, Depends(current_account)]) -> Account:
    if account.role != Role.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Admin only")
    return account
