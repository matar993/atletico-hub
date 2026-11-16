import pytest

from atletico_hub.db.engine import get_session_factory


class TestGetSessionFactory:
    def test_get_session_factory_binds_engine_to_settings_url(
        self, monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest
    ) -> None:
        monkeypatch.setenv("DB_HOST", "db")
        monkeypatch.setenv("DB_PORT", "5432")
        monkeypatch.setenv("DB_USER", "atletico")
        monkeypatch.setenv("DB_PASS", "secret")
        monkeypatch.setenv("DB_DATABASE", "atletico")
        get_session_factory.cache_clear()
        request.addfinalizer(get_session_factory.cache_clear)

        factory = get_session_factory()

        url = factory.kw["bind"].url
        assert url.drivername == "postgresql+psycopg"
        assert url.host == "db"
        assert url.database == "atletico"
        assert factory.kw["bind"].pool._pre_ping is True
