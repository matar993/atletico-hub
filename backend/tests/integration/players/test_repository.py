from sqlalchemy.orm import Session

from atletico_hub.auth.models import Account, Role
from atletico_hub.players.models import Player
from atletico_hub.players.repository import PlayerRepository


class TestPlayerRepository:
    def test_add_assigns_an_id(self, db_session: Session) -> None:
        player = PlayerRepository(db_session).add(player=Player(first_name="Luca", last_name="Bianchi"))

        assert player.id is not None

    def test_get_returns_the_player(self, db_session: Session) -> None:
        repository = PlayerRepository(db_session)
        added = repository.add(player=Player(first_name="Luca", last_name="Bianchi"))

        assert repository.get(player_id=added.id) == added

    def test_get_returns_none_for_an_unknown_id(self, db_session: Session) -> None:
        assert PlayerRepository(db_session).get(player_id=0) is None

    def test_list_with_account_sorts_by_last_name_then_first_name(self, db_session: Session) -> None:
        repository = PlayerRepository(db_session)
        for first_name, last_name in [("Marco", "Rossi"), ("Luca", "Bianchi"), ("Anna", "Rossi")]:
            repository.add(player=Player(first_name=first_name, last_name=last_name))

        names = [(player.first_name, player.last_name) for player, _ in repository.list_with_account()]

        assert names == [("Luca", "Bianchi"), ("Anna", "Rossi"), ("Marco", "Rossi")]

    def test_list_with_account_gives_the_account_or_none(self, db_session: Session) -> None:
        repository = PlayerRepository(db_session)
        with_account = repository.add(player=Player(first_name="Anna", last_name="Rossi"))
        repository.add(player=Player(first_name="Luca", last_name="Bianchi"))
        db_session.add(
            Account(player_id=with_account.id, email="anna@example.com", password_hash="hash", role=Role.PLAYER)
        )
        db_session.flush()

        emails = {
            player.first_name: account.email if account else None for player, account in repository.list_with_account()
        }

        assert emails == {"Anna": "anna@example.com", "Luca": None}
