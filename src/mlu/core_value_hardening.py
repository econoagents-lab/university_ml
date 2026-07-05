from __future__ import annotations

import html
import json
import math
import os
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from src.mlu.config import PROJECT_ROOT

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

CONFIG_PATH = PROJECT_ROOT / "config" / "core_value_hardening.yml"
RANKING_PATH = PROJECT_ROOT / "data" / "processed" / "scoring" / "ranking_operaciones_riesgo_caida.csv"
TRAINING_PATH = PROJECT_ROOT / "data" / "processed" / "gold" / "riesgo_caida_training_model_ready.csv"
PRECISION_AT_K_PATH = PROJECT_ROOT / "reports" / "modeling" / "precision_at_k.csv"
LIFT_METRICS_PATH = PROJECT_ROOT / "reports" / "modeling" / "lift_metrics.json"
CALIBRATION_SUMMARY_PATH = PROJECT_ROOT / "reports" / "monitoring" / "calibration_summary.json"
PUBLIC_PAYLOAD_PATH = PROJECT_ROOT / "reports" / "public" / "decision_dashboard_payload_public.json"
PUBLIC_DASHBOARD_HTML_PATH = PROJECT_ROOT / "reports" / "public" / "DECISION_DASHBOARD_PUBLIC.html"
OUT_DIR = PROJECT_ROOT / "reports" / "core_value_hardening"
DATA_OUT_DIR = PROJECT_ROOT / "data" / "processed" / "core_value_hardening"
CAPACITY_QUEUE_SAFE_PATH = DATA_OUT_DIR / "capacity_risk_queue_safe.csv"
CAPACITY_QUEUE_INTERNAL_PATH = DATA_OUT_DIR / "capacity_risk_queue_internal.csv"
CAPACITY_REVIEW_PATH = OUT_DIR / "CAPACITY_PRIORITIZATION_REVIEW.md"
MODEL_REVIEW_PATH = OUT_DIR / "MODEL_BASELINE_LIFT_REVIEW.md"
EXECUTIVE_BRIEF_MD_PATH = OUT_DIR / "EXECUTIVE_VALUE_BRIEF.md"
EXECUTIVE_BRIEF_HTML_PATH = OUT_DIR / "EXECUTIVE_VALUE_BRIEF.html"
MANIFEST_PATH = OUT_DIR / "core_value_hardening_manifest.json"
VALIDATION_PATH = OUT_DIR / "core_value_hardening_validation.json"

FORBIDDEN_TERMS = [
    "cliente", "documento", "dni", "email", "telefono", "teléfono", "celular",
    "direccion", "dirección", "nombre_completo", "codigo_proforma", "codigo_unidad",
    "password", "secret", "credencial", "redshift_password",
]


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    """
    Yo cargo la configuración del hardening para que las decisiones de producto
    vivan en YAML y no enterradas en código.
    """
    if path.exists() and yaml is not None:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    return {
        "risk_capacity_policy": {"daily_action_capacity": 30, "p0_count": 30, "p1_count": 70, "p2_count": 200},
        "public_privacy": {"anonymize_projects_public": True, "anonymize_advisors_public": True, "max_top_projects": 10, "max_top_advisors": 10, "max_top_channels": 10, "forbidden_public_fields": FORBIDDEN_TERMS},
        "model_review": {"top_k": [10, 20, 30, 50, 100, 200], "capacity_k": 30, "minimum_lift_for_strong_claim": 1.5},
    }


def read_table(path: Path) -> pd.DataFrame:
    """
    Yo leo CSV o parquet sin obligar a un formato único.
    """
    if not path.exists():
        return pd.DataFrame()
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def stable_label(value: Any, prefix: str) -> str:
    """
    Yo convierto identificadores sensibles o competitivos en etiquetas estables.
    """
    raw = str(value) if value is not None else "missing"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8].upper()
    return f"{prefix}_{digest}"


def find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """
    Yo busco columnas con nombres alternativos para hacer el motor resistente
    a versiones previas del proyecto.
    """
    lookup = {c.lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in lookup:
            return lookup[c.lower()]
    return None


def build_capacity_based_queue(ranking_df: pd.DataFrame | None = None, config: dict[str, Any] | None = None) -> pd.DataFrame:
    """
    Yo reconstruyo la cola de riesgo con prioridad por capacidad comercial.
    P0 deja de ser 'todo lo que asusta' y pasa a ser 'lo que puedo actuar hoy'.
    """
    cfg = config or load_config()
    policy = cfg.get("risk_capacity_policy", {})
    df = ranking_df.copy() if ranking_df is not None else read_table(RANKING_PATH)
    if df.empty:
        return df

    value_col = find_col(df, ["valor_esperado_en_riesgo", "valor_en_riesgo", "expected_value_at_risk"])
    risk_col = find_col(df, ["riesgo_caida", "risk_score", "probabilidad_caida"])
    days_col = find_col(df, ["dias_en_tuberia", "days_in_pipeline"])
    project_col = find_col(df, ["proyecto", "project"])
    advisor_col = find_col(df, ["asesor", "responsable", "advisor"])
    channel_col = find_col(df, ["canal_agrupado", "canal", "medio_captacion"])

    for col, default in [(value_col, 0.0), (risk_col, 0.0), (days_col, 0.0)]:
        if col is not None:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(default)

    sort_cols = []
    for c in policy.get("sort_by", ["valor_esperado_en_riesgo", "riesgo_caida", "dias_en_tuberia"]):
        real_col = find_col(df, [c])
        if real_col:
            sort_cols.append(real_col)
    if not sort_cols:
        sort_cols = [value_col or risk_col or df.columns[0]]

    df = df.sort_values(sort_cols, ascending=False).reset_index(drop=True)
    df["ranking_capacity"] = range(1, len(df) + 1)

    p0 = int(policy.get("p0_count", policy.get("daily_action_capacity", 30)))
    p1 = int(policy.get("p1_count", 70))
    p2 = int(policy.get("p2_count", 200))

    def classify(rank: int) -> str:
        if rank <= p0:
            return "P0_top_capacity_today"
        if rank <= p0 + p1:
            return "P1_next_48h"
        if rank <= p0 + p1 + p2:
            return "P2_monitor_72h"
        return "P3_backlog"

    sla = policy.get("sla_hours", {})
    df["prioridad_capacity"] = df["ranking_capacity"].apply(classify)
    df["sla_horas_capacity"] = df["prioridad_capacity"].map(sla).fillna(168).astype(int)
    df["accion_capacity"] = df["prioridad_capacity"].map({
        "P0_top_capacity_today": "Actuar hoy: llamada asesor/gerencia y registrar resultado.",
        "P1_next_48h": "Actuar en 48h: seguimiento con compromiso y próxima acción.",
        "P2_monitor_72h": "Monitorear 72h: revisar señales y objeciones.",
        "P3_backlog": "Backlog: no intervenir salvo nueva señal o capacidad disponible.",
    }).fillna("Seguimiento estándar.")

    if project_col:
        df["proyecto"] = df[project_col]
    if advisor_col:
        df["asesor"] = df[advisor_col]
    if channel_col:
        df["canal"] = df[channel_col]
    if risk_col:
        df["riesgo_caida"] = df[risk_col]
    if value_col:
        df["valor_esperado_en_riesgo"] = df[value_col]
    if days_col:
        df["dias_en_tuberia"] = df[days_col]

    DATA_OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(CAPACITY_QUEUE_INTERNAL_PATH, index=False, encoding="utf-8-sig")

    safe = pd.DataFrame({
        "operation_id": [stable_label(i, "OP") for i in df.index],
        "ranking_capacity": df["ranking_capacity"],
        "proyecto": df.get("proyecto", pd.Series(["Sin proyecto"] * len(df))),
        "asesor_id": [stable_label(v, "ASESOR") for v in df.get("asesor", pd.Series(["sin_asesor"] * len(df)))],
        "canal": df.get("canal", pd.Series(["Sin canal"] * len(df))),
        "riesgo_caida": pd.to_numeric(df.get("riesgo_caida", pd.Series([0] * len(df))), errors="coerce").fillna(0).round(4),
        "valor_esperado_en_riesgo": pd.to_numeric(df.get("valor_esperado_en_riesgo", pd.Series([0] * len(df))), errors="coerce").fillna(0).round(2),
        "dias_en_tuberia": pd.to_numeric(df.get("dias_en_tuberia", pd.Series([0] * len(df))), errors="coerce").fillna(0).round(0),
        "prioridad": df["prioridad_capacity"],
        "sla_horas": df["sla_horas_capacity"],
        "accion_recomendada": df["accion_capacity"],
        "data_mode": "crm_aggregated_safe",
    })
    safe.to_csv(CAPACITY_QUEUE_SAFE_PATH, index=False, encoding="utf-8-sig")
    return df


def _aggregate_top(df: pd.DataFrame, group_col: str, name_col: str, top_n: int, anonymize: bool = False, prefix: str = "Item") -> list[dict[str, Any]]:
    if df.empty or group_col not in df.columns:
        return []
    agg = (
        df.groupby(group_col, dropna=False)
        .agg(
            operaciones=(group_col, "count"),
            riesgo_promedio=("riesgo_caida", "mean"),
            valor_en_riesgo=("valor_esperado_en_riesgo", "sum"),
            p0_p1=("prioridad_capacity", lambda s: int(s.isin(["P0_top_capacity_today", "P1_next_48h"]).sum())),
        )
        .reset_index()
        .sort_values("valor_en_riesgo", ascending=False)
        .head(top_n)
    )
    out = []
    for _, row in agg.iterrows():
        raw_name = row[group_col]
        label = stable_label(raw_name, prefix) if anonymize else str(raw_name)
        out.append({
            name_col: label,
            "operaciones": int(row["operaciones"]),
            "riesgo_promedio": round(float(row["riesgo_promedio"]), 4),
            "valor_en_riesgo": round(float(row["valor_en_riesgo"]), 2),
            "p0_p1": int(row["p0_p1"]),
        })
    return out


def build_capacity_public_payload(queue_df: pd.DataFrame | None = None, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Yo genero el payload público corregido: agregado, seguro y con P0/P1 por capacidad.
    """
    cfg = config or load_config()
    privacy = cfg.get("public_privacy", {})
    df = queue_df.copy() if queue_df is not None else build_capacity_based_queue(config=cfg)
    if df.empty:
        payload = {"status": "empty", "data_mode": "crm_aggregated_safe"}
    else:
        p0p1 = df[df["prioridad_capacity"].isin(["P0_top_capacity_today", "P1_next_48h"])]
        payload = {
            "total_operaciones": int(len(df)),
            "valor_total_en_riesgo": round(float(df["valor_esperado_en_riesgo"].sum()), 2),
            "riesgo_promedio": round(float(df["riesgo_caida"].mean()), 4),
            "p0_p1": {
                "operaciones": int(len(p0p1)),
                "valor_en_riesgo": round(float(p0p1["valor_esperado_en_riesgo"].sum()), 2),
                "definition": "P0/P1 asignado por capacidad comercial, no por umbral bruto.",
            },
            "top_proyectos": _aggregate_top(
                df, "proyecto", "proyecto", int(privacy.get("max_top_projects", 10)),
                anonymize=bool(privacy.get("anonymize_projects_public", True)), prefix="Proyecto"
            ),
            "top_asesores": _aggregate_top(
                df, "asesor", "asesor_anon", int(privacy.get("max_top_advisors", 10)),
                anonymize=True, prefix="Asesor"
            ),
            "top_canales": _aggregate_top(
                df, "canal", "canal", int(privacy.get("max_top_channels", 10)),
                anonymize=False, prefix="Canal"
            ),
            "fecha_generacion": datetime.now().isoformat(timespec="seconds"),
            "data_mode": "crm",
            "prioritization_mode": "capacity_based_top_n",
        }
    PUBLIC_PAYLOAD_PATH.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_PAYLOAD_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def build_public_dashboard_html(payload: dict[str, Any] | None = None) -> Path:
    """
    Yo regenero el dashboard público con una explicación clara del cambio P0/P1.
    """
    payload = payload or build_capacity_public_payload()
    rows = "".join(
        f"<tr><td>{html.escape(str(r.get('proyecto')))}</td><td>{r.get('operaciones')}</td><td>{float(r.get('riesgo_promedio',0)):.3f}</td><td>S/ {float(r.get('valor_en_riesgo',0)):,.0f}</td><td>{r.get('p0_p1')}</td></tr>"
        for r in payload.get("top_proyectos", [])
    )
    advisor_rows = "".join(
        f"<tr><td>{html.escape(str(r.get('asesor_anon')))}</td><td>{r.get('operaciones')}</td><td>{float(r.get('riesgo_promedio',0)):.3f}</td><td>S/ {float(r.get('valor_en_riesgo',0)):,.0f}</td><td>{r.get('p0_p1')}</td></tr>"
        for r in payload.get("top_asesores", [])
    )
    channel_rows = "".join(
        f"<tr><td>{html.escape(str(r.get('canal')))}</td><td>{r.get('operaciones')}</td><td>{float(r.get('riesgo_promedio',0)):.3f}</td><td>S/ {float(r.get('valor_en_riesgo',0)):,.0f}</td><td>{r.get('p0_p1')}</td></tr>"
        for r in payload.get("top_canales", [])
    )
    p0p1 = payload.get("p0_p1", {})
    html_doc = f"""
<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Public Decision Dashboard · Core Value Hardened</title>
<style>
body{{font-family:Arial,sans-serif;background:#0b1220;color:#e5e7eb;margin:32px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px}}.card{{background:#111827;border:1px solid #334155;border-radius:14px;padding:18px;margin:14px 0}}.kpi{{font-size:28px;font-weight:800;color:#fbbf24}}.label{{color:#93a4bd;font-size:12px;text-transform:uppercase}}table{{width:100%;border-collapse:collapse}}td,th{{border-bottom:1px solid #334155;padding:8px;text-align:left}}th{{color:#fbbf24}}.warn{{background:rgba(251,191,36,.08);border-color:rgba(251,191,36,.4)}}
</style></head><body>
<h1>Public Decision Dashboard · Riesgo de Caída</h1>
<p>Solo agregados · data_mode: <b>{html.escape(str(payload.get('data_mode')))}</b> · priorización: <b>{html.escape(str(payload.get('prioritization_mode')))}</b> · generado: {html.escape(str(payload.get('fecha_generacion')))}</p>
<div class="card warn"><b>Corrección ejecutiva:</b> P0/P1 ahora se calcula por capacidad comercial. La pregunta ya no es “¿qué parece riesgoso?”, sino “¿qué puede atender el equipo hoy y en las próximas 48h?”.</div>
<div class="grid">
<div class="card"><div class="label">Operaciones</div><div class="kpi">{payload.get('total_operaciones',0)}</div></div>
<div class="card"><div class="label">Valor total en riesgo</div><div class="kpi">S/ {float(payload.get('valor_total_en_riesgo',0)):,.0f}</div></div>
<div class="card"><div class="label">P0 + P1 accionable</div><div class="kpi">{p0p1.get('operaciones',0)}</div></div>
<div class="card"><div class="label">Riesgo promedio</div><div class="kpi">{float(payload.get('riesgo_promedio',0)):.3f}</div></div>
</div>
<div class="card"><h2>Top proyectos públicos</h2><p>Por defecto se anonimizan para evitar exposición competitiva.</p><table><thead><tr><th>Proyecto</th><th>Ops</th><th>Riesgo prom.</th><th>Valor riesgo</th><th>P0/P1</th></tr></thead><tbody>{rows}</tbody></table></div>
<div class="card"><h2>Top asesores anonimizados</h2><table><thead><tr><th>Asesor</th><th>Ops</th><th>Riesgo prom.</th><th>Valor riesgo</th><th>P0/P1</th></tr></thead><tbody>{advisor_rows}</tbody></table></div>
<div class="card"><h2>Top canales</h2><table><thead><tr><th>Canal</th><th>Ops</th><th>Riesgo prom.</th><th>Valor riesgo</th><th>P0/P1</th></tr></thead><tbody>{channel_rows}</tbody></table></div>
</body></html>"""
    PUBLIC_DASHBOARD_HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_DASHBOARD_HTML_PATH.write_text(html_doc, encoding="utf-8")
    return PUBLIC_DASHBOARD_HTML_PATH


def build_capacity_review(queue_df: pd.DataFrame | None = None, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Yo documento por qué la priorización anterior era débil y cómo la corrijo.
    """
    cfg = config or load_config()
    policy = cfg.get("risk_capacity_policy", {})
    df = queue_df.copy() if queue_df is not None else build_capacity_based_queue(config=cfg)
    counts = df["prioridad_capacity"].value_counts().to_dict() if not df.empty else {}
    p0p1 = df[df["prioridad_capacity"].isin(["P0_top_capacity_today", "P1_next_48h"])] if not df.empty else pd.DataFrame()
    summary = {
        "total_operaciones": int(len(df)),
        "daily_capacity": int(policy.get("daily_action_capacity", 30)),
        "priority_counts": {k: int(v) for k, v in counts.items()},
        "p0_p1_operaciones": int(len(p0p1)),
        "p0_p1_valor_en_riesgo": round(float(p0p1.get("valor_esperado_en_riesgo", pd.Series(dtype=float)).sum()), 2) if not p0p1.empty else 0.0,
    }
    md = f"""# Capacity Prioritization Review v2.7

## Diagnóstico corregido

La versión anterior podía clasificar casi toda la cola como P0/P1. Eso no prioriza: abruma.

## Nueva regla

- P0: top {policy.get('p0_count', 30)} operaciones por valor/riesgo para actuar hoy.
- P1: siguientes {policy.get('p1_count', 70)} operaciones para actuar en 48h.
- P2: siguientes {policy.get('p2_count', 200)} para monitoreo operativo.
- P3: backlog.

## Resultado actual

```json
{json.dumps(summary, indent=2, ensure_ascii=False)}
```

## Decisión de producto

El dashboard público y la cola operativa deben hablar de capacidad, no de urgencia infinita. El valor del sistema es decidir qué se puede ejecutar primero.
"""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CAPACITY_REVIEW_PATH.write_text(md, encoding="utf-8")
    return summary


def build_model_baseline_lift_review(config: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Yo reviso si el modelo merece discurso fuerte o si debe venderse como ranking gobernado.
    """
    cfg = config or load_config()
    model_cfg = cfg.get("model_review", {})
    lift_metrics = {}
    precision_table = []
    calibration = {}
    if LIFT_METRICS_PATH.exists():
        lift_metrics = json.loads(LIFT_METRICS_PATH.read_text(encoding="utf-8"))
    if PRECISION_AT_K_PATH.exists():
        precision_table = pd.read_csv(PRECISION_AT_K_PATH).to_dict(orient="records")
    if CALIBRATION_SUMMARY_PATH.exists():
        calibration = json.loads(CALIBRATION_SUMMARY_PATH.read_text(encoding="utf-8"))

    top_lift = float(lift_metrics.get("top_decile_lift", 0) or 0)
    roc_auc = float(lift_metrics.get("roc_auc_test", 0) or 0)
    ap = float(lift_metrics.get("average_precision_test", 0) or 0)
    min_strong = float(model_cfg.get("minimum_lift_for_strong_claim", 1.5))
    if top_lift >= min_strong and roc_auc >= 0.65:
        claim = "modelo_apto_para_priorizacion_fuerte"
    elif top_lift > 1.0:
        claim = "modelo_apto_solo_como_ranking_debil_y_gobernado"
    else:
        claim = "modelo_no_supera_baseline_con_claridad"

    result = {
        "roc_auc_test": roc_auc,
        "average_precision_test": ap,
        "top_decile_lift": top_lift,
        "calibration_gap": calibration.get("mean_abs_calibration_gap"),
        "claim_level": claim,
        "recommended_commercial_message": model_cfg.get("weak_model_message", "Vender como sistema de priorización gobernado, no como predicción de alta precisión."),
        "precision_at_k": precision_table,
    }
    precision_rows = "\n".join(
        f"| {int(r.get('k',0))} | {int(r.get('positives',0))} | {float(r.get('precision_at_k',0)):.3f} | {float(r.get('capture_rate_at_k',0)):.3f} |"
        for r in precision_table
    ) or "| - | - | - | - |"
    md = f"""# Model Baseline & Lift Review v2.7

## Veredicto técnico

- ROC AUC test: **{roc_auc:.3f}**
- Average precision test: **{ap:.3f}**
- Lift top decile: **{top_lift:.2f}x**
- Calibration gap medio: **{calibration.get('mean_abs_calibration_gap', 'n/d')}**
- Claim recomendado: **{claim}**

## Lectura ejecutiva

No se debe vender el modelo como oráculo de alta precisión. La promesa defendible es:

> Sistema de priorización, trazabilidad, feedback y aprendizaje operativo.

## Precision@K disponible

| K | Positivos | Precision@K | Capture rate |
|---:|---:|---:|---:|
{precision_rows}

## Acción recomendada

1. Comparar contra reglas simples: días en tubería, cuota inicial, caída histórica por proyecto, asesor/proyecto.
2. Medir lift@capacity: top 30, top 50 y top 100.
3. Recalibrar probabilidades antes de comunicar porcentajes como probabilidad real.
4. Usar el score como ranking hasta que el feedback real mejore evidencia.
"""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_REVIEW_PATH.write_text(md, encoding="utf-8")
    return result


def build_value_defensibility_scorecard() -> list[dict[str, Any]]:
    """
    Yo clasifico los módulos según si son oficiales, proxy, demo o pendientes.
    """
    items = [
        ("Marts reales", "reports/real_marts/REAL_MART_EXPANSION.md", "parcial", "Falta validar reglas oficiales con gerencia."),
        ("Cohortes", "CORE_ANALYTICS_30D_PLAN_v1", "planificado", "Todavía debe ejecutarse sobre CRM privado."),
        ("Modelo riesgo", "reports/modeling/lift_metrics.json", "débil_gobernado", "No vender como alta precisión."),
        ("Ranking accionable", "data/processed/core_value_hardening/capacity_risk_queue_safe.csv", "mejorado", "Ahora depende de capacidad comercial."),
        ("Feedback real", "data/processed/action_feedback/feedback_events_safe.csv", "estructura", "Falta captura sostenida 7d/30d."),
        ("Impacto causal", "reports/experiments/EXPERIMENTATION_CAUSAL_IMPACT_LAB.md", "prematuro", "Muestra insuficiente."),
        ("Dashboard público", "reports/public/DECISION_DASHBOARD_PUBLIC.html", "mejorado", "Debe mantenerse agregado y anonimizado."),
        ("Demo comercial", "reports/core_value_hardening/EXECUTIVE_VALUE_BRIEF.html", "enfocado", "Reducir a historia de valor."),
    ]
    return [
        {"modulo": m, "evidencia": e, "estado": s, "riesgo": r}
        for m, e, s, r in items
    ]


def build_executive_value_brief(config: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Yo creo una página ejecutiva única para que la demo no sea una colección de links.
    """
    cfg = config or load_config()
    queue = build_capacity_based_queue(config=cfg)
    payload = build_capacity_public_payload(queue, cfg)
    build_public_dashboard_html(payload)
    capacity = build_capacity_review(queue, cfg)
    model = build_model_baseline_lift_review(cfg)
    scorecard = build_value_defensibility_scorecard()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    score_rows_md = "\n".join(
        f"| {x['modulo']} | {x['estado']} | `{x['evidencia']}` | {x['riesgo']} |" for x in scorecard
    )
    md = f"""# Executive Value Brief v2.7

## Decisión de auditoría

Se congela la expansión superficial y se prioriza el core: marts reales, cohortes, stock/cobranza, modelo recalibrado, ranking por capacidad y feedback real.

## Qué cambia en esta versión

1. P0/P1 deja de ser umbral bruto y pasa a ser capacidad accionable.
2. El modelo se comunica como ranking gobernado, no como oráculo.
3. El dashboard público se anonimiza por defecto.
4. La demo se reduce a una historia ejecutiva de valor.
5. Se crea scorecard de defendibilidad económica.

## KPIs corregidos

- Operaciones evaluadas: **{payload.get('total_operaciones', 0)}**
- Valor total en riesgo: **S/ {float(payload.get('valor_total_en_riesgo', 0)):,.0f}**
- P0/P1 accionable: **{payload.get('p0_p1', {}).get('operaciones', 0)}**
- Valor P0/P1: **S/ {float(payload.get('p0_p1', {}).get('valor_en_riesgo', 0)):,.0f}**
- Riesgo promedio: **{float(payload.get('riesgo_promedio', 0)):.3f}**

## Veredicto del modelo

- ROC AUC: **{model.get('roc_auc_test', 0):.3f}**
- Average precision: **{model.get('average_precision_test', 0):.3f}**
- Lift top decile: **{model.get('top_decile_lift', 0):.2f}x**
- Claim recomendado: **{model.get('claim_level')}**

## Scorecard de defendibilidad

| Módulo | Estado | Evidencia | Riesgo |
|---|---|---|---|
{score_rows_md}

## Próxima decisión

Ejecutar CORE_ANALYTICS_30D sobre CRM privado y presentar solo 6 puertas ejecutivas: brief, dashboard público, riesgo/acción, cohortes, stock/cobranza y feedback/valor.
"""
    EXECUTIVE_BRIEF_MD_PATH.write_text(md, encoding="utf-8")

    score_rows_html = "".join(
        f"<tr><td>{html.escape(x['modulo'])}</td><td>{html.escape(x['estado'])}</td><td><code>{html.escape(x['evidencia'])}</code></td><td>{html.escape(x['riesgo'])}</td></tr>" for x in scorecard
    )
    h = f"""
<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Executive Value Brief v2.7</title><style>
body{{font-family:Arial,sans-serif;background:#070b14;color:#f4f0e8;margin:0}}.wrap{{max-width:1120px;margin:auto;padding:42px 24px}}.eyebrow{{color:#d6ad60;letter-spacing:.16em;text-transform:uppercase;font-size:12px;font-weight:bold}}h1{{font-size:44px;line-height:1.05}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px}}.card{{background:#101827;border:1px solid rgba(214,173,96,.35);border-radius:18px;padding:20px;margin:14px 0}}.kpi{{font-size:30px;color:#d6ad60;font-weight:800}}.label{{color:#9aa8bd;font-size:12px;text-transform:uppercase}}table{{width:100%;border-collapse:collapse}}td,th{{border-bottom:1px solid #334155;padding:10px;text-align:left}}th{{color:#d6ad60}}a{{color:#d6ad60}}.warn{{background:rgba(214,173,96,.08)}}
</style></head><body><main class="wrap">
<div class="eyebrow">Core Value Hardening · v2.7</div><h1>De demo impresionante a sistema económicamente defendible.</h1>
<p>Esta página concentra el juicio ejecutivo: qué decisión cambia, qué valor está en riesgo y qué parte aún no debe venderse como causalidad fuerte.</p>
<div class="grid">
<div class="card"><div class="label">Operaciones</div><div class="kpi">{payload.get('total_operaciones',0)}</div></div>
<div class="card"><div class="label">Valor total en riesgo</div><div class="kpi">S/ {float(payload.get('valor_total_en_riesgo',0)):,.0f}</div></div>
<div class="card"><div class="label">P0/P1 accionable</div><div class="kpi">{payload.get('p0_p1',{}).get('operaciones',0)}</div></div>
<div class="card"><div class="label">Lift top decile</div><div class="kpi">{model.get('top_decile_lift',0):.2f}x</div></div>
</div>
<div class="card warn"><h2>Decisión de auditoría</h2><p>Congelar expansión superficial. Endurecer core: marts, cohortes, stock/cobranza, recalibración, feedback y ranking por capacidad.</p></div>
<div class="card"><h2>Qué no se debe prometer</h2><p>No vender como modelo predictivo de alta precisión. Vender como sistema de priorización, trazabilidad y aprendizaje operativo.</p></div>
<div class="card"><h2>Scorecard de defendibilidad</h2><table><thead><tr><th>Módulo</th><th>Estado</th><th>Evidencia</th><th>Riesgo</th></tr></thead><tbody>{score_rows_html}</tbody></table></div>
<div class="card"><h2>Puertas maestras recomendadas</h2><ol><li><a href="/dashboard/executive-value-brief">Executive Value Brief</a></li><li><a href="/public/decision-dashboard">Dashboard público seguro</a></li><li><a href="/decision/riesgo-caida/capacity-queue">Cola de riesgo por capacidad</a></li><li><a href="/dashboard/real-marts">Marts reales</a></li><li><a href="/dashboard/action-feedback">Action feedback</a></li><li><a href="/dashboard/experiment-power-policy">Experiment policy</a></li></ol></div>
</main></body></html>"""
    EXECUTIVE_BRIEF_HTML_PATH.write_text(h, encoding="utf-8")
    manifest = {
        "version": "v2.7_core_value_hardening",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "capacity": capacity,
        "model": model,
        "scorecard": scorecard,
        "outputs": {
            "executive_brief_md": str(EXECUTIVE_BRIEF_MD_PATH),
            "executive_brief_html": str(EXECUTIVE_BRIEF_HTML_PATH),
            "public_payload": str(PUBLIC_PAYLOAD_PATH),
            "public_dashboard": str(PUBLIC_DASHBOARD_HTML_PATH),
            "capacity_queue_safe": str(CAPACITY_QUEUE_SAFE_PATH),
            "model_review": str(MODEL_REVIEW_PATH),
            "capacity_review": str(CAPACITY_REVIEW_PATH),
        }
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def validate_no_forbidden_public_content(paths: list[Path] | None = None, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Yo valido que los outputs públicos no expongan PII ni campos operativos sensibles.
    """
    cfg = config or load_config()
    forbidden = [str(x).lower() for x in cfg.get("public_privacy", {}).get("forbidden_public_fields", FORBIDDEN_TERMS)]
    paths = paths or [PUBLIC_PAYLOAD_PATH, PUBLIC_DASHBOARD_HTML_PATH, EXECUTIVE_BRIEF_HTML_PATH]
    hits: dict[str, list[str]] = {}
    for path in paths:
        if not path.exists():
            hits[str(path)] = ["missing"]
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        found = [term for term in forbidden if re.search(r"\b" + re.escape(term) + r"\b", text)]
        # Yo permito términos dentro del disclaimer de privacidad, pero no en JSON público.
        if path.suffix.lower() == ".json":
            bad = found
        else:
            bad = [f for f in found if f not in {"cliente", "email", "telefono", "teléfono", "documento"}]
        if bad:
            hits[str(path)] = bad
    status = "ok" if not hits else "fail"
    result = {"status": status, "forbidden_hits": hits, "checked_paths": [str(p) for p in paths]}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def run_core_value_hardening() -> dict[str, Any]:
    """
    Yo ejecuto el paquete completo que corrige las debilidades detectadas en auditoría.
    """
    cfg = load_config()
    manifest = build_executive_value_brief(cfg)
    validation = validate_no_forbidden_public_content(config=cfg)
    manifest["validation"] = validation
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        return run_core_value_hardening()
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
