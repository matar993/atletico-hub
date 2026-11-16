from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import Engine

ALEMBIC_INI = Path(__file__).parents[3] / "alembic.ini"


class TestMigrations:
    # `alembic check` runs env.py, so it sees every models module env.py imports.
    def test_check_finds_no_drift_between_models_and_migrations(self, db_engine: Engine) -> None:
        config = Config(ALEMBIC_INI)

        with db_engine.connect() as connection:
            config.attributes["connection"] = connection
            command.check(config=config)
