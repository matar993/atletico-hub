from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.orm import Session as DbSession
from sqlalchemy.orm import contains_eager

from atletico_hub.auth.models import Account, Invite, Role
from atletico_hub.players.models import Player


class UserRepository:
    def __init__(self, session: DbSession) -> None:
        self._session = session

    def list_accounts(self) -> Sequence[Account]:
        statement = (
            select(Account)
            .join(Account.player)
            .options(contains_eager(Account.player))
            .order_by(Player.last_name, Player.first_name)
        )
        return self._session.scalars(statement).all()

    def account_by_id(self, account_id: int) -> Account | None:
        # populate_existing: after waiting for a lock, the role in the session may be older than the row.
        return self._session.scalar(
            select(Account).where(Account.id == account_id).execution_options(populate_existing=True)
        )

    def lock_admins(self) -> Sequence[int]:
        # Lock in id order: two demotions at once then take the locks in the same order and cannot deadlock.
        return self._session.scalars(
            select(Account.id).where(Account.role == Role.ADMIN).order_by(Account.id).with_for_update()
        ).all()

    def delete_open_invites_of_player(self, player_id: int) -> None:
        self._session.execute(delete(Invite).where(Invite.player_id == player_id, Invite.used_at.is_(None)))
