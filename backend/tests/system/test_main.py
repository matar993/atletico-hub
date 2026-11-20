from fastapi.testclient import TestClient


class TestApp:
    def test_health_answers_ok(self, client: TestClient) -> None:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
