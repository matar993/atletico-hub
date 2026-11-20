from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from atletico_hub.auth.models import Account
from atletico_hub.players.models import Player


class PlayerRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, player: Player) -> Player:
        self._session.add(player)
        self._session.flush()
        return player

    def get(self, player_id: int) -> Player | None:
        return self._session.get(Player, player_id)

    def list_with_account(self) -> Sequence[tuple[Player, Account | None]]:
        statement = (
            select(Player, Account)
            .outerjoin(Account, Account.player_id == Player.id)
            .order_by(Player.last_name, Player.first_name)
        )
        return [(player, account) for player, account in self._session.execute(statement)]
