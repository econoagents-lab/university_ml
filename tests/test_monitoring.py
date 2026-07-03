import numpy as np
import pandas as pd

from src.mlu.monitoring import population_stability_index, compute_feature_drift, compute_prediction_drift


def test_population_stability_index_zero_for_same_distribution():
    s = pd.Series([1, 2, 3, 4, 5] * 10)
    psi = population_stability_index(s, s)
    assert psi < 0.001


def test_feature_drift_flags_shift():
    ref = pd.DataFrame({"precio_departamento": np.arange(100, 200), "proyecto": ["A"] * 100})
    cur = pd.DataFrame({"precio_departamento": np.arange(1000, 1100), "proyecto": ["B"] * 100})
    drift = compute_feature_drift(ref, cur, ["precio_departamento", "proyecto"], threshold_warning=0.01, threshold_fail=0.02)
    assert set(drift["status"]) <= {"ok", "warning", "fail", "missing", "unknown"}
    assert (drift["status"] == "fail").any()


def test_prediction_drift_returns_status():
    ref = pd.Series(np.linspace(0.01, 0.20, 100))
    cur = pd.Series(np.linspace(0.70, 0.95, 100))
    result = compute_prediction_drift(ref, cur, threshold_warning=0.01, threshold_fail=0.02)
    assert result["status"] == "fail"
    assert result["prediction_psi"] > 0
