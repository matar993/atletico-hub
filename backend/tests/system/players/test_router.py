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
        assert [(p["first_name"], p["last_name"], p["has_account"], p["email"]) for p in response.json()["items"]] == [
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

        assert [(p["first_name"], p["has_account"], p["email"]) for p in response.json()["items"]] == [
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
        names = [p["first_name"] for p in client.get("/players").json()["items"]]
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


def sign_in(client: TestClient, db_session: DbSession, role: Role) -> Account:
    account = Account(
        player=Player(first_name=role.value.capitalize(), last_name="Tester"),
        email=f"{role.value}@example.com",
        password_hash=Argon2PasswordHasher().hash(PASSWORD),
        role=role,
        failed_logins=0,
    )
    db_session.add(account)
    db_session.flush()
    client.post("/auth/login", json={"email": account.email, "password": PASSWORD}, headers=WRITE_HEADER)
    return account


class TestSquadPermissions:
    def test_a_player_gets_every_flag_false_and_the_api_refuses_each_action(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        sign_in(client, db_session, Role.PLAYER)
        luca = Player(first_name="Luca", last_name="Bianchi")
        db_session.add(luca)
        db_session.flush()

        body = client.get("/players").json()

        assert body["permissions"] == {"create": False}
        assert all(item["permissions"] == {"update": False, "create_invite": False} for item in body["items"])
        assert (
            client.post("/players", json={"first_name": "A", "last_name": "B"}, headers=WRITE_HEADER).status_code == 403
        )
        rename = client.patch(f"/players/{luca.id}", json={"first_name": "A", "last_name": "B"}, headers=WRITE_HEADER)
        assert rename.status_code == 403
        assert client.post("/auth/invites", json={"player_id": luca.id}, headers=WRITE_HEADER).status_code == 403

    def test_an_admin_gets_the_flags_and_no_invite_on_an_admin_account(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        sign_in(client, db_session, Role.ADMIN)
        db_session.add(Player(first_name="Luca", last_name="Bianchi"))
        db_session.flush()

        body = client.get("/players").json()

        assert body["permissions"] == {"create": True}
        assert {i["first_name"]: i["permissions"] for i in body["items"]} == {
            "Luca": {"update": True, "create_invite": True},
            "Admin": {"update": True, "create_invite": False},
        }


class TestRenamePlayer:
    def test_an_admin_changes_the_name_of_a_player_and_the_squad_shows_it(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        sign_in(client, db_session, Role.ADMIN)
        luca = Player(first_name="Luca", last_name="Bianchi")
        db_session.add(luca)
        db_session.flush()

        response = client.patch(
            f"/players/{luca.id}", json={"first_name": " Luca ", "last_name": "Bianchi Rossi"}, headers=WRITE_HEADER
        )

        assert response.status_code == 200
        assert response.json() == {"id": luca.id, "first_name": "Luca", "last_name": "Bianchi Rossi"}
        names = [(p["first_name"], p["last_name"]) for p in client.get("/players").json()["items"]]
        assert ("Luca", "Bianchi Rossi") in names

    def test_a_player_cannot_rename_even_themselves_and_nothing_changes(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        account = sign_in(client, db_session, Role.PLAYER)

        response = client.patch(
            f"/players/{account.player_id}", json={"first_name": "A", "last_name": "B"}, headers=WRITE_HEADER
        )

        assert response.status_code == 403
        assert account.player.last_name == "Tester"

    def test_an_empty_name_answers_422_and_changes_nothing(self, client: TestClient, db_session: DbSession) -> None:
        sign_in(client, db_session, Role.ADMIN)
        luca = Player(first_name="Luca", last_name="Bianchi")
        db_session.add(luca)
        db_session.flush()

        response = client.patch(
            f"/players/{luca.id}", json={"first_name": "   ", "last_name": "Bianchi"}, headers=WRITE_HEADER
        )

        assert response.status_code == 422
        assert luca.first_name == "Luca"

    def test_an_unknown_player_answers_404(self, client: TestClient, db_session: DbSession) -> None:
        sign_in(client, db_session, Role.ADMIN)

        response = client.patch("/players/0", json={"first_name": "A", "last_name": "B"}, headers=WRITE_HEADER)

        assert response.status_code == 404
