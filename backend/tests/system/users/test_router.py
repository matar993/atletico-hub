from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from atletico_hub.auth.models import Account, Invite, Role
from atletico_hub.auth.passwords import Argon2PasswordHasher
from atletico_hub.players.models import Player

WRITE_HEADER = {"X-Requested-With": "atletico-hub"}
PASSWORD = "secret-pass"


def add_account(db_session: DbSession, first_name: str, last_name: str, role: Role) -> Account:
    account = Account(
        player=Player(first_name=first_name, last_name=last_name),
        email=f"{first_name}@example.com".lower(),
        password_hash=Argon2PasswordHasher().hash(PASSWORD),
        role=role,
        failed_logins=0,
    )
    db_session.add(account)
    db_session.flush()
    return account


def sign_in(client: TestClient, account: Account) -> None:
    client.post("/auth/login", json={"email": account.email, "password": PASSWORD}, headers=WRITE_HEADER)


def put_role(client: TestClient, account_id: int, role: str) -> int:
    return client.put(f"/users/{account_id}/role", json={"role": role}, headers=WRITE_HEADER).status_code


class TestListUsers:
    def test_an_admin_sees_every_account_sorted_with_the_change_role_flag(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        anna = add_account(db_session, "Anna", "Rossi", Role.ADMIN)
        add_account(db_session, "Luca", "Bianchi", Role.PLAYER)
        db_session.add(Player(first_name="Senza", last_name="Account"))
        db_session.flush()
        sign_in(client, anna)

        response = client.get("/users")

        assert response.status_code == 200
        assert [
            (i["first_name"], i["last_name"], i["email"], i["role"], i["permissions"]) for i in response.json()["items"]
        ] == [
            ("Luca", "Bianchi", "luca@example.com", "player", {"change_role": True}),
            ("Anna", "Rossi", "anna@example.com", "admin", {"change_role": True}),
        ]

    def test_a_player_gets_403(self, client: TestClient, db_session: DbSession) -> None:
        sign_in(client, add_account(db_session, "Luca", "Bianchi", Role.PLAYER))

        assert client.get("/users").status_code == 403

    def test_no_session_gets_401(self, client: TestClient) -> None:
        assert client.get("/users").status_code == 401


class TestChangeRole:
    def test_an_admin_promotes_a_player_who_then_has_admin_permissions(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        anna = add_account(db_session, "Anna", "Rossi", Role.ADMIN)
        luca = add_account(db_session, "Luca", "Bianchi", Role.PLAYER)
        sign_in(client, anna)

        response = client.put(f"/users/{luca.id}/role", json={"role": "admin"}, headers=WRITE_HEADER)

        assert response.status_code == 200
        assert response.json() == {"id": luca.id, "role": "admin"}
        luca_client = TestClient(client.app, base_url="https://testserver")
        sign_in(luca_client, luca)
        assert luca_client.get("/users").status_code == 200

    def test_an_admin_demotes_themselves_when_another_admin_is_left_and_loses_the_permissions_in_the_same_session(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        anna = add_account(db_session, "Anna", "Rossi", Role.ADMIN)
        add_account(db_session, "Boris", "Verdi", Role.ADMIN)
        sign_in(client, anna)

        assert put_role(client, anna.id, "player") == 200

        assert client.get("/users").status_code == 403
        assert client.get("/players").status_code == 200

    def test_a_demoted_admin_gets_403_in_a_session_opened_before(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        anna = add_account(db_session, "Anna", "Rossi", Role.ADMIN)
        boris = add_account(db_session, "Boris", "Verdi", Role.ADMIN)
        sign_in(client, anna)
        boris_client = TestClient(client.app, base_url="https://testserver")
        sign_in(boris_client, boris)
        assert boris_client.get("/users").status_code == 200

        assert put_role(client, boris.id, "player") == 200

        assert boris_client.get("/users").status_code == 403

    def test_the_only_admin_cannot_demote_themselves(self, client: TestClient, db_session: DbSession) -> None:
        anna = add_account(db_session, "Anna", "Rossi", Role.ADMIN)
        sign_in(client, anna)

        response = client.put(f"/users/{anna.id}/role", json={"role": "player"}, headers=WRITE_HEADER)

        assert response.status_code == 409
        assert response.json()["detail"] == "Serve almeno un admin"
        assert anna.role == Role.ADMIN
        assert client.get("/users").status_code == 200

    def test_an_unknown_account_answers_404(self, client: TestClient, db_session: DbSession) -> None:
        sign_in(client, add_account(db_session, "Anna", "Rossi", Role.ADMIN))

        response = client.put("/users/0/role", json={"role": "admin"}, headers=WRITE_HEADER)

        assert response.status_code == 404
        assert response.json()["detail"] == "Account non trovato"

    def test_a_player_cannot_change_a_role_even_with_an_invalid_body_and_nothing_changes(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        luca = add_account(db_session, "Luca", "Bianchi", Role.PLAYER)
        sign_in(client, luca)

        assert put_role(client, luca.id, "admin") == 403
        assert client.put(f"/users/{luca.id}/role", json={}, headers=WRITE_HEADER).status_code == 403
        assert luca.role == Role.PLAYER

    def test_an_unknown_role_or_field_answers_422(self, client: TestClient, db_session: DbSession) -> None:
        anna = add_account(db_session, "Anna", "Rossi", Role.ADMIN)
        luca = add_account(db_session, "Luca", "Bianchi", Role.PLAYER)
        sign_in(client, anna)

        assert put_role(client, luca.id, "owner") == 422
        extra = client.put(f"/users/{luca.id}/role", json={"role": "admin", "id": 1}, headers=WRITE_HEADER)
        assert extra.status_code == 422
        assert luca.role == Role.PLAYER

    def test_promotion_cancels_the_open_invite_link_of_the_player(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        anna = add_account(db_session, "Anna", "Rossi", Role.ADMIN)
        luca = add_account(db_session, "Luca", "Bianchi", Role.PLAYER)
        sign_in(client, anna)
        invite = client.post("/auth/invites", json={"player_id": luca.player_id}, headers=WRITE_HEADER)
        token = invite.json()["path"].rsplit("/", 1)[1]
        assert client.get(f"/auth/invites/{token}").status_code == 200

        assert put_role(client, luca.id, "admin") == 200

        assert client.get(f"/auth/invites/{token}").status_code == 404
        assert db_session.scalars(select(Invite).where(Invite.used_at.is_(None))).all() == []

    def test_an_invite_link_created_before_a_promotion_cannot_reset_the_admin_password(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        anna = add_account(db_session, "Anna", "Rossi", Role.ADMIN)
        luca = add_account(db_session, "Luca", "Bianchi", Role.PLAYER)
        sign_in(client, anna)
        invite = client.post("/auth/invites", json={"player_id": luca.player_id}, headers=WRITE_HEADER)
        token = invite.json()["path"].rsplit("/", 1)[1]
        assert put_role(client, luca.id, "admin") == 200
        password_hash = luca.password_hash

        response = TestClient(client.app).post(
            f"/auth/invites/{token}/accept",
            json={"email": luca.email, "password": "calcetto del martedi"},
            headers=WRITE_HEADER,
        )

        assert response.status_code == 404
        assert luca.password_hash == password_hash
        assert luca.role == Role.ADMIN
