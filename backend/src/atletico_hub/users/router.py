from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from atletico_hub.auth.dependencies import require
from atletico_hub.auth.models import Account
from atletico_hub.auth.permissions import Permission
from atletico_hub.db.session import get_session
from atletico_hub.users.repository import UserRepository
from atletico_hub.users.schemas import AccountPermissions, AccountRole, Accounts, AccountSummary, ChangeRoleRequest
from atletico_hub.users.service import AccountEntry, AccountNotFoundError, LastAdminError, UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(session: Annotated[Session, Depends(get_session)]) -> UserService:
    return UserService(users=UserRepository(session), transaction=session)


ServiceDep = Annotated[UserService, Depends(get_user_service)]


def to_summary(entry: AccountEntry) -> AccountSummary:
    return AccountSummary(
        id=entry.account.id,
        first_name=entry.account.player.first_name,
        last_name=entry.account.player.last_name,
        email=entry.account.email,
        role=entry.account.role,
        permissions=AccountPermissions(change_role=entry.change_role),
    )


@router.get("")
def list_users(account: Annotated[Account, Depends(require(Permission.USERS_VIEW))], service: ServiceDep) -> Accounts:
    return Accounts(items=[to_summary(entry) for entry in service.list_accounts(account)])


@router.put("/{account_id}/role", dependencies=[Depends(require(Permission.USERS_CHANGE_ROLE))])
def change_role(account_id: int, body: ChangeRoleRequest, service: ServiceDep) -> AccountRole:
    try:
        account = service.change_role(account_id, body.role)
    except AccountNotFoundError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex)) from ex
    except LastAdminError as ex:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Serve almeno un admin") from ex
    return AccountRole(id=account.id, role=account.role)
