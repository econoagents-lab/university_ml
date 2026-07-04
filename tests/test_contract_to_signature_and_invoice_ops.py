from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app
from src.mlu.contract_to_signature_and_invoice_ops import REPORT_DIR, run_contract_to_signature_and_invoice_ops, get_contract_ops_package


def test_contract_ops_generates_required_artifacts():
    manifest = run_contract_to_signature_and_invoice_ops()
    assert manifest["status"] == "ok"
    assert manifest["tenant_count"] >= 1
    assert (REPORT_DIR / "contract_ops_index.html").exists()
    assert (REPORT_DIR / "CONTRACT_OPS_INDEX.md").exists()


def test_contract_ops_package_has_invoice_and_work_order():
    manifest = run_contract_to_signature_and_invoice_ops()
    tenant_id = manifest["tenants"][0]["tenant_id"]
    package = get_contract_ops_package(tenant_id)
    assert package["work_order"]["work_order_id"].startswith("WO-")
    assert package["invoice_proforma"]["invoice_id"]
    assert package["invoice_proforma"]["total"] >= 0


def test_contract_ops_outputs_do_not_include_forbidden_crm_fields():
    run_contract_to_signature_and_invoice_ops()
    forbidden = ["dni", "telefono", "teléfono", "email", "codigo_proforma", "codigo_unidad", "redshift_password"]
    for path in REPORT_DIR.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".json", ".md", ".html", ".csv"}:
            text = path.read_text(encoding="utf-8").lower()
            assert not any(term in text for term in forbidden), f"Forbidden term in {path}"


def test_contract_ops_api_endpoints():
    run_contract_to_signature_and_invoice_ops()
    client = TestClient(app)
    response = client.get("/metadata/contract-ops")
    assert response.status_code == 200
    tenant_id = response.json()["tenants"][0]["tenant_id"]
    assert client.get("/contracts/ops/clients").status_code == 200
    assert client.get(f"/contract/client/{tenant_id}/work-order").status_code == 200
    assert client.get(f"/contract/client/{tenant_id}/invoice").status_code == 200
    assert client.get(f"/contract/client/{tenant_id}/ops-package").status_code == 200
