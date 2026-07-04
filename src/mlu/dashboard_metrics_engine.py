from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.mlu.config import PROJECT_ROOT

METRICS_CONFIG_PATH = PROJECT_ROOT / "config" / "dashboard_metrics.yml"
RANKING_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "scoring" / "ranking_operaciones_riesgo_caida.csv"
TRAINING_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "gold" / "riesgo_caida_training_model_ready.csv"
SAMPLE_CSV_PATH = PROJECT_ROOT / "data" / "sample" / "fact_operaciones_sample.csv"
PUBLIC_PAYLOAD_PATH = PROJECT_ROOT / "reports" / "public" / "decision_dashboard_payload_public.json"
DASHBOARD_PAYLOAD_PATH = PROJECT_ROOT / "reports" / "dashboard" / "decision_dashboard_payload.json"
RAGAS_SUMMARY_PATH = PROJECT_ROOT / "reports" / "uni_final" / "RAGAS_LIKE_SUMMARY.md"
LIFT_METRICS_PATH = PROJECT_ROOT / "reports" / "modeling" / "lift_metrics.json"
LIFT_DECILES_PATH = PROJECT_ROOT / "reports" / "modeling" / "lift_deciles.csv"
FEATURE_DRIFT_PATH = PROJECT_ROOT / "reports" / "monitoring" / "feature_drift_summary.json"
PREDICTION_DRIFT_PATH = PROJECT_ROOT / "reports" / "monitoring" / "prediction_drift.json"
CALIBRATION_SUMMARY_PATH = PROJECT_ROOT / "reports" / "monitoring" / "calibration_summary.json"
MODEL_REGISTRY_METADATA_PATH = PROJECT_ROOT / "reports" / "registry" / "model_registry_metadata.json"
CHAMPION_VS_CHALLENGERS_PATH = PROJECT_ROOT / "reports" / "registry" / "champion_vs_challengers.csv"
MARKET_CONTEXT_PATH = PROJECT_ROOT / "data" / "market" / "gold" / "mart_market_district_month.csv"
ALERTS_MANIFEST_PATH = PROJECT_ROOT / "reports" / "alerts" / "alerts_manifest.json"
PRIVACY_VALIDATION_PATH = PROJECT_ROOT / "reports" / "public" / "production_public_payload_validation.json"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "dashboard_metrics"
FAMILY_METRICS_JSON = OUTPUT_DIR / "family_metrics.json"
ENGINE_REPORT_MD = OUTPUT_DIR / "DASHBOARD_METRICS_ENGINE.md"
VALIDATION_JSON = OUTPUT_DIR / "dashboard_metrics_validation.json"
REAL_MART_METADATA_PATH = PROJECT_ROOT / "reports" / "real_marts" / "real_mart_manifest.json"
REAL_MART_VALIDATION_PATH = PROJECT_ROOT / "reports" / "real_marts" / "real_mart_validation.json"
MART_FUNNEL_PATH = PROJECT_ROOT / "data" / "processed" / "real_marts" / "mart_funnel_stage_month.csv"
MART_COBRANZA_PATH = PROJECT_ROOT / "data" / "processed" / "real_marts" / "mart_cobranza_venta.csv"
MART_STOCK_PATH = PROJECT_ROOT / "data" / "processed" / "real_marts" / "mart_stock_inicial_mensual.csv"
MART_PRICING_PATH = PROJECT_ROOT / "data" / "processed" / "real_marts" / "mart_pricing_unit_m2.csv"
MART_MARKET_PROJECT_PATH = PROJECT_ROOT / "data" / "processed" / "real_marts" / "mart_project_vs_market.csv"
MART_FEEDBACK_PATH = PROJECT_ROOT / "data" / "processed" / "real_marts" / "mart_feedback_interventions.csv"
MART_PROXY_GAP_PATH = PROJECT_ROOT / "data" / "processed" / "real_marts" / "mart_proxy_vs_official_gap.csv"

ACTION_FEEDBACK_MANIFEST_PATH = PROJECT_ROOT / "reports" / "action_feedback" / "action_feedback_manifest.json"
ACTION_FEEDBACK_VALIDATION_PATH = PROJECT_ROOT / "reports" / "action_feedback" / "action_feedback_validation.json"
ACTION_FEEDBACK_QUEUE_PATH = PROJECT_ROOT / "data" / "processed" / "action_feedback" / "decision_action_queue_safe.csv"
ACTION_FEEDBACK_OUTCOMES_PATH = PROJECT_ROOT / "data" / "processed" / "action_feedback" / "action_outcomes_summary.csv"
ACTION_FEEDBACK_SIGNAL_PATH = PROJECT_ROOT / "data" / "processed" / "action_feedback" / "retraining_signal.json"


def load_yaml(path: Path) -> dict[str, Any]:
    """
    Yo cargo configuración YAML para que los umbrales de negocio vivan fuera del código.
    """
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def read_json(path: Path) -> dict[str, Any]:
    """
    Yo leo JSON de reportes previos y devuelvo vacío cuando el artefacto todavía no existe.
    """
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def read_csv(path: Path) -> pd.DataFrame:
    """
    Yo leo CSV de forma tolerante para que el motor no dependa de Parquet en Colab o GitHub Actions.
    """
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Yo convierto métricas a float sin romper el reporte si aparece un nulo o texto inesperado.
    """
    try:
        if value is None:
            return default
        if isinstance(value, float) and math.isnan(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """
    Yo busco columnas equivalentes porque mis outputs cambian de nombre entre versiones del proyecto.
    """
    normalized = {str(column).lower().strip(): column for column in df.columns}
    for candidate in candidates:
        key = candidate.lower().strip()
        if key in normalized:
            return normalized[key]
    return None


def percent(value: float) -> float:
    """
    Yo redondeo proporciones como porcentajes de lectura ejecutiva.
    """
    return round(100 * safe_float(value), 2)


def parse_ragas_summary(path: Path = RAGAS_SUMMARY_PATH) -> dict[str, float]:
    """
    Yo extraigo métricas RAGAS-like desde Markdown para convertir la calidad del asistente en KPIs gobernados.
    """
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    metrics: dict[str, float] = {}
    for key in ["faithfulness_proxy_mean", "answer_relevance_proxy_mean", "context_relevance_proxy_mean", "trap_refusal_rate"]:
        match = re.search(rf"{re.escape(key)}:\*\*\s*([0-9.]+)", text)
        if not match:
            match = re.search(rf"{re.escape(key)}\s*[:=]\s*([0-9.]+)", text)
        metrics[key] = safe_float(match.group(1)) if match else 0.0
    return metrics


def build_global_source_context() -> dict[str, Any]:
    """
    Yo reúno los artefactos disponibles para que cada familia calcule métricas especializadas desde la misma evidencia.
    """
    ranking = read_csv(RANKING_CSV_PATH)
    training = read_csv(TRAINING_CSV_PATH)
    if training.empty:
        training = read_csv(SAMPLE_CSV_PATH)
    return {
        "ranking": ranking,
        "training": training,
        "public_payload": read_json(PUBLIC_PAYLOAD_PATH),
        "dashboard_payload": read_json(DASHBOARD_PAYLOAD_PATH),
        "ragas": parse_ragas_summary(),
        "lift_metrics": read_json(LIFT_METRICS_PATH),
        "lift_deciles": read_csv(LIFT_DECILES_PATH),
        "feature_drift": read_json(FEATURE_DRIFT_PATH),
        "prediction_drift": read_json(PREDICTION_DRIFT_PATH),
        "calibration": read_json(CALIBRATION_SUMMARY_PATH),
        "registry": read_json(MODEL_REGISTRY_METADATA_PATH),
        "challengers": read_csv(CHAMPION_VS_CHALLENGERS_PATH),
        "market": read_csv(MARKET_CONTEXT_PATH),
        "real_mart_manifest": read_json(REAL_MART_METADATA_PATH),
        "real_mart_validation": read_json(REAL_MART_VALIDATION_PATH),
        "mart_funnel": read_csv(MART_FUNNEL_PATH),
        "mart_cobranza": read_csv(MART_COBRANZA_PATH),
        "mart_stock": read_csv(MART_STOCK_PATH),
        "mart_pricing": read_csv(MART_PRICING_PATH),
        "mart_market_project": read_csv(MART_MARKET_PROJECT_PATH),
        "mart_feedback": read_csv(MART_FEEDBACK_PATH),
        "mart_proxy_gap": read_csv(MART_PROXY_GAP_PATH),
        "alerts": read_json(ALERTS_MANIFEST_PATH),
        "privacy_validation": read_json(PRIVACY_VALIDATION_PATH),
        "action_feedback_manifest": read_json(ACTION_FEEDBACK_MANIFEST_PATH),
        "action_feedback_validation": read_json(ACTION_FEEDBACK_VALIDATION_PATH),
        "action_feedback_queue": read_csv(ACTION_FEEDBACK_QUEUE_PATH),
        "action_feedback_outcomes": read_csv(ACTION_FEEDBACK_OUTCOMES_PATH),
        "action_feedback_signal": read_json(ACTION_FEEDBACK_SIGNAL_PATH),
    }


def action_feedback_metrics(ctx: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Yo mido si el sistema cerró el ciclo entre alerta, acción, resultado y aprendizaje.
    """
    manifest = ctx.get("action_feedback_manifest") or {}
    validation = ctx.get("action_feedback_validation") or {}
    queue: pd.DataFrame = ctx.get("action_feedback_queue", pd.DataFrame())
    outcomes: pd.DataFrame = ctx.get("action_feedback_outcomes", pd.DataFrame())
    signal = ctx.get("action_feedback_signal") or {}
    p0 = int((queue.get("prioridad", pd.Series(dtype=str)) == "P0").sum()) if not queue.empty else 0
    p1 = int((queue.get("prioridad", pd.Series(dtype=str)) == "P1").sum()) if not queue.empty else 0
    value_total = safe_float(pd.to_numeric(queue.get("valor_esperado_en_riesgo", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if not queue.empty else 0.0
    feedback_events = int((manifest.get("counts") or {}).get("feedback_events", 0)) if isinstance(manifest, dict) else 0
    return {
        "metric_group": "action_feedback",
        "status": "ok" if validation.get("status", "ok") == "ok" and not queue.empty else "warning",
        "queue_rows": int(len(queue)),
        "p0_actions": p0,
        "p1_actions": p1,
        "feedback_events": feedback_events,
        "outcome_rows": int(len(outcomes)),
        "value_at_risk_in_queue": value_total,
        "retraining_recommendation": signal.get("recommendation", "sin_signal"),
        "should_retrain_or_recalibrate": bool(signal.get("should_retrain_or_recalibrate", False)),
        "privacy_status": validation.get("status", "unknown"),
        "decision": "Yo uso esta familia para medir si las alertas realmente se convierten en acciones, resultados y aprendizaje.",
    }


def risk_metrics(ctx: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Yo calculo P0/P1, valor en riesgo y SLA porque riesgo sin prioridad operativa no cambia decisiones.
    """
    ranking: pd.DataFrame = ctx["ranking"]
    public_payload = ctx["public_payload"] or {}
    thresholds = cfg.get("thresholds", {}).get("risk", {})
    risk_col = find_column(ranking, ["riesgo_caida", "riesgo", "risk_score", "probabilidad_caida"])
    value_col = find_column(ranking, ["valor_esperado_en_riesgo", "valor_riesgo", "expected_value_at_risk"])
    priority_col = find_column(ranking, ["prioridad_operativa", "prioridad", "priority", "nivel_riesgo", "nivel_prioridad"])

    if not ranking.empty and risk_col:
        scores = pd.to_numeric(ranking[risk_col], errors="coerce").fillna(0)
        p0 = int((scores >= safe_float(thresholds.get("p0_score", 0.70))).sum())
        p1 = int(((scores >= safe_float(thresholds.get("p1_score", 0.50))) & (scores < safe_float(thresholds.get("p0_score", 0.70)))).sum())
        p2 = int(((scores >= safe_float(thresholds.get("p2_score", 0.35))) & (scores < safe_float(thresholds.get("p1_score", 0.50)))).sum())
        risk_mean = safe_float(scores.mean())
        risk_p90 = safe_float(scores.quantile(0.90))
    else:
        p0p1 = public_payload.get("p0_p1", {})
        p0 = int((p0p1 or {}).get("operaciones", 0)) if isinstance(p0p1, dict) else int(safe_float(p0p1))
        p1 = 0
        p2 = 0
        risk_mean = safe_float(public_payload.get("riesgo_promedio"))
        risk_p90 = 0.0

    value_total = 0.0
    if not ranking.empty and value_col:
        value_total = safe_float(pd.to_numeric(ranking[value_col], errors="coerce").fillna(0).sum())
    else:
        value_total = safe_float(public_payload.get("valor_total_en_riesgo"))

    return {
        "metric_group": "risk",
        "status": "ok" if p0 + p1 + p2 > 0 else "warning",
        "total_operaciones": int(len(ranking)) if not ranking.empty else int(public_payload.get("total_operaciones", 0)),
        "p0_intervenir_hoy": p0,
        "p1_24h": p1,
        "p2_72h": p2,
        "p0_p1_total": p0 + p1,
        "valor_total_en_riesgo": round(value_total, 2),
        "riesgo_promedio": round(risk_mean, 4),
        "riesgo_p90": round(risk_p90, 4),
        "sla": {
            "p0_hours": thresholds.get("sla_p0_hours", 0),
            "p1_hours": thresholds.get("sla_p1_hours", 24),
            "p2_hours": thresholds.get("sla_p2_hours", 72),
        },
        "decision": "Yo priorizo P0/P1 por valor esperado en riesgo y obligo feedback de intervención.",
    }


def funnel_metrics(ctx: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Yo calculo tasas de etapa con mart real cuando existe; si no, declaro el proxy.
    """
    mart: pd.DataFrame = ctx.get("mart_funnel", pd.DataFrame())
    if not mart.empty and "leads" in mart.columns:
        totals = mart.sum(numeric_only=True)
        leads = safe_float(totals.get("leads"))
        sep = safe_float(totals.get("separaciones"))
        minu = safe_float(totals.get("minutas"))
        caidas = safe_float(totals.get("caidas"))
        return {
            "metric_group": "funnel",
            "status": "ok",
            "metric_mode": "official_or_real_mart",
            "leads": int(leads),
            "separaciones": int(sep),
            "minutas": int(minu),
            "caidas": int(caidas),
            "lead_to_separacion_rate": round(sep / leads, 6) if leads else 0.0,
            "separacion_to_minuta_rate": round(minu / sep, 6) if sep else 0.0,
            "separacion_to_caida_rate": round(caidas / sep, 6) if sep else 0.0,
            "canales_observados": int(mart["canal"].nunique()) if "canal" in mart.columns else 0,
            "periodos_observados": int(mart["periodo_mes"].nunique()) if "periodo_mes" in mart.columns else 0,
            "decision": "Yo uso tasas reales por etapa para decidir dónde está el cuello de botella comercial.",
        }
    training: pd.DataFrame = ctx["training"]
    ranking: pd.DataFrame = ctx["ranking"]
    target_col = find_column(training, ["caida_30d", "target", "cae_30d"])
    channel_col = find_column(training, ["canal_agrupado", "canal", "medio_captacion"])
    project_col = find_column(training, ["proyecto", "project"])
    target_rate = safe_float(pd.to_numeric(training[target_col], errors="coerce").mean()) if target_col else 0.0
    return {
        "metric_group": "funnel",
        "status": "proxy" if len(ranking) else "warning",
        "metric_mode": "proxy_from_training_or_scoring",
        "training_snapshots": int(len(training)),
        "scoring_operaciones_actuales": int(len(ranking)),
        "caida_rate_historica": round(target_rate, 4),
        "retencion_proxy": round(1 - target_rate, 4) if target_rate else 0.0,
        "canales_observados": int(training[channel_col].nunique()) if channel_col else 0,
        "proyectos_observados": int(training[project_col].nunique()) if project_col else 0,
        "decision": "Yo marco proxy cuando no existe mart real de funnel.",
    }


def stock_pricing_metrics(ctx: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Yo calculo stock, valorización, absorción y precio/m² con marts reales cuando están disponibles.
    """
    stock: pd.DataFrame = ctx.get("mart_stock", pd.DataFrame())
    pricing: pd.DataFrame = ctx.get("mart_pricing", pd.DataFrame())
    market_project: pd.DataFrame = ctx.get("mart_market_project", pd.DataFrame())
    if not stock.empty and "stock_total" in stock.columns:
        stock_total = safe_float(pd.to_numeric(stock.get("stock_total", pd.Series(dtype=float)), errors="coerce").sum())
        stock_disp = safe_float(pd.to_numeric(stock.get("stock_disponible", pd.Series(dtype=float)), errors="coerce").sum())
        stock_vendido = safe_float(pd.to_numeric(stock.get("stock_vendido", pd.Series(dtype=float)), errors="coerce").sum())
        stock_val = safe_float(pd.to_numeric(stock.get("stock_valorizado", pd.Series(dtype=float)), errors="coerce").sum())
        price_m2 = safe_float(pd.to_numeric(pricing.get("precio_m2_calculado", pd.Series(dtype=float)), errors="coerce").mean()) if not pricing.empty else 0.0
        gap = safe_float(pd.to_numeric(market_project.get("brecha_precio_m2_pct", pd.Series(dtype=float)), errors="coerce").mean()) if not market_project.empty else 0.0
        return {
            "metric_group": "stock_pricing",
            "status": "ok",
            "metric_mode": "official_or_real_mart",
            "stock_total": int(stock_total),
            "stock_disponible": int(stock_disp),
            "stock_vendido": int(stock_vendido),
            "stock_valorizado": round(stock_val, 2),
            "absorcion_real_proxy": round(stock_vendido / stock_total, 6) if stock_total else 0.0,
            "unidades_con_precio_m2": int(len(pricing)) if not pricing.empty else 0,
            "precio_m2_promedio_interno": round(price_m2, 2),
            "brecha_precio_m2_promedio": round(gap, 4),
            "market_comparable_source": sorted(market_project.get("comparable_source", pd.Series(dtype=str)).dropna().astype(str).unique().tolist()) if not market_project.empty and "comparable_source" in market_project.columns else [],
            "decision": "Yo uso stock real, precio/m² y brecha de mercado para decidir pricing, campaña o foco de venta.",
        }
    ranking: pd.DataFrame = ctx["ranking"]
    market: pd.DataFrame = ctx["market"]
    thresholds = cfg.get("thresholds", {}).get("stock", {})
    pricing_thresholds = cfg.get("thresholds", {}).get("pricing", {})
    days_col = find_column(ranking, ["dias_en_tuberia", "dias_stock", "days_in_stock"])
    price_col = find_column(ranking, ["precio_departamento", "precio", "price"])
    discount_col = find_column(ranking, ["descuento_pct", "discount_pct"])
    days = pd.to_numeric(ranking[days_col], errors="coerce").fillna(0) if days_col else pd.Series(dtype=float)
    prices = pd.to_numeric(ranking[price_col], errors="coerce").fillna(0) if price_col else pd.Series(dtype=float)
    discounts = pd.to_numeric(ranking[discount_col], errors="coerce").fillna(0) if discount_col else pd.Series(dtype=float)
    return {
        "metric_group": "stock_pricing",
        "status": "proxy" if len(ranking) else "warning",
        "metric_mode": "proxy_from_ranking",
        "stock_proxy_operaciones": int(len(ranking)),
        "dias_promedio_en_tuberia_o_stock": round(safe_float(days.mean()), 2) if len(days) else 0.0,
        "stock_valorizado_proxy": round(safe_float(prices.sum()), 2) if len(prices) else 0.0,
        "precio_promedio_departamento": round(safe_float(prices.mean()), 2) if len(prices) else 0.0,
        "descuento_promedio": round(safe_float(discounts.mean()), 4) if len(discounts) else 0.0,
        "mercado_distritos_observados": int(market["distrito"].nunique()) if not market.empty and "distrito" in market.columns else 0,
        "decision": "Yo marco proxy cuando todavía no existe mart real de stock/pricing.",
    }


def cobranza_metrics(ctx: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Yo calculo avance de cobranza con mart real cuando existe y dejo de usar valor en riesgo como proxy.
    """
    mart: pd.DataFrame = ctx.get("mart_cobranza", pd.DataFrame())
    if not mart.empty and "valor_venta_total" in mart.columns:
        valor = safe_float(pd.to_numeric(mart.get("valor_venta_total", pd.Series(dtype=float)), errors="coerce").sum())
        pagado = safe_float(pd.to_numeric(mart.get("monto_pagado_total", pd.Series(dtype=float)), errors="coerce").sum())
        saldo = safe_float(pd.to_numeric(mart.get("saldo_pendiente_total", pd.Series(dtype=float)), errors="coerce").sum())
        return {
            "metric_group": "cobranza",
            "status": "ok" if pagado or saldo or valor else "requires_payment_mart",
            "metric_mode": "official_or_real_mart",
            "operaciones_cobranza": int(pd.to_numeric(mart.get("operaciones", pd.Series(dtype=float)), errors="coerce").sum()),
            "valor_venta_total": round(valor, 2),
            "monto_pagado_total": round(pagado, 2),
            "saldo_pendiente_total": round(saldo, 2),
            "avance_cobranza": round(pagado / valor, 6) if valor else 0.0,
            "source_status": sorted(mart.get("source_status", pd.Series(dtype=str)).dropna().astype(str).unique().tolist()) if "source_status" in mart.columns else [],
            "decision": "Yo priorizo caja real: ventas con saldo pendiente y bajo avance de cobranza.",
        }
    dashboard_payload = ctx["dashboard_payload"] or {}
    kpis = dashboard_payload.get("kpis", {}) if isinstance(dashboard_payload, dict) else {}
    return {
        "metric_group": "cobranza",
        "status": "requires_payment_mart",
        "metric_mode": "proxy_from_risk_value",
        "saldo_en_riesgo_proxy": round(safe_float(kpis.get("valor_total_en_riesgo")), 2),
        "decision": "Yo no invento caja: si no existe mart de pagos, marco requerimiento.",
    }


def rag_metrics(ctx: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Yo traduzco RAGAS-like en una señal de calidad presentable para UNI y demo comercial.
    """
    ragas = ctx["ragas"]
    thresholds = cfg.get("thresholds", {}).get("rag", {})
    faith = safe_float(ragas.get("faithfulness_proxy_mean"))
    ans = safe_float(ragas.get("answer_relevance_proxy_mean"))
    cont = safe_float(ragas.get("context_relevance_proxy_mean"))
    traps = safe_float(ragas.get("trap_refusal_rate"))
    fails = []
    if faith < safe_float(thresholds.get("faithfulness_min", 0.75)): fails.append("faithfulness")
    if ans < safe_float(thresholds.get("answer_relevance_min", 0.75)): fails.append("answer_relevance")
    if cont < safe_float(thresholds.get("context_relevance_min", 0.60)): fails.append("context_relevance")
    if traps < safe_float(thresholds.get("trap_refusal_min", 1.0)): fails.append("trap_refusal")
    return {
        "metric_group": "rag",
        "status": "ok" if not fails else "warning",
        "faithfulness_proxy_mean": round(faith, 4),
        "answer_relevance_proxy_mean": round(ans, 4),
        "context_relevance_proxy_mean": round(cont, 4),
        "trap_refusal_rate": round(traps, 4),
        "failed_gates": fails,
        "decision": "Yo no presento el asistente como confiable si falla citas, relevancia o preguntas trampa.",
    }


def mlops_metrics(ctx: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Yo calculo drift, lift y champion/challenger para saber si el modelo debe seguir vivo o ser retado.
    """
    feature_drift = ctx["feature_drift"] or {}
    prediction_drift = ctx["prediction_drift"] or {}
    calibration = ctx["calibration"] or {}
    registry = ctx["registry"] or {}
    lift = ctx["lift_metrics"] or {}
    challengers: pd.DataFrame = ctx["challengers"]
    thresholds = cfg.get("thresholds", {}).get("mlops", {})
    champion = registry.get("champion", {}) if isinstance(registry, dict) else {}
    champion_metrics = champion.get("metrics", {}) if isinstance(champion, dict) else {}
    prediction_psi = safe_float(prediction_drift.get("prediction_psi"))
    drift_status = prediction_drift.get("status") or feature_drift.get("global_status") or "unknown"
    top_lift = safe_float(lift.get("top_decile_lift", champion_metrics.get("top_decile_lift", 0)))
    recall = safe_float(champion_metrics.get("recall", 0))
    retrain_reasons = []
    if prediction_psi >= safe_float(thresholds.get("prediction_psi_fail", 0.25)): retrain_reasons.append("prediction_psi_fail")
    if top_lift and top_lift < safe_float(thresholds.get("min_top_decile_lift", 1.2)): retrain_reasons.append("low_lift")
    if recall and recall < safe_float(thresholds.get("min_recall", 0.70)): retrain_reasons.append("low_recall")
    return {
        "metric_group": "mlops",
        "status": "retrain_recommended" if retrain_reasons else "ok",
        "champion_model_id": registry.get("current_champion", "unknown"),
        "champion_algorithm": champion.get("algorithm", "unknown") if isinstance(champion, dict) else "unknown",
        "registered_models": int(registry.get("n_registered_models", 0)) if isinstance(registry, dict) else int(len(challengers)),
        "prediction_psi": round(prediction_psi, 4),
        "drift_status": drift_status,
        "feature_drift_fail_count": int((feature_drift.get("feature_status_counts") or {}).get("fail", 0)) if isinstance(feature_drift, dict) else 0,
        "brier_score": round(safe_float(calibration.get("brier_score")), 4),
        "top_decile_lift": round(top_lift, 4),
        "champion_recall": round(recall, 4),
        "challengers_compared": int(len(challengers)) if not challengers.empty else 0,
        "retraining_reasons": retrain_reasons,
        "decision": "Yo reviso drift, lift y challenger antes de confiar ciegamente en el ranking operativo.",
    }


def market_metrics(ctx: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Yo resumo mercado usando mart proyecto vs mercado cuando existe; si no, marco fuente faltante.
    """
    project_market: pd.DataFrame = ctx.get("mart_market_project", pd.DataFrame())
    if not project_market.empty and "precio_m2_proyecto" in project_market.columns:
        return {
            "metric_group": "market",
            "status": "ok" if not project_market.get("comparable_source", pd.Series(dtype=str)).astype(str).str.contains("proxy|requires", case=False, regex=True).all() else "proxy",
            "metric_mode": "real_mart_project_vs_market",
            "proyectos_comparados": int(project_market["proyecto"].nunique()) if "proyecto" in project_market.columns else int(len(project_market)),
            "distritos": int(project_market["distrito"].nunique()) if "distrito" in project_market.columns else 0,
            "precio_m2_proyecto_promedio": round(safe_float(pd.to_numeric(project_market.get("precio_m2_proyecto", pd.Series(dtype=float)), errors="coerce").mean()), 2),
            "precio_m2_mercado_promedio": round(safe_float(pd.to_numeric(project_market.get("precio_m2_mercado", pd.Series(dtype=float)), errors="coerce").mean()), 2),
            "brecha_precio_m2_promedio": round(safe_float(pd.to_numeric(project_market.get("brecha_precio_m2_pct", pd.Series(dtype=float)), errors="coerce").mean()), 4),
            "comparable_source": sorted(project_market.get("comparable_source", pd.Series(dtype=str)).dropna().astype(str).unique().tolist()) if "comparable_source" in project_market.columns else [],
            "decision": "Yo uso brecha de precio/m² para distinguir problema de precio, producto o presión de mercado.",
        }
    market: pd.DataFrame = ctx["market"]
    if market.empty:
        return {"metric_group": "market", "status": "requires_market_data", "decision": "Yo necesito fuente de mercado para defender pricing frente a stock y absorción."}
    return {
        "metric_group": "market",
        "status": "proxy",
        "distritos": int(market["distrito"].nunique()) if "distrito" in market.columns else 0,
        "oferta_activa_total": int(pd.to_numeric(market.get("oferta_activa", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()),
        "precio_m2_mercado_promedio": round(safe_float(pd.to_numeric(market.get("precio_m2_mercado", pd.Series(dtype=float)), errors="coerce").mean()), 2),
        "decision": "Yo uso mercado como proxy hasta construir mart proyecto vs mercado.",
    }


def real_mart_metrics(ctx: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Yo resumo cobertura de marts reales para saber qué productos ya salieron del territorio proxy.
    """
    manifest = ctx.get("real_mart_manifest") or {}
    validation = ctx.get("real_mart_validation") or {}
    gap: pd.DataFrame = ctx.get("mart_proxy_gap", pd.DataFrame())
    marts = manifest.get("marts", []) if isinstance(manifest, dict) else []
    closed = int(gap.get("gap_closed", pd.Series(dtype=bool)).astype(bool).sum()) if not gap.empty and "gap_closed" in gap.columns else 0
    return {
        "metric_group": "real_marts",
        "status": "ok" if validation.get("status", "ok") == "ok" and marts else "warning",
        "marts_generados": int(len(marts)),
        "validation_status": validation.get("status", "unknown"),
        "gaps_cerrados": closed,
        "familias_con_mart": sorted([str(x.get("mart")) for x in marts if isinstance(x, dict)]),
        "safe_aggregate_only": bool(manifest.get("safe_aggregate_only", True)) if isinstance(manifest, dict) else True,
        "decision": "Yo uso este control para saber qué dashboard se defiende con mart real y cuál sigue requiriendo fuente oficial.",
    }


def public_privacy_metrics(ctx: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Yo valido que Railway vea agregados y no filas sensibles.
    """
    payload = ctx["public_payload"] or {}
    validation = ctx["privacy_validation"] or {}
    return {
        "metric_group": "public_privacy",
        "status": validation.get("status", "ok" if payload else "warning"),
        "data_mode": payload.get("data_mode", "unknown"),
        "total_operaciones_publicas": int(payload.get("total_operaciones", 0)) if isinstance(payload, dict) else 0,
        "campos_publicos": sorted(payload.keys()) if isinstance(payload, dict) else [],
        "privacy_errors": validation.get("errors", []) if isinstance(validation, dict) else [],
        "decision": "Yo sirvo solo payload público agregado en Railway y bloqueo fallback demo en producción.",
    }


def build_family_metrics() -> dict[str, Any]:
    """
    Yo construyo métricas específicas por familia de dashboard y dejo un artefacto central para el generador.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "families").mkdir(parents=True, exist_ok=True)
    cfg = load_yaml(METRICS_CONFIG_PATH)
    ctx = build_global_source_context()
    metrics = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "version": "v1.6_real_mart_expansion",
        "safe_aggregate_only": True,
        "families": {
            "executive": {"metric_group": "executive", "status": "ok", "decision": "Yo combino riesgo, RAG y MLOps para decidir qué debe revisar gerencia."},
            "commercial": funnel_metrics(ctx, cfg),
            "funnel": funnel_metrics(ctx, cfg),
            "risk": risk_metrics(ctx, cfg),
            "stock_pricing": stock_pricing_metrics(ctx, cfg),
            "cobranza": cobranza_metrics(ctx, cfg),
            "rag": rag_metrics(ctx, cfg),
            "modeling": mlops_metrics(ctx, cfg),
            "monitoring": mlops_metrics(ctx, cfg),
            "registry": mlops_metrics(ctx, cfg),
            "mlops": mlops_metrics(ctx, cfg),
            "market": market_metrics(ctx, cfg),
            "real_marts": real_mart_metrics(ctx, cfg),
            "feedback": {**real_mart_metrics(ctx, cfg), "metric_group": "feedback", "decision": "Yo uso feedback real agregado para cerrar el loop acción-resultado."},
            "action_feedback": action_feedback_metrics(ctx, cfg),
            "public": public_privacy_metrics(ctx, cfg),
            "alerts": {"metric_group": "alerts", "status": "ok" if ctx["alerts"] else "warning", "alerts_manifest_available": bool(ctx["alerts"]), "decision": "Yo convierto métricas en alerta ejecutiva, issue o artifact."},
        },
        "source_paths": {
            "ranking_csv": str(RANKING_CSV_PATH.relative_to(PROJECT_ROOT)),
            "training_csv": str(TRAINING_CSV_PATH.relative_to(PROJECT_ROOT)),
            "ragas_summary": str(RAGAS_SUMMARY_PATH.relative_to(PROJECT_ROOT)),
            "model_registry": str(MODEL_REGISTRY_METADATA_PATH.relative_to(PROJECT_ROOT)),
            "public_payload": str(PUBLIC_PAYLOAD_PATH.relative_to(PROJECT_ROOT)),
            "real_mart_manifest": str(REAL_MART_METADATA_PATH.relative_to(PROJECT_ROOT)),
        },
    }
    FAMILY_METRICS_JSON.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    write_metrics_markdown(metrics)
    return metrics


def metrics_for_family(family: str) -> dict[str, Any]:
    """
    Yo devuelvo la métrica especializada de una familia y genero el bundle si todavía no existe.
    """
    if not FAMILY_METRICS_JSON.exists():
        build_family_metrics()
    bundle = read_json(FAMILY_METRICS_JSON)
    families = bundle.get("families", {}) if isinstance(bundle, dict) else {}
    return families.get(family, families.get("executive", {}))


def metrics_for_dashboard(dashboard_id: str, family: str) -> dict[str, Any]:
    """
    Yo asigno métricas específicas a cada dashboard usando familia y palabras clave del identificador.
    """
    dashboard_id_l = str(dashboard_id).lower()
    if any(k in dashboard_id_l for k in ["funnel", "conversion", "lead", "separaciones", "minutas"]):
        return metrics_for_family("funnel")
    if any(k in dashboard_id_l for k in ["riesgo", "caida", "caídas", "tuberia", "valor_esperado"]):
        return metrics_for_family("risk")
    if any(k in dashboard_id_l for k in ["stock", "pricing", "precio", "descuento", "absorcion", "product_mix"]):
        return metrics_for_family("stock_pricing")
    if any(k in dashboard_id_l for k in ["cobranza", "pago", "caja", "cuota"]):
        return metrics_for_family("cobranza")
    if any(k in dashboard_id_l for k in ["rag", "text_to_sql", "corpus", "citation"]):
        return metrics_for_family("rag")
    if any(k in dashboard_id_l for k in ["feedback", "accion", "acción", "intervencion", "intervención", "action_feedback"]):
        return metrics_for_family("action_feedback")
    if any(k in dashboard_id_l for k in ["real_mart", "proxy_vs_official", "official_gap", "mart_expansion"]):
        return metrics_for_family("real_marts")
    if any(k in dashboard_id_l for k in ["drift", "lift", "registry", "calibration", "mlops", "model"]):
        return metrics_for_family("mlops")
    if "market" in dashboard_id_l or family == "market":
        return metrics_for_family("market")
    return metrics_for_family(family)


def markdown_value_table(metrics: dict[str, Any]) -> str:
    """
    Yo convierto métricas específicas en una tabla legible por gerencia y por el profesor evaluador.
    """
    if not metrics:
        return "_Sin métricas específicas disponibles._"
    rows = []
    for key, value in metrics.items():
        if isinstance(value, (dict, list)):
            value_text = json.dumps(value, ensure_ascii=False)[:500]
        else:
            value_text = str(value)
        rows.append(f"| `{key}` | {value_text} |")
    return "| Métrica | Valor |\n|---|---|\n" + "\n".join(rows)


def write_metrics_markdown(bundle: dict[str, Any]) -> Path:
    """
    Yo escribo un informe maestro para explicar qué inteligencia específica produce cada familia.
    """
    lines = [
        "# Dashboard Metrics Engine v1.5",
        "",
        "Yo calculo métricas específicas por familia para que el catálogo deje de heredar solo KPIs globales.",
        "",
        f"**Generado:** {bundle.get('generated_at')}  ",
        f"**Safe aggregate only:** {bundle.get('safe_aggregate_only')}",
        "",
    ]
    for family, metrics in sorted((bundle.get("families") or {}).items()):
        lines.append(f"## {family}")
        lines.append(markdown_value_table(metrics))
        lines.append("")
        family_path = OUTPUT_DIR / "families" / f"{family}.md"
        family_path.write_text(f"# Métricas familia: {family}\n\n" + markdown_value_table(metrics) + "\n", encoding="utf-8")
    ENGINE_REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    return ENGINE_REPORT_MD


def validate_dashboard_metrics() -> dict[str, Any]:
    """
    Yo valido que las familias críticas tengan métricas específicas y que no dependan solo del KPI global.
    """
    if not FAMILY_METRICS_JSON.exists():
        build_family_metrics()
    bundle = read_json(FAMILY_METRICS_JSON)
    families = bundle.get("families", {}) if isinstance(bundle, dict) else {}
    required = ["funnel", "risk", "stock_pricing", "cobranza", "rag", "mlops", "real_marts"]
    errors = []
    warnings = []
    for family in required:
        if family not in families:
            errors.append(f"Falta familia {family}")
        elif len(families[family].keys()) < 4:
            errors.append(f"Familia {family} tiene métricas insuficientes")
    if families.get("cobranza", {}).get("status") == "requires_payment_mart":
        warnings.append("Cobranza requiere mart de pagos para métricas reales de caja")
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": "ok" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "families_available": sorted(families.keys()),
    }
    VALIDATION_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def dashboard_metrics_metadata() -> dict[str, Any]:
    """
    Yo expongo metadata mínima para API y auditoría.
    """
    if not FAMILY_METRICS_JSON.exists():
        build_family_metrics()
    bundle = read_json(FAMILY_METRICS_JSON)
    validation = validate_dashboard_metrics()
    return {
        "version": bundle.get("version", "v1.5_dashboard_metrics_engine"),
        "generated_at": bundle.get("generated_at"),
        "families": sorted((bundle.get("families") or {}).keys()),
        "validation_status": validation.get("status"),
        "report_path": str(ENGINE_REPORT_MD.relative_to(PROJECT_ROOT)),
        "json_path": str(FAMILY_METRICS_JSON.relative_to(PROJECT_ROOT)),
    }
