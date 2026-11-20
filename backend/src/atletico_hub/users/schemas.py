from pydantic import BaseModel

from atletico_hub.auth.models import Role
from atletico_hub.schemas import RequestModel


class ChangeRoleRequest(RequestModel):
    role: Role


class AccountPermissions(BaseModel):
    change_role: bool


class AccountSummary(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    role: Role
    permissions: AccountPermissions


class Accounts(BaseModel):
    items: list[AccountSummary]


class AccountRole(BaseModel):
    id: int
    role: Role
