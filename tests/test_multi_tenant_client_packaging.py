from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app
from src.mlu.config import PROJECT_ROOT
from src.mlu.multi_tenant_client_packaging import (
    MANIFEST_JSON,
    VALIDATION_JSON,
    build_all_tenant_packages,
    get_tenant_package,
    validate_multi_tenant_packaging,
)


def test_build_all_tenant_packages_creates_artifacts():
    manifest = build_all_tenant_packages()
    assert manifest["tenant_count"] >= 3
    assert manifest["status"] == "ok"
    for tenant in manifest["tenants"]:
        for rel_path in tenant["artifact_paths"].values():
            assert (PROJECT_ROOT / rel_path).exists()
        assert tenant["privacy_status"] == "ok"


def test_validate_multi_tenant_packaging_ok():
    build_all_tenant_packages()
    validation = validate_multi_tenant_packaging()
    assert validation["status"] == "ok"
    assert MANIFEST_JSON.exists()
    assert VALIDATION_JSON.exists()


def test_payloads_do_not_expose_forbidden_fields():
    manifest = build_all_tenant_packages()
    forbidden = ["cliente", "documento", "dni", "email", "telefono", "teléfono", "direccion", "dirección", "codigo_proforma", "codigo_unidad", "credenciales"]
    for tenant in manifest["tenants"]:
        payload_path = PROJECT_ROOT / tenant["artifact_paths"]["payload"]
        text = payload_path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert f'"{token}"' not in text


def test_get_tenant_package():
    build_all_tenant_packages()
    package = get_tenant_package("cliente_alpha")
    assert package["tenant_id"] == "cliente_alpha"
    assert package["privacy_status"] == "ok"


def test_api_multi_tenant_endpoints():
    build_all_tenant_packages()
    client = TestClient(app)
    meta = client.get("/metadata/client-tenants")
    assert meta.status_code == 200
    assert meta.json()["tenant_count"] >= 3
    index = client.get("/demo/tenants")
    assert index.status_code == 200
    tenant = client.get("/product/client/cliente_alpha/package")
    assert tenant.status_code == 200
    landing = client.get("/demo/client/cliente_alpha")
    assert landing.status_code == 200
