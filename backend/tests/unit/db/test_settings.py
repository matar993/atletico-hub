import pytest
from pydantic import ValidationError

from atletico_hub.db.settings import DatabaseSettings


class TestDatabaseSettings:
    def test_url_builds_psycopg_url_from_db_variables(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DB_HOST", "db")
        monkeypatch.setenv("DB_PORT", "5432")
        monkeypatch.setenv("DB_USER", "atletico")
        monkeypatch.setenv("DB_PASS", "p@ss/word")
        monkeypatch.setenv("DB_DATABASE", "atletico")

        url = DatabaseSettings().url

        assert url.drivername == "postgresql+psycopg"
        assert url.host == "db"
        assert url.port == 5432
        assert url.username == "atletico"
        assert url.password == "p@ss/word"
        assert url.database == "atletico"

    def test_init_fails_when_a_variable_is_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DB_HOST", "db")
        monkeypatch.setenv("DB_PORT", "5432")
        monkeypatch.setenv("DB_USER", "atletico")
        monkeypatch.delenv("DB_PASS", raising=False)
        monkeypatch.setenv("DB_DATABASE", "atletico")

        with pytest.raises(ValidationError, match="DB_PASS"):
            DatabaseSettings()
