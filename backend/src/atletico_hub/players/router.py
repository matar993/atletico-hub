from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from atletico_hub.auth.dependencies import require
from atletico_hub.auth.models import Account
from atletico_hub.auth.permissions import Permission
from atletico_hub.db.session import get_session
from atletico_hub.players.repository import PlayerRepository
from atletico_hub.players.schemas import (
    AddPlayerRequest,
    PlayerName,
    PlayerPermissions,
    RenamePlayerRequest,
    Squad,
    SquadMember,
    SquadPermissions,
)
from atletico_hub.players.service import InvalidPlayerNameError, PlayerNotFoundError, PlayerService, SquadEntry

router = APIRouter(prefix="/players", tags=["players"])


def get_player_service(session: Annotated[Session, Depends(get_session)]) -> PlayerService:
    return PlayerService(players=PlayerRepository(session), transaction=session)


ServiceDep = Annotated[PlayerService, Depends(get_player_service)]


def to_member(entry: SquadEntry) -> SquadMember:
    return SquadMember(
        id=entry.player.id,
        first_name=entry.player.first_name,
        last_name=entry.player.last_name,
        has_account=entry.has_account,
        email=entry.email,
        permissions=PlayerPermissions(update=entry.update, create_invite=entry.create_invite),
    )


@router.get("")
def list_players(account: Annotated[Account, Depends(require(Permission.SQUAD_VIEW))], service: ServiceDep) -> Squad:
    squad = service.list_squad(account)
    return Squad(permissions=SquadPermissions(create=squad.create), items=[to_member(e) for e in squad.entries])


@router.post("", status_code=status.HTTP_201_CREATED)
def add_player(
    body: AddPlayerRequest,
    account: Annotated[Account, Depends(require(Permission.SQUAD_CREATE))],
    service: ServiceDep,
) -> SquadMember:
    try:
        player = service.add_player(first_name=body.first_name, last_name=body.last_name)
    except InvalidPlayerNameError as ex:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(ex)) from ex
    return to_member(service.describe_new(account, player))


@router.patch("/{player_id}", dependencies=[Depends(require(Permission.PLAYERS_UPDATE))])
def rename_player(player_id: int, body: RenamePlayerRequest, service: ServiceDep) -> PlayerName:
    try:
        player = service.rename(player_id, first_name=body.first_name, last_name=body.last_name)
    except PlayerNotFoundError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Giocatore non trovato") from ex
    except InvalidPlayerNameError as ex:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(ex)) from ex
    return PlayerName(id=player.id, first_name=player.first_name, last_name=player.last_name)
