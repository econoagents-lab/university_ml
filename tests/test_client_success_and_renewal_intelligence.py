from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app
from src.mlu.client_success_and_renewal_intelligence import (
    INDEX_HTML,
    MANIFEST_JSON,
    VALIDATION_JSON,
    get_client_success_package,
    run_client_success_and_renewal_intelligence,
)


def test_client_success_engine_generates_packages():
    result = run_client_success_and_renewal_intelligence()
    assert result["validation"]["status"] == "ok"
    assert result["validation"]["tenant_count"] >= 1
    assert INDEX_HTML.exists()
    assert MANIFEST_JSON.exists()
    assert VALIDATION_JSON.exists()


def test_client_success_package_has_required_fields():
    package = get_client_success_package("cliente_alpha")
    assert "health_snapshot" in package
    assert "renewal_plan" in package
    assert package["health_snapshot"]["health_band"] in {"green", "yellow", "red"}
    assert package["health_snapshot"]["churn_risk"] in {"low", "medium", "high"}


def test_client_success_outputs_do_not_expose_forbidden_terms():
    run_client_success_and_renewal_intelligence()
    forbidden = ["dni", "documento", "telefono", "teléfono", "email", "codigo_proforma", "codigo_unidad", "password", "secret"]
    public_files = list(Path("reports/client_success").rglob("*.md")) + list(Path("reports/client_success").rglob("*.html")) + list(Path("reports/client_success").rglob("*.json"))
    text = "\n".join(path.read_text(encoding="utf-8", errors="ignore").lower() for path in public_files)
    assert not any(term in text for term in forbidden)


def test_client_success_api_endpoints():
    run_client_success_and_renewal_intelligence()
    client = TestClient(app)
    assert client.get("/metadata/client-success").status_code == 200
    assert client.get("/success/clients").status_code == 200
    assert client.get("/success/client/cliente_alpha/health").status_code == 200
    assert client.get("/success/client/cliente_alpha/renewal-plan").status_code == 200
    assert client.get("/success/client/cliente_alpha/package").status_code == 200
