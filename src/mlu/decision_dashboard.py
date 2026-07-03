from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from src.mlu.config import PROJECT_ROOT, SCORING_RANKING_PATH
from src.mlu.leakage import assert_no_forbidden_columns

DASHBOARD_DIR = PROJECT_ROOT / "reports" / "dashboard"
DASHBOARD_FIGURES_DIR = PROJECT_ROOT / "reports" / "figures" / "dashboard"
DECISION_QUEUE_PATH = DASHBOARD_DIR / "decision_queue_riesgo_caida.parquet"
DECISION_QUEUE_CSV_PATH = DASHBOARD_DIR / "decision_queue_riesgo_caida.csv"
DASHBOARD_PAYLOAD_PATH = DASHBOARD_DIR / "decision_dashboard_payload.json"
DASHBOARD_HTML_PATH = DASHBOARD_DIR / "DECISION_DASHBOARD_RIESGO_CAIDA.html"
EXECUTIVE_BRIEF_PATH = DASHBOARD_DIR / "EXECUTIVE_DECISION_BRIEF_RIESGO_CAIDA.md"

QUEUE_REQUIRED_COLUMNS = [
    "codigo_proforma",
    "codigo_unidad",
    "proyecto",
    "asesor",
    "precio_departamento",
    "dias_en_tuberia",
    "riesgo_caida",
    "nivel_riesgo",
    "decision_recomendada",
    "responsable",
    "valor_esperado_en_riesgo",
    "ranking_prioridad",
]

API_ALLOWED_QUEUE_COLUMNS = QUEUE_REQUIRED_COLUMNS + [
    "fecha_separacion",
    "medio_captacion",
    "canal_agrupado",
    "dormitorios",
    "tiene_cuota_inicial",
    "cambios_unidad",
    "interacciones_ult_7d",
    "descuento_pct",
    "prioridad_operativa",
    "sla_horas",
    "fecha_limite_accion",
    "accion_operativa",
    "estado_accion",
    "decision_owner",
]


def _read_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe archivo requerido: {path}")
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def load_ranking(path: Path | None = None) -> pd.DataFrame:
    ranking_path = path or SCORING_RANKING_PATH
    df = _read_table(ranking_path)
    missing = [c for c in QUEUE_REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Ranking incompleto. Faltan columnas: {missing}")
    assert_no_forbidden_columns(df, context="decision_dashboard_input_ranking")
    return df.copy()


def classify_operational_priority(row: pd.Series) -> str:
    risk = float(row.get("riesgo_caida", 0.0))
    value = float(row.get("valor_esperado_en_riesgo", 0.0))
    days = float(row.get("dias_en_tuberia", 0.0))
    if risk >= 0.70 or value >= 150_000 or days >= 120:
        return "P0_intervenir_hoy"
    if risk >= 0.40 or value >= 75_000 or days >= 60:
        return "P1_24_horas"
    if risk >= 0.25 or value >= 35_000:
        return "P2_72_horas"
    return "P3_monitoreo"


def sla_hours(priority: str) -> int:
    return {
        "P0_intervenir_hoy": 8,
        "P1_24_horas": 24,
        "P2_72_horas": 72,
        "P3_monitoreo": 168,
    }.get(priority, 168)


def action_from_priority(priority: str) -> str:
    return {
        "P0_intervenir_hoy": "Llamada gerente/asesor hoy + revisar condición financiera y cuota inicial.",
        "P1_24_horas": "Seguimiento asesor en 24h + registrar compromiso concreto.",
        "P2_72_horas": "Seguimiento preventivo y validación de objeciones.",
        "P3_monitoreo": "Mantener seguimiento estándar y observar señales nuevas.",
    }.get(priority, "Seguimiento estándar.")


def build_decision_queue(
    ranking_df: pd.DataFrame | None = None,
    ranking_path: Path | None = None,
    max_rows: int | None = None,
) -> pd.DataFrame:
    df = ranking_df.copy() if ranking_df is not None else load_ranking(ranking_path)
    assert_no_forbidden_columns(df, context="decision_queue_before_selection")

    for col in API_ALLOWED_QUEUE_COLUMNS:
        if col not in df.columns:
            df[col] = "" if col not in {"prioridad_operativa", "sla_horas"} else None

    df["prioridad_operativa"] = df.apply(classify_operational_priority, axis=1)
    df["sla_horas"] = df["prioridad_operativa"].apply(sla_hours)
    now = datetime.now()
    df["fecha_limite_accion"] = df["sla_horas"].apply(lambda h: (now + timedelta(hours=int(h))).strftime("%Y-%m-%d %H:%M"))
    df["accion_operativa"] = df["prioridad_operativa"].apply(action_from_priority)
    df["estado_accion"] = "pendiente"
    df["decision_owner"] = df["responsable"].fillna(df["asesor"])

    df = df.sort_values(
        by=["prioridad_operativa", "valor_esperado_en_riesgo", "riesgo_caida", "dias_en_tuberia"],
        ascending=[True, False, False, False],
    ).reset_index(drop=True)
    df["ranking_decision"] = range(1, len(df) + 1)

    selected = [c for c in API_ALLOWED_QUEUE_COLUMNS + ["ranking_decision"] if c in df.columns]
    out = df[selected].copy()
    assert_no_forbidden_columns(out, context="decision_queue_output")
    if max_rows is not None:
        out = out.head(int(max_rows)).copy()
    return out


def compute_decision_kpis(queue_df: pd.DataFrame) -> dict[str, Any]:
    if queue_df.empty:
        return {
            "total_operaciones": 0,
            "valor_total_en_riesgo": 0.0,
            "riesgo_promedio": 0.0,
            "p0_operaciones": 0,
            "p1_operaciones": 0,
            "p0_p1_valor_en_riesgo": 0.0,
            "top_proyecto_por_valor": None,
            "top_asesor_por_valor": None,
        }

    priority_counts = queue_df["prioridad_operativa"].value_counts().to_dict()
    p0p1 = queue_df[queue_df["prioridad_operativa"].isin(["P0_intervenir_hoy", "P1_24_horas"])]
    project_value = queue_df.groupby("proyecto", dropna=False)["valor_esperado_en_riesgo"].sum().sort_values(ascending=False)
    advisor_value = queue_df.groupby("asesor", dropna=False)["valor_esperado_en_riesgo"].sum().sort_values(ascending=False)

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_operaciones": int(len(queue_df)),
        "valor_total_en_riesgo": round(float(queue_df["valor_esperado_en_riesgo"].sum()), 2),
        "riesgo_promedio": round(float(queue_df["riesgo_caida"].mean()), 4),
        "riesgo_p90": round(float(queue_df["riesgo_caida"].quantile(0.90)), 4),
        "p0_operaciones": int(priority_counts.get("P0_intervenir_hoy", 0)),
        "p1_operaciones": int(priority_counts.get("P1_24_horas", 0)),
        "p2_operaciones": int(priority_counts.get("P2_72_horas", 0)),
        "p3_operaciones": int(priority_counts.get("P3_monitoreo", 0)),
        "p0_p1_valor_en_riesgo": round(float(p0p1["valor_esperado_en_riesgo"].sum()), 2),
        "top_proyecto_por_valor": str(project_value.index[0]) if len(project_value) else None,
        "top_proyecto_valor_en_riesgo": round(float(project_value.iloc[0]), 2) if len(project_value) else 0.0,
        "top_asesor_por_valor": str(advisor_value.index[0]) if len(advisor_value) else None,
        "top_asesor_valor_en_riesgo": round(float(advisor_value.iloc[0]), 2) if len(advisor_value) else 0.0,
    }


def aggregate_by(queue_df: pd.DataFrame, group_col: str, top_n: int = 20) -> pd.DataFrame:
    if group_col not in queue_df.columns:
        raise ValueError(f"No existe columna de agrupación: {group_col}")
    agg = (
        queue_df.groupby(group_col, dropna=False)
        .agg(
            operaciones=("codigo_proforma", "count"),
            riesgo_promedio=("riesgo_caida", "mean"),
            valor_en_riesgo=("valor_esperado_en_riesgo", "sum"),
            p0=("prioridad_operativa", lambda s: int((s == "P0_intervenir_hoy").sum())),
            p1=("prioridad_operativa", lambda s: int((s == "P1_24_horas").sum())),
        )
        .reset_index()
        .sort_values(["valor_en_riesgo", "operaciones"], ascending=[False, False])
        .head(top_n)
    )
    agg["riesgo_promedio"] = agg["riesgo_promedio"].round(4)
    agg["valor_en_riesgo"] = agg["valor_en_riesgo"].round(2)
    return agg


def build_dashboard_payload(queue_df: pd.DataFrame) -> dict[str, Any]:
    kpis = compute_decision_kpis(queue_df)
    by_project = aggregate_by(queue_df, "proyecto", top_n=15).to_dict(orient="records")
    by_advisor = aggregate_by(queue_df, "asesor", top_n=15).to_dict(orient="records")
    action_plan = queue_df.head(50).to_dict(orient="records")
    return {
        "metadata": {
            "project": "riesgo_caida",
            "dashboard_version": "0.9.0",
            "data_mode": "crm_first",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "source": str(SCORING_RANKING_PATH),
        },
        "kpis": kpis,
        "by_project": by_project,
        "by_advisor": by_advisor,
        "action_plan": action_plan,
    }


def save_decision_artifacts(queue_df: pd.DataFrame, payload: dict[str, Any]) -> dict[str, str]:
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    queue_df.to_parquet(DECISION_QUEUE_PATH, index=False)
    queue_df.to_csv(DECISION_QUEUE_CSV_PATH, index=False, encoding="utf-8-sig")
    DASHBOARD_PAYLOAD_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return {
        "decision_queue_parquet": str(DECISION_QUEUE_PATH),
        "decision_queue_csv": str(DECISION_QUEUE_CSV_PATH),
        "dashboard_payload": str(DASHBOARD_PAYLOAD_PATH),
    }


def load_dashboard_payload() -> dict[str, Any]:
    if DASHBOARD_PAYLOAD_PATH.exists():
        return json.loads(DASHBOARD_PAYLOAD_PATH.read_text(encoding="utf-8"))
    queue = build_decision_queue()
    payload = build_dashboard_payload(queue)
    save_decision_artifacts(queue, payload)
    return payload


def load_decision_queue(limit: int | None = None, prioridad: str | None = None) -> pd.DataFrame:
    if DECISION_QUEUE_PATH.exists():
        df = pd.read_parquet(DECISION_QUEUE_PATH)
    else:
        df = build_decision_queue()
        save_decision_artifacts(df, build_dashboard_payload(df))
    if prioridad:
        df = df[df["prioridad_operativa"] == prioridad].copy()
    if limit is not None:
        df = df.head(int(limit)).copy()
    assert_no_forbidden_columns(df, context="decision_queue_api_response")
    return df


def generate_dashboard_html(payload: dict[str, Any] | None = None) -> Path:
    payload = payload or load_dashboard_payload()
    k = payload["kpis"]
    by_project_rows = "".join(
        f"<tr><td>{r['proyecto']}</td><td>{r['operaciones']}</td><td>{r['riesgo_promedio']}</td><td>S/ {r['valor_en_riesgo']:,.0f}</td><td>{r['p0']}</td><td>{r['p1']}</td></tr>"
        for r in payload["by_project"][:10]
    )
    action_rows = "".join(
        f"<tr><td>{r.get('ranking_decision')}</td><td>{r.get('proyecto')}</td><td>{r.get('asesor')}</td><td>{r.get('codigo_unidad')}</td><td>{float(r.get('riesgo_caida',0)):.3f}</td><td>{r.get('prioridad_operativa')}</td><td>S/ {float(r.get('valor_esperado_en_riesgo',0)):,.0f}</td><td>{r.get('accion_operativa')}</td></tr>"
        for r in payload["action_plan"][:25]
    )
    html = f"""
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Decision Dashboard - Riesgo de Caída</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 32px; background: #0f172a; color: #e5e7eb; }}
.card {{ background: #111827; border: 1px solid #334155; border-radius: 14px; padding: 18px; margin: 14px 0; }}
.grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }}
.kpi {{ font-size: 26px; font-weight: 700; color: #fbbf24; }}
.label {{ color: #94a3b8; font-size: 12px; text-transform: uppercase; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
th, td {{ border-bottom: 1px solid #334155; padding: 8px; text-align: left; font-size: 13px; }}
th {{ color: #fbbf24; }}
small {{ color: #94a3b8; }}
</style>
</head>
<body>
<h1>Decision Dashboard - Riesgo de Caída</h1>
<p><small>CRM-first · generado: {payload['metadata']['generated_at']} · fuente: {payload['metadata']['source']}</small></p>
<div class="grid">
  <div class="card"><div class="label">Operaciones</div><div class="kpi">{k['total_operaciones']}</div></div>
  <div class="card"><div class="label">Valor total en riesgo</div><div class="kpi">S/ {k['valor_total_en_riesgo']:,.0f}</div></div>
  <div class="card"><div class="label">P0 + P1</div><div class="kpi">{k['p0_operaciones'] + k['p1_operaciones']}</div></div>
  <div class="card"><div class="label">Riesgo promedio</div><div class="kpi">{k['riesgo_promedio']:.3f}</div></div>
</div>
<div class="card">
<h2>Lectura ejecutiva</h2>
<p>Priorizar primero operaciones P0/P1 por valor esperado en riesgo y SLA comercial. Esta cola convierte el score del modelo en una lista accionable por responsable.</p>
</div>
<div class="card">
<h2>Top proyectos por valor en riesgo</h2>
<table><thead><tr><th>Proyecto</th><th>Ops</th><th>Riesgo prom.</th><th>Valor riesgo</th><th>P0</th><th>P1</th></tr></thead><tbody>{by_project_rows}</tbody></table>
</div>
<div class="card">
<h2>Plan de acción operativo</h2>
<table><thead><tr><th>#</th><th>Proyecto</th><th>Asesor</th><th>Unidad</th><th>Riesgo</th><th>Prioridad</th><th>Valor riesgo</th><th>Acción</th></tr></thead><tbody>{action_rows}</tbody></table>
</div>
</body>
</html>
"""
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    DASHBOARD_HTML_PATH.write_text(html, encoding="utf-8")
    return DASHBOARD_HTML_PATH


def generate_executive_brief(payload: dict[str, Any] | None = None) -> Path:
    payload = payload or load_dashboard_payload()
    k = payload["kpis"]
    md = f"""# Executive Decision Brief - Riesgo de Caída v0.9

## Estado operativo

La cola de decisión convierte el scoring de riesgo de caída en una lista priorizada por responsable, SLA y valor esperado en riesgo.

## KPIs

- Operaciones activas en cola: {k['total_operaciones']}
- Valor total esperado en riesgo: S/ {k['valor_total_en_riesgo']:,.0f}
- Riesgo promedio: {k['riesgo_promedio']:.3f}
- P0 intervenir hoy: {k['p0_operaciones']}
- P1 24 horas: {k['p1_operaciones']}
- Valor P0/P1: S/ {k['p0_p1_valor_en_riesgo']:,.0f}
- Proyecto principal por valor en riesgo: {k['top_proyecto_por_valor']} (S/ {k['top_proyecto_valor_en_riesgo']:,.0f})
- Asesor principal por valor en riesgo: {k['top_asesor_por_valor']} (S/ {k['top_asesor_valor_en_riesgo']:,.0f})

## Decisión recomendada

1. Revisar diariamente P0 y P1.
2. Registrar acción tomada en feedback loop.
3. Comparar caídas reales versus operaciones intervenidas.
4. No presentar el modelo como oráculo: presentarlo como sistema de priorización gobernado.

## Output operativo

- reports/dashboard/decision_queue_riesgo_caida.csv
- reports/dashboard/decision_dashboard_payload.json
- reports/dashboard/DECISION_DASHBOARD_RIESGO_CAIDA.html
"""
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    EXECUTIVE_BRIEF_PATH.write_text(md, encoding="utf-8")
    return EXECUTIVE_BRIEF_PATH


def generate_dashboard_figures(queue_df: pd.DataFrame | None = None) -> dict[str, str]:
    import matplotlib.pyplot as plt

    df = queue_df.copy() if queue_df is not None else load_decision_queue()
    DASHBOARD_FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, str] = {}

    level_counts = df["prioridad_operativa"].value_counts().reindex(["P0_intervenir_hoy", "P1_24_horas", "P2_72_horas", "P3_monitoreo"]).fillna(0)
    fig, ax = plt.subplots(figsize=(9, 5))
    level_counts.plot(kind="bar", ax=ax)
    ax.set_title("Distribución de prioridades operativas")
    ax.set_xlabel("Prioridad")
    ax.set_ylabel("Operaciones")
    fig.tight_layout()
    p = DASHBOARD_FIGURES_DIR / "01_priority_distribution.png"
    fig.savefig(p, dpi=160)
    plt.close(fig)
    outputs["priority_distribution"] = str(p)

    by_project = aggregate_by(df, "proyecto", top_n=10).sort_values("valor_en_riesgo")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(by_project["proyecto"].astype(str), by_project["valor_en_riesgo"])
    ax.set_title("Top proyectos por valor esperado en riesgo")
    ax.set_xlabel("Valor esperado en riesgo")
    fig.tight_layout()
    p = DASHBOARD_FIGURES_DIR / "02_project_value_at_risk.png"
    fig.savefig(p, dpi=160)
    plt.close(fig)
    outputs["project_value_at_risk"] = str(p)

    by_advisor = aggregate_by(df, "asesor", top_n=10).sort_values("valor_en_riesgo")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(by_advisor["asesor"].astype(str), by_advisor["valor_en_riesgo"])
    ax.set_title("Top asesores por valor esperado en riesgo")
    ax.set_xlabel("Valor esperado en riesgo")
    fig.tight_layout()
    p = DASHBOARD_FIGURES_DIR / "03_advisor_value_at_risk.png"
    fig.savefig(p, dpi=160)
    plt.close(fig)
    outputs["advisor_value_at_risk"] = str(p)

    top = df.head(20).sort_values("valor_esperado_en_riesgo")
    fig, ax = plt.subplots(figsize=(10, 7))
    labels = top["codigo_proforma"].astype(str) + " | " + top["codigo_unidad"].astype(str)
    ax.barh(labels, top["valor_esperado_en_riesgo"])
    ax.set_title("Top 20 operaciones por valor esperado en riesgo")
    ax.set_xlabel("Valor esperado en riesgo")
    fig.tight_layout()
    p = DASHBOARD_FIGURES_DIR / "04_top20_operations_value_at_risk.png"
    fig.savefig(p, dpi=160)
    plt.close(fig)
    outputs["top20_operations_value_at_risk"] = str(p)

    return outputs
