from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json
import sys

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "alert_thresholds.yml"
DEFAULT_OUTPUT_DIR = ROOT / "reports" / "alerts"


def load_yaml(path: Path) -> dict[str, Any]:
    """Yo cargo la configuración de umbrales para separar señales normales de alertas comerciales."""
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Yo busco una columna usando varios alias porque mis outputs cambian entre versiones."""
    normalized = {str(column).lower().strip(): column for column in df.columns}
    for candidate in candidates:
        key = candidate.lower().strip()
        if key in normalized:
            return normalized[key]
    return None


def detect_priority_column(df: pd.DataFrame) -> str | None:
    """Yo detecto la columna de prioridad comercial para contar P0, P1, P2 y P3."""
    return find_column(df, [
        "prioridad", "priority", "nivel_prioridad", "decision_priority", "prioridad_comercial",
        "nivel", "risk_level", "nivel_riesgo",
    ])


def normalize_priority(value: Any) -> str:
    """Yo normalizo textos de prioridad para que 'P0 intervenir hoy' y 'P0' cuenten juntos."""
    text = str(value).strip()
    upper = text.upper()
    if upper.startswith("P0") or "INTERVENIR HOY" in upper:
        return "P0"
    if upper.startswith("P1") or "24" in upper:
        return "P1"
    if upper.startswith("P2") or "72" in upper:
        return "P2"
    if upper.startswith("P3") or "MONITOREO" in upper:
        return "P3"
    if not text or text.lower() == "nan":
        return "Sin prioridad"
    return text


def numeric_series(df: pd.DataFrame, candidates: list[str]) -> tuple[str | None, pd.Series | None]:
    """Yo convierto una columna numérica aunque venga con símbolos de moneda o separadores."""
    column = find_column(df, candidates)
    if column is None:
        return None, None
    series = df[column]
    if not pd.api.types.is_numeric_dtype(series):
        series = (
            series.astype(str)
            .str.replace("S/", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.replace("%", "", regex=False)
            .str.strip()
        )
    return column, pd.to_numeric(series, errors="coerce")


def top_dimension(df: pd.DataFrame, dimension_candidates: list[str], value_column: str | None, top_n: int) -> list[dict[str, Any]]:
    """Yo agrupo por proyecto o asesor para que el digest diga dónde concentrar la atención."""
    dimension = find_column(df, dimension_candidates)
    if dimension is None:
        return []
    grouped = df.groupby(dimension, dropna=False).size().reset_index(name="operaciones")
    if value_column is not None and value_column in df.columns:
        values = pd.to_numeric(df[value_column], errors="coerce").fillna(0)
        temp = df.copy()
        temp[value_column] = values
        sums = temp.groupby(dimension, dropna=False)[value_column].sum().reset_index(name="valor_esperado_en_riesgo")
        grouped = grouped.merge(sums, on=dimension, how="left")
        grouped = grouped.sort_values(["valor_esperado_en_riesgo", "operaciones"], ascending=False)
    else:
        grouped = grouped.sort_values("operaciones", ascending=False)
    return grouped.head(top_n).to_dict(orient="records")


def evaluate_severity(metrics: dict[str, Any], thresholds: dict[str, Any]) -> tuple[str, list[str]]:
    """Yo convierto KPIs en severidad para que GitHub pueda abrir issue solo cuando importa."""
    reasons: list[str] = []
    severity = "ok"
    total = max(int(metrics.get("total_operations") or 0), 1)
    p0 = int(metrics.get("priority_counts", {}).get("P0", 0))
    p0_share = p0 / total
    avg_risk = metrics.get("average_risk")
    total_value = metrics.get("total_value_at_risk")

    def escalate(new: str) -> None:
        nonlocal severity
        levels = {"ok": 0, "warning": 1, "critical": 2}
        if levels[new] > levels[severity]:
            severity = new

    if p0 >= int(thresholds.get("p0_critical_count", 50)):
        escalate("critical")
        reasons.append(f"P0={p0} supera umbral crítico.")
    elif p0 >= int(thresholds.get("p0_warning_count", 10)):
        escalate("warning")
        reasons.append(f"P0={p0} supera umbral de advertencia.")

    if p0_share >= float(thresholds.get("p0_critical_share", 0.4)):
        escalate("critical")
        reasons.append(f"P0 share={p0_share:.1%} supera umbral crítico.")

    if avg_risk is not None:
        if avg_risk >= float(thresholds.get("average_risk_critical", 0.55)):
            escalate("critical")
            reasons.append(f"Riesgo promedio={avg_risk:.3f} supera umbral crítico.")
        elif avg_risk >= float(thresholds.get("average_risk_warning", 0.35)):
            escalate("warning")
            reasons.append(f"Riesgo promedio={avg_risk:.3f} supera umbral de advertencia.")

    if total_value is not None:
        if total_value >= float(thresholds.get("value_at_risk_critical", 15000000)):
            escalate("critical")
            reasons.append(f"Valor esperado en riesgo=S/ {total_value:,.2f} supera umbral crítico.")
        elif total_value >= float(thresholds.get("value_at_risk_warning", 5000000)):
            escalate("warning")
            reasons.append(f"Valor esperado en riesgo=S/ {total_value:,.2f} supera umbral de advertencia.")

    if not reasons:
        reasons.append("Los KPIs están dentro de los umbrales configurados.")
    return severity, reasons


def build_digest(config_path: Path = DEFAULT_CONFIG, output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    """Yo construyo el digest ejecutivo desde el ranking operativo de riesgo de caída."""
    config = load_yaml(config_path)
    risk_cfg = config.get("commercial_risk", {})
    ranking_path = ROOT / risk_cfg.get("ranking_path", "data/processed/scoring/ranking_operaciones_riesgo_caida.csv")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not ranking_path.exists():
        payload = {
            "severity": "critical",
            "error": f"No encuentro el ranking esperado: {ranking_path.as_posix()}",
            "ranking_path": ranking_path.as_posix(),
        }
        write_outputs(payload, output_dir)
        raise FileNotFoundError(payload["error"])

    df = pd.read_csv(ranking_path)
    risk_column, risk_values = numeric_series(df, ["riesgo_caida", "riesgo", "risk_score", "probabilidad_caida", "score_riesgo", "probability"])
    value_column, value_values = numeric_series(df, ["valor_esperado_en_riesgo", "expected_value_at_risk", "valor_riesgo", "valor_en_riesgo"])
    if value_column and value_values is not None:
        df[value_column] = value_values.fillna(0)

    priority_column = detect_priority_column(df)
    if priority_column:
        priority_counts = df[priority_column].map(normalize_priority).value_counts().to_dict()
    else:
        priority_counts = {"Sin prioridad": int(len(df))}

    top_n = int(risk_cfg.get("top_n", 5))
    metrics = {
        "total_operations": int(len(df)),
        "priority_column": priority_column,
        "priority_counts": {str(k): int(v) for k, v in priority_counts.items()},
        "risk_column": risk_column,
        "average_risk": None if risk_values is None else float(risk_values.mean()),
        "value_column": value_column,
        "total_value_at_risk": None if value_values is None else float(value_values.sum()),
        "top_projects": top_dimension(df, ["proyecto", "project", "nombre_proyecto"], value_column, top_n),
        "top_advisors": top_dimension(df, ["asesor", "advisor", "usuario_separacion", "nombres_usuario"], value_column, top_n),
        "source_path": ranking_path.as_posix(),
    }
    severity, reasons = evaluate_severity(metrics, risk_cfg)
    metrics["severity"] = severity
    metrics["alert_reasons"] = reasons
    write_outputs(metrics, output_dir)
    return metrics


def money(value: Any) -> str:
    """Yo formateo montos en soles para que el mensaje sea comprensible para gerencia."""
    if value is None:
        return "No detectado"
    return f"S/ {float(value):,.2f}"


def write_outputs(payload: dict[str, Any], output_dir: Path) -> None:
    """Yo dejo JSON, Markdown e issue body para que GitHub Actions pueda publicar la alerta."""
    output_dir.mkdir(parents=True, exist_ok=True)
    severity = payload.get("severity", "ok")
    icon = {"ok": "✅", "warning": "⚠️", "critical": "🚨"}.get(severity, "ℹ️")
    title = f"{icon} Intelligence Factory · Commercial KPI Digest"
    lines = [
        f"# {title}",
        "",
        "## Estado ejecutivo",
        f"- Severidad: **{severity.upper()}**",
    ]
    for reason in payload.get("alert_reasons", []):
        lines.append(f"- {reason}")

    if "error" not in payload:
        lines.extend([
            "",
            "## Riesgo de caída",
            f"- Operaciones evaluadas: **{payload.get('total_operations', 0):,}**",
            f"- Prioridades: **{payload.get('priority_counts', {})}**",
            f"- Riesgo promedio: **{payload.get('average_risk') if payload.get('average_risk') is not None else 'No detectado'}**",
            f"- Valor esperado en riesgo: **{money(payload.get('total_value_at_risk'))}**",
            "",
            "## Top proyectos por valor/riesgo",
            "```json",
            json.dumps(payload.get("top_projects", []), ensure_ascii=False, indent=2),
            "```",
            "",
            "## Top asesores por valor/riesgo",
            "```json",
            json.dumps(payload.get("top_advisors", []), ensure_ascii=False, indent=2),
            "```",
        ])

    lines.extend([
        "",
        "## Acción recomendada",
        "Yo revisaría primero la cola P0, validaría concentración por proyecto/asesor y cerraría el día con feedback de intervención.",
        "",
        "## Archivos fuente",
        f"- Ranking: `{payload.get('source_path', payload.get('ranking_path', 'No detectado'))}`",
    ])

    (output_dir / "EXECUTIVE_KPI_DIGEST.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "EXECUTIVE_KPI_DIGEST.md").write_text("\n".join(lines), encoding="utf-8")
    (output_dir / "COMMERCIAL_ALERT_ISSUE_BODY.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--fail-on-critical", action="store_true")
    args = parser.parse_args()
    payload = build_digest(Path(args.config), Path(args.output_dir))
    print(f"Digest generado en {Path(args.output_dir) / 'EXECUTIVE_KPI_DIGEST.md'}")
    if args.fail_on_critical and payload.get("severity") == "critical":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
