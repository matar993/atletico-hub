from collections.abc import Callable, Iterator
from typing import Any

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from atletico_hub.db.session import get_session
from atletico_hub.main import app


# The https base URL lets the client send back cookies with the Secure flag, as a browser would.
@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_session] = lambda: db_session
    yield TestClient(app, base_url="https://testserver")
    app.dependency_overrides.clear()


# Mounts a route on the real app for the length of one test, and removes it after.
@pytest.fixture
def mount_route() -> Iterator[Callable[..., None]]:
    mounted: list[str] = []

    def mount(path: str, endpoint: Callable[..., Any], methods: list[str]) -> None:
        app.add_api_route(path, endpoint, methods=methods)
        mounted.append(path)

    yield mount
    app.router.routes = [
        route for route in app.router.routes if not (isinstance(route, APIRoute) and route.path in mounted)
    ]
