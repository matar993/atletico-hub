from datetime import datetime
from typing import Self

from pydantic import BaseModel, EmailStr, Field

from atletico_hub.auth.models import Account, Role


class LoginRequest(BaseModel):
    email: str
    password: str


class CurrentUser(BaseModel):
    first_name: str
    last_name: str
    email: str
    role: Role

    @classmethod
    def from_account(cls, account: Account) -> Self:
        return cls(
            first_name=account.player.first_name,
            last_name=account.player.last_name,
            email=account.email,
            role=account.role,
        )


class CreateInviteRequest(BaseModel):
    player_id: int


class InviteCreated(BaseModel):
    path: str
    expires_at: datetime


class InviteDetails(BaseModel):
    first_name: str
    last_name: str
    has_account: bool
    email: str | None


class AcceptInviteRequest(BaseModel):
    email: EmailStr | None = None
    password: str = Field(min_length=8, max_length=128)
