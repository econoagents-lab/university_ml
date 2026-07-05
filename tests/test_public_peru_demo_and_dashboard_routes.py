from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app
from src.mlu.dashboard_generator import generate_dashboards_from_catalog
from src.mlu.public_peru_demo import public_examples_metadata, run_public_peru_demo_build


def test_public_peru_examples_have_three_companies():
    payload = public_examples_metadata()
    assert payload["company_count"] == 3
    names = {item["company_name"] for item in payload["companies"]}
    assert {"Besco", "Edifica", "Paz Inmobiliaria"}.issubset(names)


def test_client_ready_landing_uses_public_peru_examples():
    run_public_peru_demo_build()
    client = TestClient(app)
    response = client.get("/demo/client-ready")
    assert response.status_code == 200
    text = response.text
    assert "Besco" in text
    assert "Edifica" in text
    assert "Paz Inmobiliaria" in text
    assert "ejemplos públicos" in text.lower()


def test_generated_dashboard_routes_do_not_return_not_found():
    generate_dashboards_from_catalog()
    client = TestClient(app)
    paths = [
        "/dashboard/catalog",
        "/dashboard/reports/generated_dashboards/executive/ceo_brief.html",
        "/dashboard/executive/ceo_brief.html",
    ]
    for path in paths:
        response = client.get(path)
        assert response.status_code == 200, response.text[:200]
        assert "Not Found" not in response.text
