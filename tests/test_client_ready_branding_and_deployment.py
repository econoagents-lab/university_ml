from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app
from src.mlu.client_ready_branding_and_deployment import (
    LANDING_HTML,
    MANIFEST_JSON,
    VALIDATION_JSON,
    run_client_ready_branding_and_deployment,
    validate_demo_token,
)


def test_v21_generates_client_ready_artifacts():
    result = run_client_ready_branding_and_deployment()
    assert result["validation"]["status"] in {"ok", "warning"}
    assert LANDING_HTML.exists()
    assert MANIFEST_JSON.exists()
    assert VALIDATION_JSON.exists()
    assert "Tu primera área" in LANDING_HTML.read_text(encoding="utf-8")


def test_v21_demo_auth_open_by_default_locally(monkeypatch):
    monkeypatch.delenv("MLU_DEMO_AUTH_ENABLED", raising=False)
    monkeypatch.delenv("MLU_DEMO_TOKEN", raising=False)
    assert validate_demo_token(None) is True


def test_v21_api_endpoints():
    run_client_ready_branding_and_deployment()
    client = TestClient(app)
    metadata = client.get("/metadata/client-ready")
    assert metadata.status_code == 200
    assert "manifest" in metadata.json()
    html_response = client.get("/demo/client-ready")
    assert html_response.status_code == 200
    assert "Commercial Intelligence" in html_response.text or "inteligencia comercial" in html_response.text.lower()
