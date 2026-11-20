import pytest

from atletico_hub.auth.settings import AuthSettings


class TestAuthSettings:
    def test_cookie_secure_defaults_to_true(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("AUTH_COOKIE_SECURE", raising=False)

        assert AuthSettings().cookie_secure is True

    def test_cookie_secure_reads_the_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AUTH_COOKIE_SECURE", "false")

        assert AuthSettings().cookie_secure is False
