from fastapi.testclient import TestClient

from atletico_hub.main import app


class TestApp:
    def test_health_answers_ok(self) -> None:
        response = TestClient(app).get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
