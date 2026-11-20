import re
from collections.abc import Callable

import pytest
from fastapi import Depends
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as DbSession

from atletico_hub.auth.dependencies import require
from atletico_hub.auth.models import Account, Role
from atletico_hub.auth.passwords import Argon2PasswordHasher
from atletico_hub.auth.permissions import Permission
from atletico_hub.main import app, create_app
from atletico_hub.players.models import Player
from atletico_hub.settings import ApiSettings

WRITE_HEADER = {"X-Requested-With": "atletico-hub"}
WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
# The routes open without a session: the health check, login, the invite routes and the OpenAPI pages.
OPEN_ROUTES = {
    ("GET", "/health"),
    ("POST", "/auth/login"),
    ("GET", "/auth/invites/{token}"),
    ("POST", "/auth/invites/{token}/accept"),
    ("GET", "/openapi.json"),
    ("GET", "/docs"),
    ("GET", "/docs/oauth2-redirect"),
    ("GET", "/redoc"),
}


# The routes open to every signed-in user: no permission, only a session.
SIGNED_IN_ROUTES = {
    ("GET", "/auth/me"),
    ("POST", "/auth/logout"),
}
PASSWORD = "secret-pass"
# Status of each route that checks a permission, for no session, a player and an admin.
# The admin sends an empty body: it passes the permission check and stops at the body check (422).
ROLE_TABLE = {
    ("GET", "/players"): (401, 200, 200),
    ("POST", "/players"): (401, 403, 422),
    ("PATCH", "/players/{player_id}"): (401, 403, 422),
    ("POST", "/auth/invites"): (401, 403, 422),
}


def permissions_of(dependant: Dependant) -> list[Permission]:
    found = []
    for dependency in dependant.dependencies:
        permission = getattr(dependency.call, "permission", None)
        if permission is not None:
            found.append(permission)
        found.extend(permissions_of(dependency))
    return found


def methods_of(route: APIRoute) -> list[str]:
    return sorted((route.methods or set()) - {"HEAD", "OPTIONS"})


def routes_without_a_declaration(client: TestClient) -> list[str]:
    undeclared = []
    for route in client.app.routes:
        if not isinstance(route, APIRoute):
            continue
        for method in methods_of(route):
            declared = (method, route.path) in OPEN_ROUTES | SIGNED_IN_ROUTES
            if not declared and not permissions_of(route.dependant):
                undeclared.append(f"{method} {route.path}")
    return undeclared


def routes_without_a_table_row(client: TestClient) -> list[str]:
    missing = []
    for route in client.app.routes:
        if not isinstance(route, APIRoute) or not permissions_of(route.dependant):
            continue
        missing.extend(f"{m} {route.path}" for m in methods_of(route) if (m, route.path) not in ROLE_TABLE)
    return missing


def routes_answering_without_a_401(client: TestClient) -> list[str]:
    answers = []
    for route in client.app.routes:
        for method in sorted(getattr(route, "methods", None) or set()):
            if method in {"HEAD", "OPTIONS"} or (method, route.path) in OPEN_ROUTES:
                continue
            path = re.sub(r"\{[^}]+\}", "1", route.path)
            response = client.request(method, path, headers=WRITE_HEADER, json={} if method in WRITE_METHODS else None)
            if response.status_code != 401:
                answers.append(f"{method} {route.path} answers {response.status_code}")
    return answers


def open_endpoint() -> dict[str, str]:
    return {}


class TestApp:
    def test_health_answers_ok(self, client: TestClient) -> None:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_every_route_outside_the_open_list_answers_401_without_a_session(self, client: TestClient) -> None:
        assert routes_answering_without_a_401(client) == []

    def test_the_walk_finds_a_route_added_without_the_session_dependency(
        self, client: TestClient, mount_route: Callable[..., None]
    ) -> None:
        mount_route("/_test/forgotten", open_endpoint, ["GET"])

        assert routes_answering_without_a_401(client) == ["GET /_test/forgotten answers 200"]

    def test_every_route_declares_a_permission_or_is_listed_as_open(self, client: TestClient) -> None:
        assert routes_without_a_declaration(client) == []

    def test_the_declaration_walk_finds_a_route_mounted_without_a_permission(
        self, client: TestClient, mount_route: Callable[..., None]
    ) -> None:
        mount_route("/_test/forgotten", open_endpoint, ["GET"])

        assert routes_without_a_declaration(client) == ["GET /_test/forgotten"]

    def test_every_route_with_a_permission_has_a_row_in_the_role_table(self, client: TestClient) -> None:
        assert routes_without_a_table_row(client) == []

    def test_the_table_walk_finds_a_permission_route_without_a_row(
        self, client: TestClient, mount_route: Callable[..., None]
    ) -> None:
        mount_route("/_test/guarded", open_endpoint, ["GET"], dependencies=[Depends(require(Permission.SQUAD_VIEW))])

        assert routes_without_a_table_row(client) == ["GET /_test/guarded"]


def signed_in_client(db_session: DbSession, role: Role) -> TestClient:
    email = f"{role}@example.com"
    db_session.add(
        Account(
            player=Player(first_name=role.value, last_name="Test"),
            email=email,
            password_hash=Argon2PasswordHasher().hash(PASSWORD),
            role=role,
            failed_logins=0,
        )
    )
    db_session.flush()
    client = TestClient(app, base_url="https://testserver")
    client.post("/auth/login", json={"email": email, "password": PASSWORD}, headers=WRITE_HEADER)
    return client


class TestRoleTable:
    @pytest.mark.parametrize(("method", "path"), sorted(ROLE_TABLE))
    def test_route_answers_each_role_as_the_table_says(
        self, client: TestClient, db_session: DbSession, method: str, path: str
    ) -> None:
        clients = (client, signed_in_client(db_session, Role.PLAYER), signed_in_client(db_session, Role.ADMIN))

        url = path.replace("{player_id}", "1")
        answers = tuple(
            c.request(method, url, headers=WRITE_HEADER, json={} if method in WRITE_METHODS else None).status_code
            for c in clients
        )

        assert answers == ROLE_TABLE[(method, path)]


class TestStrictBodies:
    @pytest.mark.parametrize(
        ("path", "body"),
        [
            ("/auth/login", {"email": "a@example.com", "password": "x", "role": "admin"}),
            ("/auth/invites/some-token/accept", {"password": "long-enough-pass", "role": "admin"}),
        ],
    )
    def test_open_route_answers_422_to_an_unknown_field(self, client: TestClient, path: str, body: dict) -> None:
        assert client.post(path, json=body, headers=WRITE_HEADER).status_code == 422

    @pytest.mark.parametrize(
        ("path", "body"),
        [
            ("/players", {"first_name": "Luca", "last_name": "Bianchi", "role": "admin"}),
            ("/auth/invites", {"player_id": 1, "role": "admin"}),
        ],
    )
    def test_admin_route_answers_422_to_an_unknown_field_and_changes_nothing(
        self, client: TestClient, db_session: DbSession, path: str, body: dict
    ) -> None:
        admin = signed_in_client(db_session, Role.ADMIN)
        players_before = len(admin.get("/players").json()["items"])

        response = admin.post(path, json=body, headers=WRITE_HEADER)

        assert response.status_code == 422
        assert len(admin.get("/players").json()["items"]) == players_before


class TestApiDocs:
    PAGES = ("/openapi.json", "/docs", "/redoc")

    def test_pages_answer_404_by_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("API_DOCS_ENABLED", raising=False)
        client = TestClient(create_app(ApiSettings()))

        assert [client.get(page).status_code for page in self.PAGES] == [404, 404, 404]

    def test_pages_answer_when_the_setting_is_on(self) -> None:
        client = TestClient(create_app(ApiSettings(docs_enabled=True)))

        assert [client.get(page).status_code for page in self.PAGES] == [200, 200, 200]

    def test_the_schema_is_available_in_code_with_the_pages_off(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("API_DOCS_ENABLED", raising=False)
        assert "/players" in create_app(ApiSettings()).openapi()["paths"]

    def test_the_setting_reads_the_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("API_DOCS_ENABLED", "true")

        assert ApiSettings().docs_enabled is True
