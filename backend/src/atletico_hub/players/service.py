from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from atletico_hub.auth.models import Account, Role
from atletico_hub.auth.permissions import Permission, can
from atletico_hub.players.models import Player

NAME_MAX_LENGTH = 50


class InvalidPlayerNameError(Exception):
    pass


class PlayerNotFoundError(Exception):
    pass


class PlayerStore(Protocol):
    def add(self, player: Player) -> Player: ...

    def get(self, player_id: int) -> Player | None: ...

    def list_with_account(self) -> Sequence[tuple[Player, Account | None]]: ...


class Transaction(Protocol):
    def commit(self) -> None: ...


@dataclass(frozen=True)
class SquadEntry:
    player: Player
    has_account: bool
    email: str | None
    update: bool
    create_invite: bool


@dataclass(frozen=True)
class Squad:
    create: bool
    entries: list[SquadEntry]


class PlayerService:
    def __init__(self, players: PlayerStore, transaction: Transaction) -> None:
        self._players = players
        self._transaction = transaction

    def add_player(self, first_name: str, last_name: str) -> Player:
        player = Player(first_name=self._clean_name(first_name), last_name=self._clean_name(last_name))
        self._players.add(player)
        self._transaction.commit()
        return player

    def rename(self, player_id: int, first_name: str, last_name: str) -> Player:
        player = self._players.get(player_id)
        if player is None:
            raise PlayerNotFoundError(f"No player with id {player_id}")
        cleaned_first_name, cleaned_last_name = self._clean_name(first_name), self._clean_name(last_name)
        player.first_name, player.last_name = cleaned_first_name, cleaned_last_name
        self._transaction.commit()
        return player

    def list_squad(self, actor: Account) -> Squad:
        show_emails = can(actor, Permission.SQUAD_VIEW_EMAIL)
        may_update = can(actor, Permission.PLAYERS_UPDATE)
        may_invite = can(actor, Permission.INVITES_CREATE)
        entries = [
            SquadEntry(
                player=player,
                has_account=account is not None,
                email=account.email if account is not None and show_emails else None,
                update=may_update,
                create_invite=may_invite and (account is None or account.role != Role.ADMIN),
            )
            for player, account in self._players.list_with_account()
        ]
        return Squad(create=can(actor, Permission.SQUAD_CREATE), entries=entries)

    @staticmethod
    def _clean_name(name: str) -> str:
        cleaned = name.strip()
        if not 1 <= len(cleaned) <= NAME_MAX_LENGTH:
            raise InvalidPlayerNameError(f"A name needs 1 to {NAME_MAX_LENGTH} characters, got {len(cleaned)}")
        return cleaned
