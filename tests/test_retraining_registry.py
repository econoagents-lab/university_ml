from src.mlu.retraining import evaluate_retraining_policy


def test_retraining_policy_flags_prediction_drift():
    manifest = {
        "prediction_drift": {"prediction_psi": 0.9},
        "feature_drift": {"feature_status_counts": {"fail": 0}},
    }
    result = evaluate_retraining_policy(monitoring_manifest=manifest)
    assert result["should_retrain"] is True
    assert any("prediction_psi" in r for r in result["reasons"])


def test_retraining_policy_can_monitor_when_no_drift():
    manifest = {
        "prediction_drift": {"prediction_psi": 0.01},
        "feature_drift": {"feature_status_counts": {"fail": 0}},
    }
    result = evaluate_retraining_policy(monitoring_manifest=manifest)
    assert result["status"] in {"monitor", "retraining_required"}
    assert "registered_models" in result
