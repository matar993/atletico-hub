from collections.abc import Sequence

import pytest

from atletico_hub.players.models import Player
from atletico_hub.players.service import InvalidPlayerNameError, PlayerService


class FakePlayerStore:
    def __init__(self, rows: Sequence[tuple[Player, str | None]] = ()) -> None:
        self.added: list[Player] = []
        self._rows = rows

    def add(self, player: Player) -> Player:
        self.added.append(player)
        return player

    def list_with_email(self) -> Sequence[tuple[Player, str | None]]:
        return self._rows


class FakeTransaction:
    def __init__(self) -> None:
        self.commits = 0

    def commit(self) -> None:
        self.commits += 1


class TestPlayerService:
    def test_add_player_trims_the_names_and_commits(self) -> None:
        store = FakePlayerStore()
        transaction = FakeTransaction()

        player = PlayerService(players=store, transaction=transaction).add_player(
            first_name="  Luca ", last_name=" Bianchi  "
        )

        assert (player.first_name, player.last_name) == ("Luca", "Bianchi")
        assert store.added == [player]
        assert transaction.commits == 1

    @pytest.mark.parametrize(("first_name", "last_name"), [("   ", "Bianchi"), ("Luca", ""), ("L" * 51, "Bianchi")])
    def test_add_player_refuses_a_name_outside_1_to_50_characters(self, first_name: str, last_name: str) -> None:
        store = FakePlayerStore()
        transaction = FakeTransaction()

        with pytest.raises(InvalidPlayerNameError):
            PlayerService(players=store, transaction=transaction).add_player(first_name=first_name, last_name=last_name)

        assert store.added == []
        assert transaction.commits == 0

    def test_add_player_accepts_names_of_50_characters(self) -> None:
        player = PlayerService(players=FakePlayerStore(), transaction=FakeTransaction()).add_player(
            first_name="L" * 50, last_name="B"
        )

        assert len(player.first_name) == 50

    def test_list_squad_gives_emails_only_when_asked(self) -> None:
        rows = [
            (Player(first_name="Luca", last_name="Bianchi"), None),
            (Player(first_name="Anna", last_name="Rossi"), "anna@example.com"),
        ]
        service = PlayerService(players=FakePlayerStore(rows), transaction=FakeTransaction())

        with_emails = service.list_squad(with_emails=True)
        without_emails = service.list_squad(with_emails=False)

        assert [(entry.has_account, entry.email) for entry in with_emails] == [
            (False, None),
            (True, "anna@example.com"),
        ]
        assert [(entry.has_account, entry.email) for entry in without_emails] == [(False, None), (True, None)]
