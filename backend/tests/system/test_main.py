import re
from collections.abc import Callable

from fastapi.testclient import TestClient

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
