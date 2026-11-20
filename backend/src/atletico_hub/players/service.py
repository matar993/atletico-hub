from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from atletico_hub.players.models import Player

NAME_MAX_LENGTH = 50


class InvalidPlayerNameError(Exception):
    pass


class PlayerStore(Protocol):
    def add(self, player: Player) -> Player: ...

    def list_with_email(self) -> Sequence[tuple[Player, str | None]]: ...


class Transaction(Protocol):
    def commit(self) -> None: ...


@dataclass(frozen=True)
class SquadEntry:
    player: Player
    has_account: bool
    email: str | None


class PlayerService:
    def __init__(self, players: PlayerStore, transaction: Transaction) -> None:
        self._players = players
        self._transaction = transaction

    def add_player(self, first_name: str, last_name: str) -> Player:
        player = Player(first_name=self._clean_name(first_name), last_name=self._clean_name(last_name))
        self._players.add(player)
        self._transaction.commit()
        return player

    def list_squad(self, with_emails: bool) -> list[SquadEntry]:
        return [
            SquadEntry(player=player, has_account=email is not None, email=email if with_emails else None)
            for player, email in self._players.list_with_email()
        ]

    @staticmethod
    def _clean_name(name: str) -> str:
        cleaned = name.strip()
        if not 1 <= len(cleaned) <= NAME_MAX_LENGTH:
            raise InvalidPlayerNameError(f"A name needs 1 to {NAME_MAX_LENGTH} characters, got {len(cleaned)}")
        return cleaned
