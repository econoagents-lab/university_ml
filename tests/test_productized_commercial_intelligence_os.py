from pathlib import Path

from src.mlu.config import PROJECT_ROOT
from src.mlu.productized_commercial_intelligence_os import (
    MANIFEST_JSON,
    VALIDATION_JSON,
    INDEX_HTML,
    run_productized_os_release,
)


def test_productized_os_release_generates_artifacts():
    """
    Yo verifico que v2.0 genere el manifiesto, la validación y el índice comercial.
    """
    result = run_productized_os_release()
    assert MANIFEST_JSON.exists()
    assert VALIDATION_JSON.exists()
    assert INDEX_HTML.exists()
    assert result["manifest"]["module_summary"]["total_modules"] >= 7


def test_productized_os_public_payload_has_no_forbidden_fields():
    """
    Yo protejo la demo pública contra campos personales o credenciales.
    """
    run_productized_os_release()
    import json
    payload = json.loads(VALIDATION_JSON.read_text(encoding="utf-8"))
    assert payload["status"] in {"ok", "warning"}
    assert payload.get("errors") == []


def test_productized_docs_exist():
    """
    Yo exijo documentos mínimos para vender y desplegar el producto.
    """
    docs = [
        PROJECT_ROOT / "docs" / "PRODUCTIZED_COMMERCIAL_INTELLIGENCE_OS.md",
        PROJECT_ROOT / "docs" / "SALES_DEMO_PLAYBOOK.md",
        PROJECT_ROOT / "docs" / "DEPLOYMENT_RUNBOOK_V2_0.md",
        PROJECT_ROOT / "docs" / "V2_0_EXECUTIVE_SUMMARY.md",
    ]
    assert all(path.exists() for path in docs)
