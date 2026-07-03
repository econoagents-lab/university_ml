from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]
ALERTS_DIR = ROOT / "reports" / "alerts"


def load_json(path: Path) -> dict[str, Any]:
    """Yo cargo un payload de alerta si existe; si no existe, devuelvo un objeto vacío."""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_issue_body(alert_type: str = "all", output_path: Path = ALERTS_DIR / "ALERT_ISSUE_BODY.md") -> str:
    """Yo consolido alertas en un único cuerpo de issue accionable."""
    commercial = load_json(ALERTS_DIR / "EXECUTIVE_KPI_DIGEST.json")
    ragas = load_json(ALERTS_DIR / "RAGAS_ALERT.json")
    uni = load_json(ALERTS_DIR / "UNI_READINESS_ALERT.json")

    sections = [
        "# 🚨 Intelligence Factory Alert",
        "",
        "Yo convierto una señal automática en una tarea concreta para cerrar el siguiente ciclo de mejora.",
        "",
    ]
    if alert_type in {"all", "commercial"}:
        sections.extend(section("Commercial KPI Digest", commercial))
    if alert_type in {"all", "ragas"}:
        sections.extend(section("RAG Quality Gate", ragas))
    if alert_type in {"all", "uni"}:
        sections.extend(section("UNI Readiness", uni))

    sections.extend([
        "## Checklist de cierre",
        "- [ ] Revisé el reporte en `reports/alerts/`.",
        "- [ ] Identifiqué si el problema es dato, modelo, RAG, prompt o entrega.",
        "- [ ] Definí una acción, responsable y fecha límite.",
    ])
    body = "\n".join(sections)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(body, encoding="utf-8")
    return body


def section(title: str, payload: dict[str, Any]) -> list[str]:
    """Yo traduzco un payload JSON en una sección Markdown corta para GitHub Issues."""
    severity = payload.get("severity", "not_run") if payload else "not_run"
    lines = [f"## {title}", f"- Severidad: **{severity.upper()}**"]
    if not payload:
        lines.append("- No encontré payload generado para esta alerta.")
    elif "alert_reasons" in payload:
        for reason in payload.get("alert_reasons", []):
            lines.append(f"- {reason}")
    elif "reasons" in payload:
        for reason in payload.get("reasons", []):
            lines.append(f"- {reason}")
    elif "recommendation" in payload:
        lines.append(f"- {payload.get('recommendation')}")
    lines.append("")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alert-type", default="all", choices=["all", "commercial", "ragas", "uni"])
    parser.add_argument("--output", default=str(ALERTS_DIR / "ALERT_ISSUE_BODY.md"))
    args = parser.parse_args()
    body = build_issue_body(args.alert_type, Path(args.output))
    print(body)


if __name__ == "__main__":
    main()
