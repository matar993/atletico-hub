from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from atletico_hub.auth.dependencies import current_account, require_admin
from atletico_hub.auth.models import Account, Role
from atletico_hub.db.session import get_session
from atletico_hub.players.repository import PlayerRepository
from atletico_hub.players.schemas import AddPlayerRequest, SquadMember
from atletico_hub.players.service import InvalidPlayerNameError, PlayerService

router = APIRouter(prefix="/players", tags=["players"])


def get_player_service(session: Annotated[Session, Depends(get_session)]) -> PlayerService:
    return PlayerService(players=PlayerRepository(session), transaction=session)


ServiceDep = Annotated[PlayerService, Depends(get_player_service)]


@router.get("")
def list_players(account: Annotated[Account, Depends(current_account)], service: ServiceDep) -> list[SquadMember]:
    entries = service.list_squad(with_emails=account.role == Role.ADMIN)
    return [
        SquadMember(
            id=entry.player.id,
            first_name=entry.player.first_name,
            last_name=entry.player.last_name,
            has_account=entry.has_account,
            email=entry.email,
        )
        for entry in entries
    ]


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def add_player(body: AddPlayerRequest, service: ServiceDep) -> SquadMember:
    try:
        player = service.add_player(first_name=body.first_name, last_name=body.last_name)
    except InvalidPlayerNameError as ex:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(ex)) from ex
    return SquadMember(
        id=player.id, first_name=player.first_name, last_name=player.last_name, has_account=False, email=None
    )
