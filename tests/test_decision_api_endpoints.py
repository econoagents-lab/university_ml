from fastapi.testclient import TestClient

from api.main import app


def test_decision_kpis_endpoint():
    client = TestClient(app)
    response = client.get("/decision/riesgo-caida/kpis")
    assert response.status_code == 200
    body = response.json()
    assert "total_operaciones" in body
    assert "valor_total_en_riesgo" in body


def test_decision_queue_endpoint():
    client = TestClient(app)
    response = client.get("/decision/riesgo-caida/queue?limit=5")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert len(body["items"]) <= 5


def test_decision_action_plan_endpoint():
    client = TestClient(app)
    response = client.get("/decision/riesgo-caida/action-plan?limit=5")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body


def test_dashboard_endpoint_returns_html():
    client = TestClient(app)
    response = client.get("/dashboard/riesgo-caida")
    assert response.status_code == 200
    assert "Decision Dashboard" in response.text
