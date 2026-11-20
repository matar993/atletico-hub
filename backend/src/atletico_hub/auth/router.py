from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from atletico_hub.auth.dependencies import (
    SESSION_COOKIE,
    current_account,
    get_auth_service,
    get_auth_settings,
    require,
    set_session_cookie,
)
from atletico_hub.auth.models import Account
from atletico_hub.auth.permissions import Permission
from atletico_hub.auth.schemas import (
    AcceptInviteRequest,
    CreateInviteRequest,
    CurrentUser,
    InviteCreated,
    InviteDetails,
    LoginRequest,
)
from atletico_hub.auth.service import (
    AccountLockedError,
    AuthService,
    EmailInUseError,
    EmailRequiredError,
    InvalidCredentialsError,
    InvalidInviteError,
    InvalidPasswordError,
    PlayerNotFoundError,
)
from atletico_hub.auth.settings import AuthSettings

router = APIRouter(prefix="/auth", tags=["auth"])

ServiceDep = Annotated[AuthService, Depends(get_auth_service)]
SettingsDep = Annotated[AuthSettings, Depends(get_auth_settings)]


@router.post("/login")
def login(body: LoginRequest, response: Response, service: ServiceDep, settings: SettingsDep) -> CurrentUser:
    try:
        account, token = service.login(email=body.email, password=body.password)
    except InvalidCredentialsError as ex:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Email o password non corretti") from ex
    except AccountLockedError as ex:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, detail="Troppi tentativi, riprova tra 15 minuti") from ex
    set_session_cookie(response, token, settings)
    return CurrentUser.from_account(account)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, service: ServiceDep, settings: SettingsDep) -> None:
    token = request.cookies.get(SESSION_COOKIE)
    if token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not signed in")
    service.logout(token)
    response.delete_cookie(SESSION_COOKIE, path="/", httponly=True, samesite="lax", secure=settings.cookie_secure)


@router.get("/me")
def me(account: Annotated[Account, Depends(current_account)]) -> CurrentUser:
    return CurrentUser.from_account(account)


@router.post("/invites", dependencies=[Depends(require(Permission.INVITES_CREATE))])
def create_invite(body: CreateInviteRequest, service: ServiceDep) -> InviteCreated:
    try:
        token, invite = service.create_invite(player_id=body.player_id)
    except PlayerNotFoundError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Player not found") from ex
    return InviteCreated(path=f"/invite/{token}", expires_at=invite.expires_at)


@router.get("/invites/{token}")
def open_invite(token: str, service: ServiceDep) -> InviteDetails:
    try:
        info = service.open_invite(token=token)
    except InvalidInviteError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Link non valido o scaduto") from ex
    return InviteDetails(
        first_name=info.player.first_name,
        last_name=info.player.last_name,
        has_account=info.account is not None,
        email=info.account.email if info.account is not None else None,
    )


@router.post("/invites/{token}/accept")
def accept_invite(
    token: str, body: AcceptInviteRequest, response: Response, service: ServiceDep, settings: SettingsDep
) -> CurrentUser:
    try:
        account, session_token = service.complete_invite(token=token, password=body.password, email=body.email)
    except InvalidInviteError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Link non valido o scaduto") from ex
    except EmailInUseError as ex:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email già in uso") from ex
    except (EmailRequiredError, InvalidPasswordError) as ex:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(ex)) from ex
    set_session_cookie(response, session_token, settings)
    return CurrentUser.from_account(account)
