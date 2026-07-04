from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from src.mlu.decision_dashboard import load_public_dashboard_payload

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_script_module(script_name: str):
    path = PROJECT_ROOT / "scripts" / script_name
    spec = importlib.util.spec_from_file_location(script_name.replace(".py", ""), path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_public_payload_has_only_allowed_top_level_keys() -> None:
    exporter = load_script_module("69_export_public_dashboard_payload.py")
    ranking = exporter.read_ranking()
    payload = exporter.build_public_payload(ranking)
    assert set(payload.keys()) == exporter.ALLOWED_TOP_LEVEL_KEYS
    assert payload["data_mode"] == "crm"
    assert payload["total_operaciones"] > 0


def test_public_payload_does_not_contain_pii_terms() -> None:
    exporter = load_script_module("69_export_public_dashboard_payload.py")
    validator = load_script_module("70_validate_no_demo_data_in_production.py")
    payload = exporter.build_public_payload(exporter.read_ranking())
    result = validator.validate_public_payload(payload, environment="production")
    assert result["status"] == "ok"
    text = str(payload).lower()
    for forbidden in ["cliente", "documento", "email", "telefono", "teléfono", "nombre_completo", "password", "secret"]:
        assert forbidden not in text


def test_validator_rejects_demo_payload_in_production() -> None:
    validator = load_script_module("70_validate_no_demo_data_in_production.py")
    payload = {
        "total_operaciones": 1,
        "valor_total_en_riesgo": 1000,
        "riesgo_promedio": 0.5,
        "p0_p1": {"operaciones": 1, "valor_en_riesgo": 1000},
        "top_proyectos": [{"proyecto": "demo_project", "operaciones": 1}],
        "top_asesores": [],
        "top_canales": [],
        "fecha_generacion": "2026-07-03T00:00:00",
        "data_mode": "crm",
    }
    result = validator.validate_public_payload(payload, environment="production")
    assert result["status"] == "fail"


def test_validator_rejects_personal_data_key() -> None:
    validator = load_script_module("70_validate_no_demo_data_in_production.py")
    payload = {
        "total_operaciones": 1,
        "valor_total_en_riesgo": 1000,
        "riesgo_promedio": 0.5,
        "p0_p1": {"operaciones": 1, "valor_en_riesgo": 1000},
        "top_proyectos": [],
        "top_asesores": [],
        "top_canales": [],
        "fecha_generacion": "2026-07-03T00:00:00",
        "data_mode": "crm",
        "cliente": "Juan Perez",
    }
    result = validator.validate_public_payload(payload, environment="production")
    assert result["status"] == "fail"


def test_production_blocks_sample_fallback_when_public_payload_missing(tmp_path: Path) -> None:
    missing_payload = tmp_path / "missing_public_payload.json"
    with pytest.raises(RuntimeError, match="No hay payload CRM público disponible"):
        load_public_dashboard_payload(
            public_payload=missing_payload,
            environment="production",
            disable_sample_fallback=True,
        )
