from pydantic import BaseModel

from atletico_hub.schemas import RequestModel


class AddPlayerRequest(RequestModel):
    first_name: str
    last_name: str


class SquadMember(BaseModel):
    id: int
    first_name: str
    last_name: str
    has_account: bool
    email: str | None
