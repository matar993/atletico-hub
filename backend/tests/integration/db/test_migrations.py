from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, inspect

ALEMBIC_INI = Path(__file__).parents[3] / "alembic.ini"


class TestMigrations:
    # `alembic check` runs env.py, so it sees every models module env.py imports.
    def test_check_finds_no_drift_between_models_and_migrations(self, db_engine: Engine) -> None:
        config = Config(ALEMBIC_INI)

        with db_engine.connect() as connection:
            config.attributes["connection"] = connection
            config.attributes["configure_logger"] = False
            command.check(config=config)

    # One transaction: Postgres DDL is transactional, so a failing downgrade leaves the test database as it was.
    def test_downgrade_reverses_every_migration(self, db_engine: Engine) -> None:
        config = Config(ALEMBIC_INI)

        with db_engine.begin() as connection:
            config.attributes["connection"] = connection
            config.attributes["configure_logger"] = False
            command.downgrade(config=config, revision="base")
            assert inspect(connection).get_table_names() == ["alembic_version"]
            command.upgrade(config=config, revision="head")

    def test_upgrade_creates_the_squad_and_auth_tables(self, db_engine: Engine) -> None:
        assert {"players", "accounts", "sessions", "invites"} <= set(inspect(db_engine).get_table_names())
