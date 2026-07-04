from pathlib import Path

from src.mlu.config import PROJECT_ROOT
from src.mlu.dashboard_metrics_engine import (
    build_family_metrics,
    metrics_for_dashboard,
    validate_dashboard_metrics,
    FAMILY_METRICS_JSON,
    ENGINE_REPORT_MD,
)
from src.mlu.dashboard_generator import generate_dashboards_from_catalog, validate_generated_dashboards


def test_dashboard_metrics_engine_builds_required_families():
    bundle = build_family_metrics()
    families = bundle["families"]
    for key in ["funnel", "risk", "stock_pricing", "cobranza", "rag", "mlops"]:
        assert key in families
        assert "decision" in families[key]
    assert FAMILY_METRICS_JSON.exists()
    assert ENGINE_REPORT_MD.exists()


def test_dashboard_metrics_validation_is_ok():
    build_family_metrics()
    validation = validate_dashboard_metrics()
    assert validation["status"] == "ok"


def test_metrics_for_dashboard_routes_to_specific_family():
    risk = metrics_for_dashboard("riesgo_caida", "risk")
    rag = metrics_for_dashboard("rag_quality", "rag")
    mlops = metrics_for_dashboard("drift_monitoring", "monitoring")
    assert risk["metric_group"] == "risk"
    assert rag["metric_group"] == "rag"
    assert mlops["metric_group"] == "mlops"


def test_generated_dashboards_include_family_metrics():
    build_family_metrics()
    manifest = generate_dashboards_from_catalog()
    validation = validate_generated_dashboards()
    assert manifest["total_generated"] >= 60
    assert validation["status"] == "ok"
    sample_json = PROJECT_ROOT / "reports" / "generated_dashboards" / "risk" / "riesgo_caida.json"
    assert sample_json.exists()
    assert "family_metrics" in sample_json.read_text(encoding="utf-8")
