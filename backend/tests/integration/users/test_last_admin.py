import threading
from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, delete, func, select
from sqlalchemy.orm import Session as DbSession

from atletico_hub.auth.models import Account, Role
from atletico_hub.players.models import Player
from atletico_hub.users.repository import UserRepository
from atletico_hub.users.service import LastAdminError, UserService


class HeldCommit:
    """Tells the test it reached the commit, then commits only when the test lets it."""

    def __init__(self, session: DbSession) -> None:
        self._session = session
        self.reached = threading.Event()
        self.release = threading.Event()

    def commit(self) -> None:
        self.reached.set()
        self.release.wait(timeout=10)
        self._session.commit()


def demote(engine: Engine, account_id: int, held: list[HeldCommit] | None = None) -> LastAdminError | None:
    with DbSession(engine) as session:
        transaction = HeldCommit(session) if held is not None else session
        if held is not None:
            held.append(transaction)  # ty: ignore[invalid-argument-type]
        try:
            UserService(users=UserRepository(session), transaction=transaction).change_role(account_id, Role.PLAYER)
        except LastAdminError as ex:
            session.rollback()
            return ex
    return None


def add_admin(session: DbSession, first_name: str) -> Account:
    account = Account(
        player=Player(first_name=first_name, last_name="Admin"),
        email=f"{first_name}@example.com".lower(),
        password_hash="x",
        role=Role.ADMIN,
    )
    session.add(account)
    return account


@pytest.fixture
def two_committed_admins(db_engine: Engine) -> Iterator[tuple[int, int]]:
    # Real commits on two connections: the rows are removed at the end, the other tests roll back.
    with DbSession(db_engine) as session:
        anna, boris = add_admin(session, "Anna"), add_admin(session, "Boris")
        session.commit()
        ids = (anna.id, boris.id)
        player_ids = [anna.player_id, boris.player_id]
    yield ids
    with DbSession(db_engine) as session:
        session.execute(delete(Account).where(Account.id.in_(ids)))
        session.execute(delete(Player).where(Player.id.in_(player_ids)))
        session.commit()


class TestLastAdminUnderConcurrency:
    def test_two_admins_demoting_each_other_at_once_leave_one_admin(
        self, db_engine: Engine, two_committed_admins: tuple[int, int]
    ) -> None:
        anna_id, boris_id = two_committed_admins
        held: list[HeldCommit] = []
        first: list[LastAdminError | None] = []
        second: list[LastAdminError | None] = []
        thread_one = threading.Thread(target=lambda: first.append(demote(db_engine, anna_id, held)))
        thread_one.start()
        while not held:
            threading.Event().wait(0.01)
        assert held[0].reached.wait(timeout=10)
        # The first demotion holds the admin locks and waits before its commit: the second one waits for it.
        thread_two = threading.Thread(target=lambda: second.append(demote(db_engine, boris_id)))
        thread_two.start()
        thread_two.join(timeout=0.5)
        assert thread_two.is_alive()
        held[0].release.set()
        thread_one.join(timeout=10)
        thread_two.join(timeout=10)

        assert first == [None]
        assert len(second) == 1
        assert isinstance(second[0], LastAdminError)
        with DbSession(db_engine) as session:
            admins = session.scalar(select(func.count()).select_from(Account).where(Account.role == Role.ADMIN))
            assert admins == 1
