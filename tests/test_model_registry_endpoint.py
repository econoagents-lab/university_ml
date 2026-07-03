from fastapi.testclient import TestClient
from api.main import app


def test_model_registry_endpoint_exists():
    client = TestClient(app)
    response = client.get("/metadata/model-registry")
    assert response.status_code == 200
    body = response.json()
    assert "current_champion" in body
    assert "n_registered_models" in body
