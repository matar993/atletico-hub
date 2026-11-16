from functools import cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from atletico_hub.db.settings import DatabaseSettings


# Built on first use, not at import: the OpenAPI document is generated without database settings.
# pool_pre_ping: after a Postgres restart, stale pooled connections are replaced instead of failing a request.
@cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=create_engine(DatabaseSettings().url, pool_pre_ping=True))
