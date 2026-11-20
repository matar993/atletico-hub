import enum
from collections.abc import Mapping

from atletico_hub.auth.models import Account, Role


class Permission(enum.StrEnum):
    SQUAD_VIEW = "squad:view"
    SQUAD_VIEW_EMAIL = "squad:view_email"
    SQUAD_CREATE = "squad:create"
    PLAYERS_UPDATE = "players:update"
    PROFILE_UPDATE = "profile:update"
    INVITES_CREATE = "invites:create"
    USERS_VIEW = "users:view"
    USERS_CHANGE_ROLE = "users:change_role"


ROLE_PERMISSIONS: Mapping[Role, frozenset[Permission]] = {
    Role.ADMIN: frozenset(Permission),
    Role.PLAYER: frozenset({Permission.SQUAD_VIEW, Permission.PROFILE_UPDATE}),
}


def can(account: Account, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS[account.role]
