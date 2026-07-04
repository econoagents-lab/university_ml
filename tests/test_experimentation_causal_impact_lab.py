from pathlib import Path
import json
import pandas as pd

from src.mlu.experimentation_causal_impact_lab import (
    ASSIGNMENT_CSV,
    CONFIG_PATH,
    IMPACT_SUMMARY_CSV,
    IMPACT_SUMMARY_JSON,
    OUTCOMES_SAFE_CSV,
    REPORT_MD,
    VALIDATION_JSON,
    run_experimentation_causal_impact_lab,
)


def test_v18_runs_and_creates_artifacts():
    result = run_experimentation_causal_impact_lab()
    assert CONFIG_PATH.exists()
    assert ASSIGNMENT_CSV.exists()
    assert OUTCOMES_SAFE_CSV.exists()
    assert IMPACT_SUMMARY_CSV.exists()
    assert IMPACT_SUMMARY_JSON.exists()
    assert REPORT_MD.exists()
    assert result["validation"]["status"] == "ok"


def test_assignment_has_treatment_or_safe_empty():
    run_experimentation_causal_impact_lab()
    df = pd.read_csv(ASSIGNMENT_CSV)
    assert "experiment_arm" in df.columns
    assert "operation_id" in df.columns
    assert not {"cliente", "documento", "dni", "telefono", "email", "codigo_proforma", "codigo_unidad"}.intersection({c.lower() for c in df.columns})
    if len(df):
        assert set(df["experiment_arm"].unique()).issubset({"treatment", "control", "not_eligible"})


def test_impact_summary_has_delta_row():
    run_experimentation_causal_impact_lab()
    df = pd.read_csv(IMPACT_SUMMARY_CSV)
    assert "experiment_arm" in df.columns
    assert "impact_delta" in set(df["experiment_arm"].astype(str))
    payload = json.loads(Path(IMPACT_SUMMARY_JSON).read_text(encoding="utf-8"))
    assert "saved_value_proxy" in payload
    assert payload["status"] in {"estimated", "needs_more_feedback"}


def test_no_pii_validation_file_ok():
    run_experimentation_causal_impact_lab()
    payload = json.loads(Path(VALIDATION_JSON).read_text(encoding="utf-8"))
    assert payload["status"] == "ok"
