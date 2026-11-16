import os
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session

from atletico_hub.db.settings import DatabaseSettings

ALEMBIC_INI = Path(__file__).parents[2] / "alembic.ini"


# One database per test run and xdist worker, migrated once: parallel workers, and runs from other worktrees
# on the shared stack, never share rows or schema.
@pytest.fixture(scope="session")
def db_engine() -> Iterator[Engine]:
    url = DatabaseSettings().url
    run = os.environ.get("PYTEST_XDIST_TESTRUNUID", uuid.uuid4().hex)[:8]
    name = f"{url.database}_test_{run}_{os.environ.get('PYTEST_XDIST_WORKER', 'main')}"
    admin = create_engine(url, isolation_level="AUTOCOMMIT")
    with admin.connect() as connection:
        connection.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
        connection.execute(text(f'CREATE DATABASE "{name}"'))
    engine = create_engine(url.set(database=name))
    config = Config(ALEMBIC_INI)
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        config.attributes["configure_logger"] = False
        command.upgrade(config, "head")
    yield engine
    engine.dispose()
    with admin.connect() as connection:
        connection.execute(text(f'DROP DATABASE "{name}" WITH (FORCE)'))
    admin.dispose()


# Each test runs in a transaction that is rolled back; a commit in the code under test only releases a savepoint.
@pytest.fixture
def db_session(db_engine: Engine) -> Iterator[Session]:
    with db_engine.connect() as connection:
        transaction = connection.begin()
        session = Session(bind=connection, join_transaction_mode="create_savepoint")
        yield session
        session.close()
        transaction.rollback()
