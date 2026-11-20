from pydantic import BaseModel


class AddPlayerRequest(BaseModel):
    first_name: str
    last_name: str


class SquadMember(BaseModel):
    id: int
    first_name: str
    last_name: str
    has_account: bool
    email: str | None
