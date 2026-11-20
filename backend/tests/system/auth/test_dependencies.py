from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Annotated

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as DbSession

from atletico_hub.auth.dependencies import current_account, require_admin
from atletico_hub.auth.models import Account, Role, Session
from atletico_hub.auth.tokens import hash_token
from atletico_hub.players.models import Player

WRITE_HEADER = {"X-Requested-With": "atletico-hub"}


def open_endpoint() -> dict[str, str]:
    return {}


def account_endpoint(account: Annotated[Account, Depends(current_account)]) -> dict[str, str]:
    return {"email": account.email}


def admin_endpoint(account: Annotated[Account, Depends(require_admin)]) -> dict[str, str]:
    return {"email": account.email}


class TestDependencies:
    def test_require_csrf_header_refuses_a_write_without_the_header_and_changes_nothing(
        self, client: TestClient, mount_route: Callable[..., None]
    ) -> None:
        calls: list[int] = []

        def write() -> dict[str, str]:
            calls.append(1)
            return {}

        mount_route("/_test/write", write, ["POST"])

        response = client.post("/_test/write")

        assert response.status_code == 403
        assert calls == []

    def test_require_csrf_header_refuses_a_write_with_another_header_value(
        self, client: TestClient, mount_route: Callable[..., None]
    ) -> None:
        mount_route("/_test/write", open_endpoint, ["DELETE"])

        response = client.delete("/_test/write", headers={"X-Requested-With": "other"})

        assert response.status_code == 403

    def test_require_csrf_header_lets_a_write_with_the_header_through(
        self, client: TestClient, mount_route: Callable[..., None]
    ) -> None:
        mount_route("/_test/write", open_endpoint, ["POST"])

        response = client.post("/_test/write", headers=WRITE_HEADER)

        assert response.status_code == 200

    def test_require_csrf_header_lets_a_read_without_the_header_through(self, client: TestClient) -> None:
        assert client.get("/health").status_code == 200

    def test_current_account_refuses_a_request_without_a_cookie(
        self, client: TestClient, mount_route: Callable[..., None]
    ) -> None:
        mount_route("/_test/me", account_endpoint, ["GET"])

        assert client.get("/_test/me").status_code == 401

    def test_current_account_refuses_an_unknown_token(
        self, client: TestClient, mount_route: Callable[..., None]
    ) -> None:
        mount_route("/_test/me", account_endpoint, ["GET"])

        response = client.get("/_test/me", headers={"Cookie": "atletico_session=unknown"})

        assert response.status_code == 401

    def test_current_account_refuses_a_session_unused_for_31_days(
        self, client: TestClient, db_session: DbSession, mount_route: Callable[..., None]
    ) -> None:
        account = Account(
            player=Player(first_name="Anna", last_name="Rossi"),
            email="anna@example.com",
            password_hash="x",
            role=Role.PLAYER,
            failed_logins=0,
        )
        db_session.add(
            Session(
                account=account,
                token_hash=hash_token("old-token"),
                last_used_at=datetime.now(UTC) - timedelta(days=31),
            )
        )
        db_session.flush()
        mount_route("/_test/me", account_endpoint, ["GET"])

        response = client.get("/_test/me", headers={"Cookie": "atletico_session=old-token"})

        assert response.status_code == 401

    def test_current_account_answers_and_sets_the_cookie_again(
        self, client: TestClient, db_session: DbSession, mount_route: Callable[..., None]
    ) -> None:
        account = Account(
            player=Player(first_name="Anna", last_name="Rossi"),
            email="anna@example.com",
            password_hash="x",
            role=Role.PLAYER,
            failed_logins=0,
        )
        db_session.add(Session(account=account, token_hash=hash_token("good-token"), last_used_at=datetime.now(UTC)))
        db_session.flush()
        mount_route("/_test/me", account_endpoint, ["GET"])

        response = client.get("/_test/me", headers={"Cookie": "atletico_session=good-token"})

        cookie = response.headers["set-cookie"].lower()
        assert response.json() == {"email": "anna@example.com"}
        assert "atletico_session=good-token" in cookie
        assert "max-age=2592000" in cookie
        assert "httponly" in cookie
        assert "samesite=lax" in cookie

    @pytest.mark.parametrize(("role", "status_code"), [(Role.PLAYER, 403), (Role.ADMIN, 200)])
    def test_require_admin_answers_403_to_a_player_and_lets_an_admin_through(
        self,
        client: TestClient,
        db_session: DbSession,
        mount_route: Callable[..., None],
        role: Role,
        status_code: int,
    ) -> None:
        account = Account(
            player=Player(first_name="Anna", last_name="Rossi"),
            email="anna@example.com",
            password_hash="x",
            role=role,
            failed_logins=0,
        )
        db_session.add(Session(account=account, token_hash=hash_token("token"), last_used_at=datetime.now(UTC)))
        db_session.flush()
        mount_route("/_test/admin", admin_endpoint, ["GET"])

        response = client.get("/_test/admin", headers={"Cookie": "atletico_session=token"})

        assert response.status_code == status_code
