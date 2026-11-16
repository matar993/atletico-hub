from unittest.mock import MagicMock

import pytest

from atletico_hub.db.session import get_session


class TestGetSession:
    def test_get_session_yields_session_and_closes_it(self) -> None:
        session = MagicMock()
        dependency = get_session(factory=MagicMock(return_value=session))

        assert next(dependency) is session
        with pytest.raises(StopIteration):
            next(dependency)

        session.close.assert_called_once_with()

    def test_get_session_closes_session_when_route_raises(self) -> None:
        session = MagicMock()
        dependency = get_session(factory=MagicMock(return_value=session))
        next(dependency)

        with pytest.raises(RuntimeError):
            dependency.throw(RuntimeError("route failed"))

        session.close.assert_called_once_with()
