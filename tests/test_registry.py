import pandas as pd

from src.mlu.registry import dataframe_fingerprint, dataset_version_id, load_model_registry
from src.mlu.comparison import compare_registered_models, evaluate_predictions
from src.mlu.official_rules import FEATURE_COLUMNS, TARGET


def test_dataframe_fingerprint_is_stable():
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    assert dataframe_fingerprint(df) == dataframe_fingerprint(df.copy())


def test_dataset_version_id_has_expected_prefix():
    vid = dataset_version_id("riesgo_caida", "crm", 1, "2026-07-03T00:00:00+00:00")
    assert vid.startswith("dataset_riesgo_caida_crm_2026_07_03_v001")


def test_evaluate_predictions_returns_lift():
    metrics = evaluate_predictions([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9], threshold=0.4)
    assert metrics["recall"] == 1.0
    assert metrics["top_decile_lift"] >= 1.0


def test_model_registry_loads_even_when_empty():
    registry = load_model_registry()
    assert "models" in registry
