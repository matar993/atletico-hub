from collections.abc import Sequence

import pytest

from atletico_hub.auth.models import Account, Role
from atletico_hub.players.models import Player
from atletico_hub.users.service import AccountNotFoundError, LastAdminError, UserService


def account(account_id: int, first_name: str, last_name: str, role: Role) -> Account:
    return Account(
        id=account_id,
        player_id=account_id + 100,
        player=Player(id=account_id + 100, first_name=first_name, last_name=last_name),
        email=f"{first_name}@example.com".lower(),
        password_hash="x",
        role=role,
    )


class FakeUserStore:
    def __init__(self, accounts: Sequence[Account]) -> None:
        self._accounts = accounts
        self.cancelled_for: list[int] = []
        self.locks = 0

    def list_accounts(self) -> Sequence[Account]:
        return self._accounts

    def account_by_id(self, account_id: int) -> Account | None:
        return next((a for a in self._accounts if a.id == account_id), None)

    def lock_admins(self) -> Sequence[int]:
        self.locks += 1
        return [a.id for a in self._accounts if a.role == Role.ADMIN]

    def delete_open_invites_of_player(self, player_id: int) -> None:
        self.cancelled_for.append(player_id)


class FakeTransaction:
    def __init__(self) -> None:
        self.commits = 0

    def commit(self) -> None:
        self.commits += 1


ANNA = account(1, "Anna", "Rossi", Role.ADMIN)
BORIS = account(2, "Boris", "Verdi", Role.ADMIN)
LUCA = account(3, "Luca", "Bianchi", Role.PLAYER)


def service_for(*accounts: Account) -> tuple[UserService, FakeUserStore, FakeTransaction]:
    store = FakeUserStore(accounts)
    transaction = FakeTransaction()
    return UserService(users=store, transaction=transaction), store, transaction


class TestListAccounts:
    def test_an_admin_gets_every_account_with_the_change_role_flag_on(self) -> None:
        service, _, _ = service_for(ANNA, LUCA)

        entries = service.list_accounts(account(9, "Actor", "Admin", Role.ADMIN))

        assert [(e.account.email, e.change_role) for e in entries] == [
            ("anna@example.com", True),
            ("luca@example.com", True),
        ]

    def test_a_player_gets_the_flag_off(self) -> None:
        service, _, _ = service_for(ANNA)

        entries = service.list_accounts(account(9, "Actor", "Player", Role.PLAYER))

        assert [e.change_role for e in entries] == [False]


class TestChangeRole:
    def test_promotion_sets_the_role_cancels_the_open_invites_and_commits(self) -> None:
        luca = account(3, "Luca", "Bianchi", Role.PLAYER)
        service, store, transaction = service_for(ANNA, luca)

        result = service.change_role(luca.id, Role.ADMIN)

        assert result.role == Role.ADMIN
        assert store.cancelled_for == [luca.player_id]
        assert transaction.commits == 1

    def test_an_admin_demotes_themselves_when_another_admin_is_left(self) -> None:
        anna = account(1, "Anna", "Rossi", Role.ADMIN)
        service, store, transaction = service_for(anna, BORIS)

        result = service.change_role(anna.id, Role.PLAYER)

        assert result.role == Role.PLAYER
        assert store.cancelled_for == []
        assert transaction.commits == 1

    def test_the_last_admin_cannot_be_demoted_and_nothing_changes(self) -> None:
        anna = account(1, "Anna", "Rossi", Role.ADMIN)
        service, _, transaction = service_for(anna, LUCA)

        with pytest.raises(LastAdminError):
            service.change_role(anna.id, Role.PLAYER)

        assert anna.role == Role.ADMIN
        assert transaction.commits == 0

    def test_a_demotion_locks_the_admins_and_a_promotion_does_not(self) -> None:
        luca = account(3, "Luca", "Bianchi", Role.PLAYER)
        service, store, _ = service_for(ANNA, BORIS, luca)

        service.change_role(luca.id, Role.ADMIN)
        assert store.locks == 0
        service.change_role(BORIS.id, Role.PLAYER)
        assert store.locks == 1

    def test_an_unknown_account_is_refused(self) -> None:
        service, _, transaction = service_for(ANNA)

        with pytest.raises(AccountNotFoundError):
            service.change_role(99, Role.ADMIN)

        assert transaction.commits == 0

    def test_the_same_role_changes_nothing_and_keeps_the_open_invites(self) -> None:
        anna = account(1, "Anna", "Rossi", Role.ADMIN)
        service, store, transaction = service_for(anna, BORIS)

        service.change_role(anna.id, Role.ADMIN)

        assert store.cancelled_for == []
        assert transaction.commits == 0

    def test_demoting_a_player_when_one_admin_is_left_is_a_no_op_and_not_an_error(self) -> None:
        luca = account(3, "Luca", "Bianchi", Role.PLAYER)
        service, _, transaction = service_for(account(1, "Anna", "Rossi", Role.ADMIN), luca)

        result = service.change_role(luca.id, Role.PLAYER)

        assert result.role == Role.PLAYER
        assert transaction.commits == 0
