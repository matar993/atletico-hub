import pytest

from atletico_hub.auth.models import Account, Role
from atletico_hub.auth.permissions import ROLE_PERMISSIONS, Permission, can

PLAYER_PERMISSIONS = {Permission.SQUAD_VIEW, Permission.PROFILE_UPDATE}


def account_with(role: Role) -> Account:
    return Account(email="a@example.com", password_hash="x", role=role)


class TestRolePermissions:
    def test_admin_gets_every_permission(self) -> None:
        assert ROLE_PERMISSIONS[Role.ADMIN] == {
            Permission.SQUAD_VIEW,
            Permission.SQUAD_VIEW_EMAIL,
            Permission.SQUAD_CREATE,
            Permission.PLAYERS_UPDATE,
            Permission.PROFILE_UPDATE,
            Permission.INVITES_CREATE,
            Permission.USERS_VIEW,
            Permission.USERS_CHANGE_ROLE,
        }

    def test_player_gets_only_squad_view_and_profile_update(self) -> None:
        assert ROLE_PERMISSIONS[Role.PLAYER] == PLAYER_PERMISSIONS

    def test_every_role_has_a_set(self) -> None:
        assert set(ROLE_PERMISSIONS) == set(Role)


class TestCan:
    @pytest.mark.parametrize("permission", list(Permission))
    def test_admin_can_do_everything(self, permission: Permission) -> None:
        assert can(account_with(Role.ADMIN), permission)

    @pytest.mark.parametrize("permission", list(Permission))
    def test_player_can_do_only_its_set(self, permission: Permission) -> None:
        assert can(account_with(Role.PLAYER), permission) == (permission in PLAYER_PERMISSIONS)
