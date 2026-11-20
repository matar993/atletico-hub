from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from atletico_hub.auth.dependencies import require
from atletico_hub.auth.models import Account
from atletico_hub.auth.permissions import Permission
from atletico_hub.auth.schemas import CurrentUser
from atletico_hub.players.router import ServiceDep
from atletico_hub.players.schemas import UpdateProfileRequest
from atletico_hub.players.service import InvalidPlayerNameError

router = APIRouter(prefix="/profile", tags=["profile"])


@router.patch("")
def update_profile(
    body: UpdateProfileRequest,
    account: Annotated[Account, Depends(require(Permission.PROFILE_UPDATE))],
    service: ServiceDep,
) -> CurrentUser:
    try:
        service.rename(account.player_id, first_name=body.first_name, last_name=body.last_name)
    except InvalidPlayerNameError as ex:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(ex)) from ex
    return CurrentUser.from_account(account)
