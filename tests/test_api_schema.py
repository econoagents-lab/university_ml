from fastapi.testclient import TestClient
from api.main import app


def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_predict_endpoint():
    client = TestClient(app)
    payload = {
        "proyecto": "Proyecto Aurora",
        "asesor": "Asesor Norte",
        "medio_captacion": "facebook",
        "precio_departamento": 620000,
        "dias_en_tuberia": 45,
        "dormitorios": 3,
        "tiene_cuota_inicial": False,
        "cambios_unidad": 1,
        "interacciones_ult_7d": 0,
        "descuento_pct": 0.03
    }
    response = client.post("/predict/riesgo-caida", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["riesgo_caida"] <= 1
    assert "decision_recomendada" in body
