from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "alert_thresholds.yml"
DEFAULT_OUTPUT_DIR = ROOT / "reports" / "alerts"

METRIC_PATTERN = re.compile(r"\*\*([a-zA-Z0-9_]+):\*\*\s*([0-9.]+)")


def load_yaml(path: Path) -> dict[str, Any]:
    """Yo cargo los umbrales RAGAS-like para decidir si la demo es confiable."""
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}


def parse_metrics(path: Path) -> dict[str, float]:
    """Yo leo métricas desde Markdown sin depender de un formato rígido de tabla."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="ignore")
    return {name: float(value) for name, value in METRIC_PATTERN.findall(text)}


def validate_ragas(config_path: Path = DEFAULT_CONFIG, output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    """Yo comparo RAGAS-like contra umbrales para proteger la demo de respuestas débiles."""
    cfg_all = load_yaml(config_path)
    cfg = cfg_all.get("rag_quality", {})
    summary_path = ROOT / cfg.get("summary_path", "reports/uni_final/RAGAS_LIKE_SUMMARY.md")
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics = parse_metrics(summary_path)

    checks = []
    severity = "ok"
    for metric_name, threshold in cfg.items():
        if not metric_name.endswith("_min"):
            continue
        metric = metric_name[:-4]
        actual = metrics.get(metric)
        passed = actual is not None and actual >= float(threshold)
        checks.append({"metric": metric, "actual": actual, "min": float(threshold), "passed": bool(passed)})
        if not passed:
            severity = "warning"

    if not metrics:
        severity = "critical"
        checks.append({"metric": "summary", "actual": None, "min": None, "passed": False, "reason": "No pude leer métricas."})

    payload = {
        "severity": severity,
        "summary_path": summary_path.as_posix(),
        "metrics": metrics,
        "checks": checks,
        "recommendation": build_recommendation(severity, checks),
    }
    write_outputs(payload, output_dir)
    return payload


def build_recommendation(severity: str, checks: list[dict[str, Any]]) -> str:
    """Yo traduzco métricas RAG en una acción que pueda ejecutar antes de presentar."""
    failed = [check for check in checks if not check.get("passed")]
    if severity == "ok":
        return "Yo presentaría la demo porque las métricas superan los umbrales mínimos configurados."
    names = ", ".join(check.get("metric", "") for check in failed)
    return f"Yo revisaría recuperación, citas y preguntas trampa antes de presentar. Métricas débiles: {names}."


def write_outputs(payload: dict[str, Any], output_dir: Path) -> None:
    """Yo escribo el gate RAG en Markdown, JSON e issue body."""
    icon = {"ok": "✅", "warning": "⚠️", "critical": "🚨"}.get(payload.get("severity"), "ℹ️")
    lines = [
        f"# {icon} RAG Quality Gate",
        "",
        f"- Severidad: **{payload.get('severity', 'ok').upper()}**",
        f"- Fuente: `{payload.get('summary_path')}`",
        "",
        "## Checks",
    ]
    for check in payload.get("checks", []):
        mark = "✅" if check.get("passed") else "❌"
        lines.append(f"- {mark} `{check.get('metric')}` = {check.get('actual')} | mínimo = {check.get('min')}")
    lines.extend(["", "## Recomendación", payload.get("recommendation", "")])
    (output_dir / "RAGAS_ALERT.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "RAGAS_ALERT.md").write_text("\n".join(lines), encoding="utf-8")
    (output_dir / "RAGAS_ISSUE_BODY.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--fail-on-alert", action="store_true")
    args = parser.parse_args()
    payload = validate_ragas(Path(args.config), Path(args.output_dir))
    print(f"RAGAS gate generado en {Path(args.output_dir) / 'RAGAS_ALERT.md'}")
    if args.fail_on_alert and payload.get("severity") != "ok":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
