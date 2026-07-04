from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app
from src.mlu.client_proposal_and_contract_automation import (
    INDEX_HTML,
    MANIFEST_JSON,
    VALIDATION_JSON,
    get_client_proposal_package,
    run_client_proposal_and_contract_automation,
)


def test_client_proposals_generate_and_validate():
    result = run_client_proposal_and_contract_automation()
    assert result["validation"]["status"] == "ok"
    assert MANIFEST_JSON.exists()
    assert VALIDATION_JSON.exists()
    assert INDEX_HTML.exists()
    assert result["manifest"]["tenant_count"] >= 1


def test_client_proposal_package_contains_scope_price_and_contract():
    package = get_client_proposal_package("cliente_alpha")
    assert package["recommended_package"]
    assert package["pricing"]["year_one_total"] >= package["pricing"]["net_setup_fee"]
    assert "metric_contract" in package["artifacts"]
    assert "scope" in package["artifacts"]


def test_client_proposal_api_endpoints():
    client = TestClient(app)
    meta = client.get("/metadata/client-proposals")
    assert meta.status_code == 200
    index = client.get("/proposals/clients")
    assert index.status_code == 200
    proposal = client.get("/proposal/client/cliente_alpha")
    assert proposal.status_code == 200
    package = client.get("/proposal/client/cliente_alpha/package")
    assert package.status_code == 200
    assert package.json()["tenant_id"] == "cliente_alpha"
