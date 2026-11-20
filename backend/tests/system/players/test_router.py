from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from atletico_hub.auth.models import Account, Role
from atletico_hub.auth.passwords import Argon2PasswordHasher
from atletico_hub.players.models import Player

WRITE_HEADER = {"X-Requested-With": "atletico-hub"}
PASSWORD = "secret-pass"


class TestPlayerRouter:
    def test_list_players_answers_401_without_a_session(self, client: TestClient) -> None:
        assert client.get("/players").status_code == 401

    def test_list_players_shows_a_player_the_squad_without_emails(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        db_session.add_all(
            [
                Account(
                    player=Player(first_name="Marco", last_name="Rossi"),
                    email="marco@example.com",
                    password_hash=Argon2PasswordHasher().hash(PASSWORD),
                    role=Role.PLAYER,
                    failed_logins=0,
                ),
                Player(first_name="Luca", last_name="Bianchi"),
            ]
        )
        db_session.flush()
        client.post("/auth/login", json={"email": "marco@example.com", "password": PASSWORD}, headers=WRITE_HEADER)

        response = client.get("/players")

        assert response.status_code == 200
        assert [(p["first_name"], p["last_name"], p["has_account"], p["email"]) for p in response.json()] == [
            ("Luca", "Bianchi", False, None),
            ("Marco", "Rossi", True, None),
        ]

    def test_list_players_shows_an_admin_the_emails(self, client: TestClient, db_session: DbSession) -> None:
        db_session.add_all(
            [
                Account(
                    player=Player(first_name="Anna", last_name="Rossi"),
                    email="anna@example.com",
                    password_hash=Argon2PasswordHasher().hash(PASSWORD),
                    role=Role.ADMIN,
                    failed_logins=0,
                ),
                Player(first_name="Luca", last_name="Bianchi"),
            ]
        )
        db_session.flush()
        client.post("/auth/login", json={"email": "anna@example.com", "password": PASSWORD}, headers=WRITE_HEADER)

        response = client.get("/players")

        assert [(p["first_name"], p["has_account"], p["email"]) for p in response.json()] == [
            ("Luca", False, None),
            ("Anna", True, "anna@example.com"),
        ]

    def test_add_player_lets_an_admin_add_a_player_who_then_shows_in_the_squad(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        db_session.add(
            Account(
                player=Player(first_name="Anna", last_name="Rossi"),
                email="anna@example.com",
                password_hash=Argon2PasswordHasher().hash(PASSWORD),
                role=Role.ADMIN,
                failed_logins=0,
            )
        )
        db_session.flush()
        client.post("/auth/login", json={"email": "anna@example.com", "password": PASSWORD}, headers=WRITE_HEADER)

        response = client.post("/players", json={"first_name": " Luca ", "last_name": "Bianchi"}, headers=WRITE_HEADER)

        assert response.status_code == 201
        assert response.json()["first_name"] == "Luca"
        assert response.json()["has_account"] is False
        names = [p["first_name"] for p in client.get("/players").json()]
        assert names == ["Luca", "Anna"]

    def test_add_player_answers_403_to_a_player_and_adds_nothing(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        db_session.add(
            Account(
                player=Player(first_name="Marco", last_name="Rossi"),
                email="marco@example.com",
                password_hash=Argon2PasswordHasher().hash(PASSWORD),
                role=Role.PLAYER,
                failed_logins=0,
            )
        )
        db_session.flush()
        client.post("/auth/login", json={"email": "marco@example.com", "password": PASSWORD}, headers=WRITE_HEADER)

        response = client.post("/players", json={"first_name": "Luca", "last_name": "Bianchi"}, headers=WRITE_HEADER)

        assert response.status_code == 403
        assert db_session.scalar(select(func.count()).select_from(Player)) == 1

    def test_add_player_answers_401_without_a_session(self, client: TestClient) -> None:
        response = client.post("/players", json={"first_name": "Luca", "last_name": "Bianchi"}, headers=WRITE_HEADER)

        assert response.status_code == 401

    def test_add_player_answers_422_to_a_blank_name_and_adds_nothing(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        db_session.add(
            Account(
                player=Player(first_name="Anna", last_name="Rossi"),
                email="anna@example.com",
                password_hash=Argon2PasswordHasher().hash(PASSWORD),
                role=Role.ADMIN,
                failed_logins=0,
            )
        )
        db_session.flush()
        client.post("/auth/login", json={"email": "anna@example.com", "password": PASSWORD}, headers=WRITE_HEADER)

        response = client.post("/players", json={"first_name": "   ", "last_name": "Bianchi"}, headers=WRITE_HEADER)

        assert response.status_code == 422
        assert db_session.scalar(select(func.count()).select_from(Player)) == 1


class TestPlayerRouterErrorOrder:
    def test_add_player_answers_403_to_a_player_who_sends_an_invalid_body(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        db_session.add(
            Account(
                player=Player(first_name="Marco", last_name="Rossi"),
                email="marco@example.com",
                password_hash=Argon2PasswordHasher().hash(PASSWORD),
                role=Role.PLAYER,
                failed_logins=0,
            )
        )
        db_session.flush()
        client.post("/auth/login", json={"email": "marco@example.com", "password": PASSWORD}, headers=WRITE_HEADER)

        response = client.post("/players", json={"first_name": "Luca"}, headers=WRITE_HEADER)

        assert response.status_code == 403
