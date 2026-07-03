from pathlib import Path
import importlib.util
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load_module(relative_path: str, name: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_commercial_digest_generates_outputs(tmp_path):
    module = load_module("scripts/61_build_commercial_alert_digest.py", "commercial_digest")
    ranking = ROOT / "data" / "processed" / "scoring" / "ranking_operaciones_riesgo_caida.csv"
    assert ranking.exists()
    payload = module.build_digest(output_dir=tmp_path)
    assert payload["total_operations"] > 0
    assert (tmp_path / "EXECUTIVE_KPI_DIGEST.md").exists()
    assert (tmp_path / "EXECUTIVE_KPI_DIGEST.json").exists()


def test_ragas_gate_reads_metrics(tmp_path):
    module = load_module("scripts/63_validate_ragas_quality_gate.py", "ragas_gate")
    payload = module.validate_ragas(output_dir=tmp_path)
    assert "metrics" in payload
    assert "faithfulness_proxy_mean" in payload["metrics"]
    assert (tmp_path / "RAGAS_ALERT.md").exists()


def test_uni_readiness_generates_alert(tmp_path):
    module = load_module("scripts/62_validate_uni_readiness.py", "uni_readiness")
    payload = module.validate_readiness(output_dir=tmp_path)
    assert payload["severity"] in {"ok", "warning", "critical"}
    assert (tmp_path / "UNI_READINESS_ALERT.md").exists()


def test_issue_body_consolidates_alerts(tmp_path):
    alerts = tmp_path / "alerts"
    alerts.mkdir(parents=True, exist_ok=True)
    (alerts / "EXECUTIVE_KPI_DIGEST.json").write_text(json.dumps({"severity": "ok", "alert_reasons": ["test"]}), encoding="utf-8")
    (alerts / "RAGAS_ALERT.json").write_text(json.dumps({"severity": "warning", "recommendation": "test"}), encoding="utf-8")
    (alerts / "UNI_READINESS_ALERT.json").write_text(json.dumps({"severity": "ok", "reasons": ["test"]}), encoding="utf-8")
    module = load_module("scripts/64_create_alert_issue_body.py", "issue_body")
    module.ALERTS_DIR = alerts
    output = tmp_path / "issue.md"
    body = module.build_issue_body(output_path=output)
    assert "Intelligence Factory Alert" in body
    assert output.exists()


def test_alert_thresholds_config_exists():
    assert (ROOT / "config" / "alert_thresholds.yml").exists()
