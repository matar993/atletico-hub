from collections.abc import Sequence

import pytest

from atletico_hub.auth.models import Account, Role
from atletico_hub.players.models import Player
from atletico_hub.players.service import InvalidPlayerNameError, PlayerNotFoundError, PlayerService


def actor_with(role: Role) -> Account:
    return Account(email="actor@example.com", password_hash="x", role=role)


ROWS = [
    (Player(first_name="Luca", last_name="Bianchi"), None),
    (
        Player(first_name="Anna", last_name="Rossi"),
        Account(email="anna@example.com", password_hash="x", role=Role.PLAYER),
    ),
    (
        Player(first_name="Boss", last_name="Verdi"),
        Account(email="boss@example.com", password_hash="x", role=Role.ADMIN),
    ),
]


class FakePlayerStore:
    def __init__(self, rows: Sequence[tuple[Player, Account | None]] = ()) -> None:
        self.added: list[Player] = []
        self._rows = rows

    def add(self, player: Player) -> Player:
        self.added.append(player)
        return player

    def get(self, player_id: int) -> Player | None:
        return next((player for player, _ in self._rows if player.id == player_id), None)

    def list_with_account(self) -> Sequence[tuple[Player, Account | None]]:
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

    def test_list_squad_gives_a_player_no_email_and_no_action(self) -> None:
        service = PlayerService(players=FakePlayerStore(ROWS), transaction=FakeTransaction())

        squad = service.list_squad(actor_with(Role.PLAYER))

        assert squad.create is False
        assert [(e.has_account, e.email, e.update, e.create_invite) for e in squad.entries] == [
            (False, None, False, False),
            (True, None, False, False),
            (True, None, False, False),
        ]

    def test_list_squad_gives_an_admin_emails_and_actions_but_no_invite_on_an_admin_account(self) -> None:
        service = PlayerService(players=FakePlayerStore(ROWS), transaction=FakeTransaction())

        squad = service.list_squad(actor_with(Role.ADMIN))

        assert squad.create is True
        assert [(e.has_account, e.email, e.update, e.create_invite) for e in squad.entries] == [
            (False, None, True, True),
            (True, "anna@example.com", True, True),
            (True, "boss@example.com", True, False),
        ]


def luca_in_a_store() -> tuple[Player, FakePlayerStore]:
    luca = Player(id=7, first_name="Luca", last_name="Bianchi")
    return luca, FakePlayerStore([(luca, None)])


class TestRename:
    def test_rename_trims_the_names_and_commits(self) -> None:
        _, store = luca_in_a_store()
        transaction = FakeTransaction()

        player = PlayerService(players=store, transaction=transaction).rename(
            7, first_name=" Luca ", last_name=" Bianchi Rossi "
        )

        assert (player.first_name, player.last_name) == ("Luca", "Bianchi Rossi")
        assert transaction.commits == 1

    def test_rename_refuses_an_unknown_player(self) -> None:
        _, store = luca_in_a_store()
        transaction = FakeTransaction()

        with pytest.raises(PlayerNotFoundError):
            PlayerService(players=store, transaction=transaction).rename(8, first_name="Luca", last_name="Bianchi")

        assert transaction.commits == 0

    @pytest.mark.parametrize(("first_name", "last_name"), [(" ", "Bianchi"), ("Gigi", ""), ("L" * 51, "Bianchi")])
    def test_rename_refuses_an_invalid_name_and_changes_nothing(self, first_name: str, last_name: str) -> None:
        luca, store = luca_in_a_store()
        transaction = FakeTransaction()

        with pytest.raises(InvalidPlayerNameError):
            PlayerService(players=store, transaction=transaction).rename(7, first_name=first_name, last_name=last_name)

        assert transaction.commits == 0
        assert (luca.first_name, luca.last_name) == ("Luca", "Bianchi")
