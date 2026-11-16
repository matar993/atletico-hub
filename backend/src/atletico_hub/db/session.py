from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session, sessionmaker

from atletico_hub.db.engine import get_session_factory


def get_session(factory: Annotated[sessionmaker[Session], Depends(get_session_factory)]) -> Generator[Session]:
    session = factory()
    try:
        yield session
    finally:
        session.close()
