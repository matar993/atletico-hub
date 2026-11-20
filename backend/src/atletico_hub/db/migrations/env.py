from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection, create_engine

# Import every feature's models module here, so autogenerate and the drift test see its tables.
import atletico_hub.auth.models
import atletico_hub.players.models  # noqa: F401
from atletico_hub.db.base import Base
from atletico_hub.db.settings import DatabaseSettings

# The tests set configure_logger to False: fileConfig would replace pytest's log capture.
if context.config.attributes.get("configure_logger", True) and context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name, disable_existing_loggers=False)


def run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=Base.metadata, compare_server_default=True)
    with context.begin_transaction():
        context.run_migrations()


# The integration tests pass the connection of their own database; otherwise connect with the DB_* settings.
test_connection = context.config.attributes.get("connection")
if test_connection is None:
    with create_engine(DatabaseSettings().url).connect() as connection:
        run_migrations(connection)
else:
    run_migrations(test_connection)
