from fastapi.testclient import TestClient

from api.main import app
from src.mlu.production import build_release_manifest, build_production_readiness
from src.mlu.security import require_api_key, role_capabilities
from src.mlu.feedback_store import feedback_store_schema


def test_release_manifest_has_version():
    manifest = build_release_manifest()
    assert manifest["version"] == "1.0.0"
    assert manifest["data_mode"] == "crm_first_demo_supported"


def test_readiness_report_has_checks():
    report = build_production_readiness()
    assert "checks" in report
    assert report["checks_total"] >= 5


def test_security_default_allows_local_without_key(monkeypatch):
    monkeypatch.delenv("MLU_AUTH_ENABLED", raising=False)
    assert require_api_key(None) is True


def test_security_rejects_wrong_key_when_enabled(monkeypatch):
    monkeypatch.setenv("MLU_AUTH_ENABLED", "true")
    monkeypatch.setenv("MLU_API_KEY", "secret")
    assert require_api_key("wrong") is False
    assert require_api_key("secret") is True


def test_role_capabilities_manager():
    caps = role_capabilities("manager")
    assert "dashboard" in caps["capabilities"]


def test_feedback_store_schema_contains_sql():
    schema = feedback_store_schema()
    assert "sql_path" in schema
    assert "columns" in schema


def test_production_endpoints():
    client = TestClient(app)
    for path in ["/production/health", "/metadata/release", "/metadata/production-readiness", "/feedback/store/schema"]:
        response = client.get(path)
        assert response.status_code == 200
