from fastapi.testclient import TestClient

from atlas_api.main import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["provider"]["provider_name"] in {"fake", "codex", "openai"}

