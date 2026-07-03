from __future__ import annotations

from pathlib import Path
import json
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "monitoring"
EXEC_DIR = ROOT / "reports" / "executive"

STEPS = [
    "22_monitor_feature_drift.py",
    "23_monitor_prediction_drift.py",
    "24_evaluate_calibration.py",
    "25_create_experiment_plan.py",
    "26_analyze_intervention_effect.py",
    "27_export_feedback_store_schema.py",
]


def run_step(script: str) -> dict:
    cmd = [sys.executable, str(ROOT / "scripts" / script)]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return {
        "script": script,
        "returncode": int(proc.returncode),
        "status": "ok" if proc.returncode == 0 else "fail",
        "stdout_tail": proc.stdout[-1500:],
        "stderr_tail": proc.stderr[-1500:],
    }


def main() -> None:
    EXEC_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    results = [run_step(step) for step in STEPS]
    # Read summaries if they exist
    feature_summary = json.loads((REPORT_DIR / "feature_drift_summary.json").read_text(encoding="utf-8")) if (REPORT_DIR / "feature_drift_summary.json").exists() else {}
    prediction_summary = json.loads((REPORT_DIR / "prediction_drift.json").read_text(encoding="utf-8")) if (REPORT_DIR / "prediction_drift.json").exists() else {}
    calibration_summary = json.loads((REPORT_DIR / "calibration_summary.json").read_text(encoding="utf-8")) if (REPORT_DIR / "calibration_summary.json").exists() else {}
    global_status = feature_summary.get("global_status", "unknown")
    if prediction_summary.get("status") == "fail":
        global_status = "fail"
    elif prediction_summary.get("status") == "warning" and global_status == "ok":
        global_status = "warning"
    manifest = {
        "version": "0.7.0-monitoring_and_experiments",
        "global_status": global_status,
        "steps": results,
        "feature_drift": feature_summary,
        "prediction_drift": prediction_summary,
        "calibration": calibration_summary,
    }
    (REPORT_DIR / "weekly_monitoring_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    md = "# Weekly Monitoring Report - Riesgo de Caída v0.7\n\n"
    md += f"Estado global: **{global_status}**\n\n"
    md += "## Lectura ejecutiva\n\n"
    if global_status == "ok":
        md += "El ranking puede usarse operativamente con monitoreo normal.\n\n"
    elif global_status == "warning":
        md += "El ranking puede usarse con revisión humana. Revisar drift y calibración.\n\n"
    else:
        md += "No usar el ranking como prioridad fuerte hasta auditar drift/fuentes o reentrenar.\n\n"
    md += "## Steps\n\n| Script | Estado |\n|---|---|\n"
    for r in results:
        md += f"| {r['script']} | {r['status']} |\n"
    md += "\n## Feature drift\n\n```json\n" + json.dumps(feature_summary, indent=2, ensure_ascii=False) + "\n```\n"
    md += "\n## Prediction drift\n\n```json\n" + json.dumps(prediction_summary, indent=2, ensure_ascii=False) + "\n```\n"
    md += "\n## Calibration\n\n```json\n" + json.dumps(calibration_summary, indent=2, ensure_ascii=False) + "\n```\n"
    (EXEC_DIR / "WEEKLY_MONITORING_REPORT.md").write_text(md, encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
