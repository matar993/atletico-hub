from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from atletico_hub.auth.models import Account, Role
from atletico_hub.auth.permissions import Permission, can


class AccountNotFoundError(Exception):
    pass


class LastAdminError(Exception):
    pass


class UserStore(Protocol):
    def list_accounts(self) -> Sequence[Account]: ...

    def account_by_id(self, account_id: int) -> Account | None: ...

    def lock_admins(self) -> Sequence[int]: ...

    def delete_open_invites_of_player(self, player_id: int) -> None: ...


class Transaction(Protocol):
    def commit(self) -> None: ...


@dataclass(frozen=True)
class AccountEntry:
    account: Account
    change_role: bool


class UserService:
    def __init__(self, users: UserStore, transaction: Transaction) -> None:
        self._users = users
        self._transaction = transaction

    def list_accounts(self, actor: Account) -> list[AccountEntry]:
        change_role = can(actor, Permission.USERS_CHANGE_ROLE)
        return [AccountEntry(account, change_role) for account in self._users.list_accounts()]

    def change_role(self, account_id: int, role: Role) -> Account:
        # Lock every admin row before reading the account: two demotions at once then run one after the other,
        # and the second one counts the admins left by the first.
        admins = self._users.lock_admins() if role == Role.PLAYER else ()
        account = self._users.account_by_id(account_id)
        if account is None:
            raise AccountNotFoundError(f"No account with id {account_id}")
        if account.role == role:
            return account
        if role == Role.PLAYER and len(admins) <= 1:
            raise LastAdminError("The app needs at least one admin")
        if role == Role.ADMIN:
            self._users.delete_open_invites_of_player(account.player_id)
        account.role = role
        self._transaction.commit()
        return account
