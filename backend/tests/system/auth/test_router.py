import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from atletico_hub.auth.models import Account, Invite, Role, Session
from atletico_hub.auth.passwords import Argon2PasswordHasher
from atletico_hub.players.models import Player

WRITE_HEADER = {"X-Requested-With": "atletico-hub"}
PASSWORD = "secret-pass"


class TestAuthRouter:
    def test_login_answers_the_user_and_sets_the_session_cookie(
        self, client: TestClient, db_session: DbSession, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AUTH_COOKIE_SECURE", "true")
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

        response = client.post(
            "/auth/login", json={"email": "Anna@Example.com", "password": PASSWORD}, headers=WRITE_HEADER
        )

        cookie = response.headers["set-cookie"].lower()
        assert response.status_code == 200
        assert response.json() == {
            "first_name": "Anna",
            "last_name": "Rossi",
            "email": "anna@example.com",
            "role": "admin",
        }
        for flag in ("httponly", "samesite=lax", "max-age=2592000", "path=/", "secure"):
            assert flag in cookie
        assert client.get("/auth/me").status_code == 200

    def test_login_leaves_out_the_secure_flag_when_the_setting_is_off(
        self, client: TestClient, db_session: DbSession, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AUTH_COOKIE_SECURE", "false")
        db_session.add(
            Account(
                player=Player(first_name="Anna", last_name="Rossi"),
                email="anna@example.com",
                password_hash=Argon2PasswordHasher().hash(PASSWORD),
                role=Role.PLAYER,
                failed_logins=0,
            )
        )
        db_session.flush()

        response = client.post(
            "/auth/login", json={"email": "anna@example.com", "password": PASSWORD}, headers=WRITE_HEADER
        )

        assert "secure" not in response.headers["set-cookie"].lower()

    def test_login_answers_401_to_a_wrong_password_and_sets_no_cookie(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        db_session.add(
            Account(
                player=Player(first_name="Anna", last_name="Rossi"),
                email="anna@example.com",
                password_hash=Argon2PasswordHasher().hash(PASSWORD),
                role=Role.PLAYER,
                failed_logins=0,
            )
        )
        db_session.flush()

        response = client.post(
            "/auth/login", json={"email": "anna@example.com", "password": "wrong-pass"}, headers=WRITE_HEADER
        )

        assert response.status_code == 401
        assert response.json() == {"detail": "Email o password non corretti"}
        assert "set-cookie" not in response.headers

    def test_login_answers_an_unknown_email_like_a_wrong_password(self, client: TestClient) -> None:
        response = client.post(
            "/auth/login", json={"email": "nobody@example.com", "password": "wrong-pass"}, headers=WRITE_HEADER
        )

        assert response.status_code == 401
        assert response.json() == {"detail": "Email o password non corretti"}

    def test_login_answers_429_after_five_failures_even_with_the_right_password(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        db_session.add(
            Account(
                player=Player(first_name="Anna", last_name="Rossi"),
                email="anna@example.com",
                password_hash=Argon2PasswordHasher().hash(PASSWORD),
                role=Role.PLAYER,
                failed_logins=0,
            )
        )
        db_session.flush()
        for _ in range(5):
            client.post(
                "/auth/login", json={"email": "anna@example.com", "password": "wrong-pass"}, headers=WRITE_HEADER
            )

        response = client.post(
            "/auth/login", json={"email": "anna@example.com", "password": PASSWORD}, headers=WRITE_HEADER
        )

        assert response.status_code == 429
        assert response.json() == {"detail": "Troppi tentativi, riprova tra 15 minuti"}
        assert "set-cookie" not in response.headers

    def test_login_answers_403_without_the_csrf_header(self, client: TestClient) -> None:
        response = client.post("/auth/login", json={"email": "anna@example.com", "password": PASSWORD})

        assert response.status_code == 403

    def test_logout_ends_the_session_and_clears_the_cookie(self, client: TestClient, db_session: DbSession) -> None:
        db_session.add(
            Account(
                player=Player(first_name="Anna", last_name="Rossi"),
                email="anna@example.com",
                password_hash=Argon2PasswordHasher().hash(PASSWORD),
                role=Role.PLAYER,
                failed_logins=0,
            )
        )
        db_session.flush()
        client.post("/auth/login", json={"email": "anna@example.com", "password": PASSWORD}, headers=WRITE_HEADER)
        old_cookie = client.cookies["atletico_session"]

        response = client.post("/auth/logout", headers=WRITE_HEADER)

        assert response.status_code == 204
        assert "max-age=0" in response.headers["set-cookie"].lower()
        stale = TestClient(client.app, base_url="https://testserver")
        assert stale.get("/auth/me", headers={"Cookie": f"atletico_session={old_cookie}"}).status_code == 401
        assert db_session.scalar(select(func.count()).select_from(Session)) == 0

    def test_logout_answers_401_without_a_session_cookie(self, client: TestClient) -> None:
        assert client.post("/auth/logout", headers=WRITE_HEADER).status_code == 401

    def test_me_answers_401_without_a_session(self, client: TestClient) -> None:
        assert client.get("/auth/me").status_code == 401

    def test_me_answers_the_signed_in_user(self, client: TestClient, db_session: DbSession) -> None:
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

        response = client.get("/auth/me")

        assert response.json() == {
            "first_name": "Anna",
            "last_name": "Rossi",
            "email": "anna@example.com",
            "role": "admin",
        }

    def test_create_invite_answers_the_path_and_expiry_to_an_admin(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        admin = Account(
            player=Player(first_name="Anna", last_name="Rossi"),
            email="anna@example.com",
            password_hash=Argon2PasswordHasher().hash(PASSWORD),
            role=Role.ADMIN,
            failed_logins=0,
        )
        luca = Player(first_name="Luca", last_name="Bianchi")
        db_session.add_all([admin, luca])
        db_session.flush()
        client.post("/auth/login", json={"email": "anna@example.com", "password": PASSWORD}, headers=WRITE_HEADER)

        response = client.post("/auth/invites", json={"player_id": luca.id}, headers=WRITE_HEADER)

        assert response.status_code == 200
        assert response.json()["path"].startswith("/invite/")
        assert "expires_at" in response.json()
        assert db_session.scalar(select(func.count()).select_from(Invite)) == 1

    def test_create_invite_answers_403_to_a_player_and_stores_nothing(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        player = Account(
            player=Player(first_name="Anna", last_name="Rossi"),
            email="anna@example.com",
            password_hash=Argon2PasswordHasher().hash(PASSWORD),
            role=Role.PLAYER,
            failed_logins=0,
        )
        db_session.add(player)
        db_session.flush()
        client.post("/auth/login", json={"email": "anna@example.com", "password": PASSWORD}, headers=WRITE_HEADER)

        response = client.post("/auth/invites", json={"player_id": player.player.id}, headers=WRITE_HEADER)

        assert response.status_code == 403
        assert db_session.scalar(select(func.count()).select_from(Invite)) == 0

    def test_create_invite_answers_401_without_a_session(self, client: TestClient) -> None:
        assert client.post("/auth/invites", json={"player_id": 1}, headers=WRITE_HEADER).status_code == 401

    def test_create_invite_answers_404_for_an_unknown_player(self, client: TestClient, db_session: DbSession) -> None:
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

        response = client.post("/auth/invites", json={"player_id": 0}, headers=WRITE_HEADER)

        assert response.status_code == 404

    @pytest.mark.parametrize(
        ("target_role", "own_account", "expected"),
        [(Role.ADMIN, False, 409), (Role.ADMIN, True, 409), (Role.PLAYER, False, 200)],
    )
    def test_create_invite_for_an_admin_account_answers_409_and_creates_no_link(
        self, client: TestClient, db_session: DbSession, target_role: Role, own_account: bool, expected: int
    ) -> None:
        admin = Account(
            player=Player(first_name="Anna", last_name="Rossi"),
            email="anna@example.com",
            password_hash=Argon2PasswordHasher().hash(PASSWORD),
            role=Role.ADMIN,
            failed_logins=0,
        )
        other = Account(
            player=Player(first_name="Boss", last_name="Verdi"),
            email="boss@example.com",
            password_hash="x",
            role=target_role,
            failed_logins=0,
        )
        db_session.add_all([admin, other])
        db_session.flush()
        client.post("/auth/login", json={"email": "anna@example.com", "password": PASSWORD}, headers=WRITE_HEADER)
        target = admin if own_account else other

        response = client.post("/auth/invites", json={"player_id": target.player_id}, headers=WRITE_HEADER)

        assert response.status_code == expected
        if expected == 409:
            assert response.json()["detail"] == "La password di un admin si reimposta solo da riga di comando"
            assert db_session.scalar(select(func.count()).select_from(Invite)) == 0

    def test_open_invite_answers_the_player_without_an_account(self, client: TestClient, db_session: DbSession) -> None:
        admin = Account(
            player=Player(first_name="Anna", last_name="Rossi"),
            email="anna@example.com",
            password_hash=Argon2PasswordHasher().hash(PASSWORD),
            role=Role.ADMIN,
            failed_logins=0,
        )
        luca = Player(first_name="Luca", last_name="Bianchi")
        db_session.add_all([admin, luca])
        db_session.flush()
        client.post("/auth/login", json={"email": "anna@example.com", "password": PASSWORD}, headers=WRITE_HEADER)
        path = client.post("/auth/invites", json={"player_id": luca.id}, headers=WRITE_HEADER).json()["path"]
        anonymous = TestClient(client.app, base_url="https://testserver")

        response = anonymous.get(f"/auth/invites/{path.removeprefix('/invite/')}")

        assert response.status_code == 200
        assert response.json() == {"first_name": "Luca", "last_name": "Bianchi", "has_account": False, "email": None}

    def test_open_invite_answers_the_email_of_a_player_with_an_account(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        admin = Account(
            player=Player(first_name="Boss", last_name="Verdi"),
            email="boss@example.com",
            password_hash=Argon2PasswordHasher().hash(PASSWORD),
            role=Role.ADMIN,
            failed_logins=0,
        )
        anna = Account(
            player=Player(first_name="Anna", last_name="Rossi"),
            email="anna@example.com",
            password_hash=Argon2PasswordHasher().hash(PASSWORD),
            role=Role.PLAYER,
            failed_logins=0,
        )
        db_session.add_all([admin, anna])
        db_session.flush()
        client.post("/auth/login", json={"email": "boss@example.com", "password": PASSWORD}, headers=WRITE_HEADER)
        path = client.post("/auth/invites", json={"player_id": anna.player.id}, headers=WRITE_HEADER).json()["path"]

        response = TestClient(client.app, base_url="https://testserver").get(
            f"/auth/invites/{path.removeprefix('/invite/')}"
        )

        assert response.json() == {
            "first_name": "Anna",
            "last_name": "Rossi",
            "has_account": True,
            "email": "anna@example.com",
        }

    def test_open_invite_answers_404_to_an_unknown_link(self, client: TestClient) -> None:
        response = client.get("/auth/invites/unknown")

        assert response.status_code == 404
        assert response.json() == {"detail": "Link non valido o scaduto"}

    def test_accept_invite_creates_the_account_and_signs_the_player_in(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        admin = Account(
            player=Player(first_name="Anna", last_name="Rossi"),
            email="anna@example.com",
            password_hash=Argon2PasswordHasher().hash(PASSWORD),
            role=Role.ADMIN,
            failed_logins=0,
        )
        luca = Player(first_name="Luca", last_name="Bianchi")
        db_session.add_all([admin, luca])
        db_session.flush()
        client.post("/auth/login", json={"email": "anna@example.com", "password": PASSWORD}, headers=WRITE_HEADER)
        path = client.post("/auth/invites", json={"player_id": luca.id}, headers=WRITE_HEADER).json()["path"]
        newcomer = TestClient(client.app, base_url="https://testserver")

        response = newcomer.post(
            f"/auth/invites/{path.removeprefix('/invite/')}/accept",
            json={"email": "Luca@Example.com", "password": "calcetto del martedi"},
            headers=WRITE_HEADER,
        )

        assert response.status_code == 200
        assert response.json() == {
            "first_name": "Luca",
            "last_name": "Bianchi",
            "email": "luca@example.com",
            "role": "player",
        }
        assert "atletico_session" in response.headers["set-cookie"]
        assert newcomer.get("/auth/me").json()["email"] == "luca@example.com"

    def test_accept_invite_answers_409_for_an_email_in_use_and_keeps_the_link_valid(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        admin = Account(
            player=Player(first_name="Anna", last_name="Rossi"),
            email="anna@example.com",
            password_hash=Argon2PasswordHasher().hash(PASSWORD),
            role=Role.ADMIN,
            failed_logins=0,
        )
        luca = Player(first_name="Luca", last_name="Bianchi")
        db_session.add_all([admin, luca])
        db_session.flush()
        client.post("/auth/login", json={"email": "anna@example.com", "password": PASSWORD}, headers=WRITE_HEADER)
        token = (
            client.post("/auth/invites", json={"player_id": luca.id}, headers=WRITE_HEADER)
            .json()["path"]
            .removeprefix("/invite/")
        )
        newcomer = TestClient(client.app, base_url="https://testserver")

        response = newcomer.post(
            f"/auth/invites/{token}/accept",
            json={"email": "ANNA@example.com", "password": "calcetto del martedi"},
            headers=WRITE_HEADER,
        )

        assert response.status_code == 409
        assert db_session.scalar(select(func.count()).select_from(Account)) == 1
        assert newcomer.get(f"/auth/invites/{token}").status_code == 200

    def test_accept_invite_answers_422_to_a_password_of_7_characters(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        admin = Account(
            player=Player(first_name="Anna", last_name="Rossi"),
            email="anna@example.com",
            password_hash=Argon2PasswordHasher().hash(PASSWORD),
            role=Role.ADMIN,
            failed_logins=0,
        )
        luca = Player(first_name="Luca", last_name="Bianchi")
        db_session.add_all([admin, luca])
        db_session.flush()
        client.post("/auth/login", json={"email": "anna@example.com", "password": PASSWORD}, headers=WRITE_HEADER)
        token = (
            client.post("/auth/invites", json={"player_id": luca.id}, headers=WRITE_HEADER)
            .json()["path"]
            .removeprefix("/invite/")
        )

        response = TestClient(client.app, base_url="https://testserver").post(
            f"/auth/invites/{token}/accept",
            json={"email": "luca@example.com", "password": "1234567"},
            headers=WRITE_HEADER,
        )

        assert response.status_code == 422
        assert "at least 8 characters" in response.text

    def test_accept_invite_answers_422_without_an_email_for_a_player_without_an_account(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        admin = Account(
            player=Player(first_name="Anna", last_name="Rossi"),
            email="anna@example.com",
            password_hash=Argon2PasswordHasher().hash(PASSWORD),
            role=Role.ADMIN,
            failed_logins=0,
        )
        luca = Player(first_name="Luca", last_name="Bianchi")
        db_session.add_all([admin, luca])
        db_session.flush()
        client.post("/auth/login", json={"email": "anna@example.com", "password": PASSWORD}, headers=WRITE_HEADER)
        token = (
            client.post("/auth/invites", json={"player_id": luca.id}, headers=WRITE_HEADER)
            .json()["path"]
            .removeprefix("/invite/")
        )

        response = TestClient(client.app, base_url="https://testserver").post(
            f"/auth/invites/{token}/accept", json={"password": "calcetto del martedi"}, headers=WRITE_HEADER
        )

        assert response.status_code == 422

    def test_accept_invite_for_a_player_with_an_account_resets_the_password_and_ends_the_sessions(
        self, client: TestClient, db_session: DbSession
    ) -> None:
        boss = Account(
            player=Player(first_name="Boss", last_name="Verdi"),
            email="boss@example.com",
            password_hash=Argon2PasswordHasher().hash(PASSWORD),
            role=Role.ADMIN,
            failed_logins=0,
        )
        anna = Account(
            player=Player(first_name="Anna", last_name="Rossi"),
            email="anna@example.com",
            password_hash=Argon2PasswordHasher().hash(PASSWORD),
            role=Role.PLAYER,
            failed_logins=0,
        )
        db_session.add_all([boss, anna])
        db_session.flush()
        second_device = TestClient(client.app, base_url="https://testserver")
        second_device.post(
            "/auth/login", json={"email": "anna@example.com", "password": PASSWORD}, headers=WRITE_HEADER
        )
        client.post("/auth/login", json={"email": "boss@example.com", "password": PASSWORD}, headers=WRITE_HEADER)
        token = (
            client.post("/auth/invites", json={"player_id": anna.player.id}, headers=WRITE_HEADER)
            .json()["path"]
            .removeprefix("/invite/")
        )
        third_device = TestClient(client.app, base_url="https://testserver")

        response = third_device.post(
            f"/auth/invites/{token}/accept", json={"password": "a brand new password"}, headers=WRITE_HEADER
        )

        assert response.status_code == 200
        assert response.json()["role"] == "player"
        assert second_device.get("/auth/me").status_code == 401
        assert third_device.get("/auth/me").status_code == 200
        login = third_device.post(
            "/auth/login",
            json={"email": "anna@example.com", "password": "a brand new password"},
            headers=WRITE_HEADER,
        )
        assert login.status_code == 200

    def test_accept_invite_answers_404_to_a_used_link(self, client: TestClient, db_session: DbSession) -> None:
        admin = Account(
            player=Player(first_name="Boss", last_name="Verdi"),
            email="boss@example.com",
            password_hash=Argon2PasswordHasher().hash(PASSWORD),
            role=Role.ADMIN,
            failed_logins=0,
        )
        anna = Account(
            player=Player(first_name="Anna", last_name="Rossi"),
            email="anna@example.com",
            password_hash=Argon2PasswordHasher().hash(PASSWORD),
            role=Role.PLAYER,
            failed_logins=0,
        )
        db_session.add_all([admin, anna])
        db_session.flush()
        client.post("/auth/login", json={"email": "boss@example.com", "password": PASSWORD}, headers=WRITE_HEADER)
        token = (
            client.post("/auth/invites", json={"player_id": anna.player.id}, headers=WRITE_HEADER)
            .json()["path"]
            .removeprefix("/invite/")
        )
        other = TestClient(client.app, base_url="https://testserver")
        other.post(f"/auth/invites/{token}/accept", json={"password": "a brand new password"}, headers=WRITE_HEADER)

        response = other.post(
            f"/auth/invites/{token}/accept", json={"password": "another new password"}, headers=WRITE_HEADER
        )

        assert response.status_code == 404
        assert other.get(f"/auth/invites/{token}").status_code == 404
