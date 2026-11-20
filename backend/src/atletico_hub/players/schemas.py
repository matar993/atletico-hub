from pydantic import BaseModel

from atletico_hub.schemas import RequestModel


class AddPlayerRequest(RequestModel):
    first_name: str
    last_name: str


class RenamePlayerRequest(RequestModel):
    first_name: str
    last_name: str


class PlayerPermissions(BaseModel):
    update: bool
    create_invite: bool


class SquadPermissions(BaseModel):
    create: bool


class SquadMember(BaseModel):
    id: int
    first_name: str
    last_name: str
    has_account: bool
    email: str | None
    permissions: PlayerPermissions


class Squad(BaseModel):
    permissions: SquadPermissions
    items: list[SquadMember]


class PlayerName(BaseModel):
    id: int
    first_name: str
    last_name: str
