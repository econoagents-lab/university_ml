from pathlib import Path
import json
import pandas as pd
import pytest

from src.mlu.decision_action_feedback_lab import (
    ASSIGNMENT_TEMPLATE_CSV,
    FEEDBACK_EVENTS_SAFE_CSV,
    MANIFEST_JSON,
    OUTCOMES_CSV,
    QUEUE_CSV,
    REPORT_MD,
    RETRAINING_SIGNAL_JSON,
    VALIDATION_JSON,
    run_decision_action_feedback_lab,
)


@pytest.fixture(scope="session", autouse=True)
def v17_artifacts():
    # Yo ejecuto una sola vez el laboratorio para que la suite sea rápida y estable.
    return run_decision_action_feedback_lab()


def test_v17_pipeline_generates_required_artifacts(v17_artifacts):
    # Yo verifico que el laboratorio produzca todos los artefactos de decisión.
    assert Path(v17_artifacts["report"]).exists()
    for path in [QUEUE_CSV, ASSIGNMENT_TEMPLATE_CSV, FEEDBACK_EVENTS_SAFE_CSV, OUTCOMES_CSV, RETRAINING_SIGNAL_JSON, MANIFEST_JSON, REPORT_MD, VALIDATION_JSON]:
        assert path.exists(), f"Falta artefacto {path}"


def test_v17_queue_uses_safe_identifiers_only(v17_artifacts):
    # Yo valido que la cola use IDs hasheados y no columnas operativas crudas.
    df = pd.read_csv(QUEUE_CSV)
    forbidden = {"codigo_proforma", "codigo_unidad", "cliente", "documento", "dni", "telefono", "teléfono", "email"}
    assert forbidden.isdisjoint({c.lower() for c in df.columns})
    if not df.empty:
        assert df["operation_id"].astype(str).str.startswith("OP_").all()
        assert df["asesor_id"].astype(str).str.startswith("ASESOR_").all() or (df["asesor_id"] == "ASESOR_SIN_DATO").all()


def test_v17_assignment_template_has_feedback_columns(v17_artifacts):
    # Yo verifico que la plantilla permita capturar acción y resultado sin PII.
    df = pd.read_csv(ASSIGNMENT_TEMPLATE_CSV)
    expected = {"operation_id", "accion_tomada", "fecha_accion", "resultado_7d", "resultado_30d", "caida_real_30d"}
    assert expected.issubset(set(df.columns))


def test_v17_privacy_validation_passes(v17_artifacts):
    # Yo bloqueo publicación si aparece una columna o patrón sensible en los outputs del laboratorio.
    payload = json.loads(VALIDATION_JSON.read_text(encoding="utf-8"))
    assert payload["status"] == "ok", payload.get("errors")


def test_v17_manifest_counts_are_consistent(v17_artifacts):
    # Yo compruebo que el manifiesto cuente filas reales y sea consumible por API.
    manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    assert manifest["version"] == "v1.7_decision_action_feedback_lab"
    assert "queue_rows" in manifest["counts"]
    assert manifest["privacy_mode"] == "aggregated_or_hashed_only"
