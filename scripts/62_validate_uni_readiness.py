from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "alert_thresholds.yml"
DEFAULT_OUTPUT_DIR = ROOT / "reports" / "alerts"


def load_yaml(path: Path) -> dict[str, Any]:
    """Yo cargo los requisitos esperados para validar si el entregable UNI está defendible."""
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}


def contains_terms(path: Path, terms: list[str]) -> tuple[list[str], list[str]]:
    """Yo verifico que un documento contenga términos mínimos de trazabilidad."""
    if not path.exists():
        return [], terms
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    present = [term for term in terms if term.lower() in text]
    missing = [term for term in terms if term.lower() not in text]
    return present, missing


def validate_readiness(config_path: Path = DEFAULT_CONFIG, output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    """Yo valido archivos, trazabilidad y reporte técnico antes de presentar el trabajo final."""
    cfg = load_yaml(config_path).get("uni_readiness", {})
    output_dir.mkdir(parents=True, exist_ok=True)
    required_files = cfg.get("required_files", [])
    missing_files = [file for file in required_files if not (ROOT / file).exists()]

    trace_path = ROOT / "docs" / "TRACEABILITY_TABLE_UNI.md"
    report_path = ROOT / "reports" / "uni_final" / "FINAL_TECHNICAL_REPORT.md"
    trace_present, trace_missing = contains_terms(trace_path, cfg.get("traceability_required_terms", []))
    report_present, report_missing = contains_terms(report_path, cfg.get("final_report_required_terms", []))

    severity = "ok"
    reasons: list[str] = []
    if missing_files:
        severity = "critical"
        reasons.append(f"Faltan archivos obligatorios: {missing_files}")
    if trace_missing:
        severity = "warning" if severity == "ok" else severity
        reasons.append(f"La trazabilidad no menciona: {trace_missing}")
    if report_missing:
        severity = "warning" if severity == "ok" else severity
        reasons.append(f"El reporte final no menciona: {report_missing}")
    if not reasons:
        reasons.append("El paquete UNI tiene los archivos y términos mínimos esperados.")

    payload = {
        "severity": severity,
        "missing_files": missing_files,
        "traceability_present_terms": trace_present,
        "traceability_missing_terms": trace_missing,
        "final_report_present_terms": report_present,
        "final_report_missing_terms": report_missing,
        "reasons": reasons,
    }
    write_outputs(payload, output_dir)
    return payload


def write_outputs(payload: dict[str, Any], output_dir: Path) -> None:
    """Yo escribo una alerta Markdown legible dentro de reports/alerts."""
    icon = {"ok": "✅", "warning": "⚠️", "critical": "🚨"}.get(payload.get("severity"), "ℹ️")
    lines = [
        f"# {icon} UNI Delivery Readiness",
        "",
        f"- Severidad: **{payload.get('severity', 'ok').upper()}**",
        "",
        "## Lectura",
    ]
    for reason in payload.get("reasons", []):
        lines.append(f"- {reason}")
    lines.extend([
        "",
        "## Acción recomendada",
        "Yo completaría primero la trazabilidad y después actualizaría el reporte final antes de exponer.",
    ])
    (output_dir / "UNI_READINESS_ALERT.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "UNI_READINESS_ALERT.md").write_text("\n".join(lines), encoding="utf-8")
    (output_dir / "UNI_READINESS_ISSUE_BODY.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--fail-on-critical", action="store_true")
    args = parser.parse_args()
    payload = validate_readiness(Path(args.config), Path(args.output_dir))
    print(f"Readiness generado en {Path(args.output_dir) / 'UNI_READINESS_ALERT.md'}")
    if args.fail_on_critical and payload.get("severity") == "critical":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
