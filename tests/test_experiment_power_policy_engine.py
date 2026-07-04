from pathlib import Path

import pandas as pd

from src.mlu.config import PROJECT_ROOT
from src.mlu.experiment_power_policy_engine import (
    COMPLIANCE_CSV,
    ESCALATION_POLICY_JSON,
    POWER_JSON,
    REPORT_MD,
    SEGMENT_IMPACT_CSV,
    SLA_RECOMMENDATIONS_JSON,
    VALIDATION_JSON,
    read_json,
    run_experiment_power_policy_engine,
)


def test_v19_policy_engine_runs_and_outputs_files():
    result = run_experiment_power_policy_engine()
    assert result["validation"]["status"] == "ok"
    for path in [POWER_JSON, COMPLIANCE_CSV, SEGMENT_IMPACT_CSV, SLA_RECOMMENDATIONS_JSON, ESCALATION_POLICY_JSON, REPORT_MD, VALIDATION_JSON]:
        assert path.exists(), path


def test_v19_power_analysis_has_policy_decision():
    if not POWER_JSON.exists():
        run_experiment_power_policy_engine()
    payload = read_json(POWER_JSON)
    assert payload["version"] == "v1.9_experiment_power_and_policy_engine"
    assert payload["required_n_per_arm"] > 0
    assert payload["decision"] in {"listo_para_politica", "seguir_acumulando_muestra_y_feedback"}


def test_v19_compliance_has_required_metrics():
    if not COMPLIANCE_CSV.exists():
        run_experiment_power_policy_engine()
    df = pd.read_csv(COMPLIANCE_CSV)
    metrics = set(df["metric"].astype(str))
    assert "treatment_contact_rate" in metrics
    assert "p0_treatment_coverage" in metrics
    assert "control_contamination_rate" in metrics
    assert "feedback_completion_30d" in metrics


def test_v19_outputs_do_not_expose_forbidden_columns():
    if not VALIDATION_JSON.exists():
        run_experiment_power_policy_engine()
    payload = read_json(VALIDATION_JSON)
    assert payload["status"] == "ok"
    forbidden = {"cliente", "dni", "documento", "telefono", "email", "codigo_proforma", "codigo_unidad"}
    for rel in ["data/processed/policy_engine/treatment_compliance_summary.csv", "data/processed/policy_engine/segment_policy_impact.csv"]:
        path = PROJECT_ROOT / rel
        df = pd.read_csv(path)
        assert not (set(map(str.lower, df.columns)) & forbidden)
