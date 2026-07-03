from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .config import PROJECT_ROOT
from .comparison import compare_registered_models, select_best_challenger
from .registry import load_model_registry, load_dataset_registry

DEFAULT_POLICY = {
    "prediction_psi_gt": 0.25,
    "feature_drift_fail_count_gte": 3,
    "champion_max_age_days": 30,
    "min_new_feedback_rows": 100,
    "min_top_decile_lift": 1.20,
    "min_recall": 0.50,
}


def _parse_dt(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def load_monitoring_manifest(path: str | Path | None = None) -> dict:
    path = Path(path) if path else PROJECT_ROOT / "reports" / "monitoring" / "weekly_monitoring_manifest.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_retraining_policy(policy: dict | None = None, monitoring_manifest: dict | None = None, new_feedback_rows: int = 0) -> dict:
    policy = {**DEFAULT_POLICY, **(policy or {})}
    monitoring_manifest = monitoring_manifest if monitoring_manifest is not None else load_monitoring_manifest()
    reasons = []

    pred = monitoring_manifest.get("prediction_drift", {})
    feature = monitoring_manifest.get("feature_drift", {})
    prediction_psi = pred.get("prediction_psi")
    if prediction_psi is not None and float(prediction_psi) > float(policy["prediction_psi_gt"]):
        reasons.append(f"prediction_psi_gt_{policy['prediction_psi_gt']}")

    fail_count = feature.get("feature_status_counts", {}).get("fail", 0) or 0
    if int(fail_count) >= int(policy["feature_drift_fail_count_gte"]):
        reasons.append(f"feature_drift_fail_count_gte_{policy['feature_drift_fail_count_gte']}")

    if int(new_feedback_rows) >= int(policy["min_new_feedback_rows"]):
        reasons.append(f"new_feedback_rows_gte_{policy['min_new_feedback_rows']}")

    registry = load_model_registry()
    champion_id = registry.get("current_champion")
    champion = None
    for m in registry.get("models", []):
        if m.get("model_id") == champion_id:
            champion = m
            break
    if champion:
        champion_dt = _parse_dt(champion.get("champion_since") or champion.get("registered_at"))
        if champion_dt:
            age = (datetime.now(timezone.utc) - champion_dt).days
            if age > int(policy["champion_max_age_days"]):
                reasons.append(f"champion_age_days_gt_{policy['champion_max_age_days']}")

    comparison = compare_registered_models()
    best_challenger = select_best_challenger(min_recall=float(policy["min_recall"]))
    should_retrain = bool(reasons)
    should_promote = False
    promotion_candidate = None
    if best_challenger and champion:
        champ_score = champion.get("metrics", {}).get("top_decile_lift") or 0
        challenger_score = best_challenger.get("metrics", {}).get("top_decile_lift") or 0
        if challenger_score >= max(float(policy["min_top_decile_lift"]), champ_score):
            should_promote = True
            promotion_candidate = best_challenger.get("model_id")

    return {
        "status": "retraining_required" if should_retrain else "monitor",
        "should_retrain": should_retrain,
        "reasons": reasons,
        "should_promote_challenger": should_promote,
        "promotion_candidate": promotion_candidate,
        "current_champion": champion_id,
        "registered_models": len(registry.get("models", [])),
        "registered_datasets": len(load_dataset_registry().get("datasets", [])),
        "comparison_rows": int(len(comparison)),
    }
