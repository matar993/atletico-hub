from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from atletico_hub.db.base import Base
from atletico_hub.db.settings import DatabaseSettings

# Import every feature's models module here, so autogenerate and the drift test see its tables.

if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name, disable_existing_loggers=False)

with create_engine(DatabaseSettings().url).connect() as connection:
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()
