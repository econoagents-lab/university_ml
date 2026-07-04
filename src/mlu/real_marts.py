from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.mlu.config import PROJECT_ROOT

CONFIG_PATH = PROJECT_ROOT / "config" / "real_mart_expansion.yml"
REAL_MART_DIR = PROJECT_ROOT / "data" / "processed" / "real_marts"
REPORT_DIR = PROJECT_ROOT / "reports" / "real_marts"
REAL_MART_METADATA_JSON = REPORT_DIR / "real_mart_manifest.json"
REAL_MART_REPORT_MD = REPORT_DIR / "REAL_MART_EXPANSION.md"
REAL_MART_VALIDATION_JSON = REPORT_DIR / "real_mart_validation.json"
PROXY_GAP_MD = REPORT_DIR / "PROXY_VS_OFFICIAL_GAP.md"

MART_FUNNEL = REAL_MART_DIR / "mart_funnel_stage_month.csv"
MART_COBRANZA = REAL_MART_DIR / "mart_cobranza_venta.csv"
MART_PAGOS_NO_ASIGNADOS = REAL_MART_DIR / "mart_pagos_no_asignados.csv"
MART_STOCK = REAL_MART_DIR / "mart_stock_inicial_mensual.csv"
MART_PRICING = REAL_MART_DIR / "mart_pricing_unit_m2.csv"
MART_MARKET = REAL_MART_DIR / "mart_project_vs_market.csv"
MART_FEEDBACK = REAL_MART_DIR / "mart_feedback_interventions.csv"
MART_PROXY_GAP = REAL_MART_DIR / "mart_proxy_vs_official_gap.csv"

RANKING_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "scoring" / "ranking_operaciones_riesgo_caida.csv"
TRAINING_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "gold" / "riesgo_caida_training_model_ready.csv"
MARKET_CONTEXT_CSV_PATH = PROJECT_ROOT / "data" / "market" / "gold" / "mart_market_district_month.csv"
FEEDBACK_TEMPLATE_CSV_PATH = PROJECT_ROOT / "data" / "feedback" / "feedback_log_template.csv"
FAMILY_METRICS_JSON = PROJECT_ROOT / "reports" / "dashboard_metrics" / "family_metrics.json"


def load_yaml(path: Path = CONFIG_PATH) -> dict[str, Any]:
    """
    Yo cargo la configuración de marts reales para que la lógica viva en contratos y no en magia oculta.
    """
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def read_json(path: Path) -> dict[str, Any]:
    """
    Yo leo JSON de forma tolerante porque algunos artefactos nacen después del pipeline.
    """
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def read_table(path: Path) -> pd.DataFrame:
    """
    Yo leo CSV o Parquet sin exponer datos crudos: la lectura solo alimenta agregados seguros.
    """
    if not path.exists():
        return pd.DataFrame()
    try:
        if path.suffix.lower() == ".parquet":
            return pd.read_parquet(path)
        if path.suffix.lower() in {".csv", ".txt"}:
            return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()
    return pd.DataFrame()


def source_roots() -> list[Path]:
    """
    Yo defino dónde puede vivir la data privada; en producción prefiero MLU_PRIVATE_DATA_DIR y jamás la copio al repositorio.
    """
    cfg = load_yaml()
    roots: list[Path] = []
    env_var = (cfg.get("source_policy") or {}).get("private_data_env_var", "MLU_PRIVATE_DATA_DIR")
    env_value = os.getenv(env_var)
    if env_value:
        roots.append(Path(env_value))
    for raw in (cfg.get("source_policy") or {}).get("allowed_source_dirs", []):
        roots.append(PROJECT_ROOT / raw)
    # Yo agrego ubicaciones internas de outputs seguros como fallback reproducible.
    roots.extend([
        PROJECT_ROOT / "data" / "processed" / "gold",
        PROJECT_ROOT / "data" / "processed" / "scoring",
        PROJECT_ROOT / "data" / "feedback",
        PROJECT_ROOT / "data" / "market" / "gold",
    ])
    return [root for root in roots if root.exists()]


def find_source(stem: str) -> Path | None:
    """
    Yo busco una fuente por nombre base sin amarrarme a CSV o Parquet.
    """
    candidates = [f"{stem}.parquet", f"{stem}.csv"]
    for root in source_roots():
        for name in candidates:
            direct = root / name
            if direct.exists():
                return direct
        for path in root.rglob("*"):
            if path.stem == stem and path.suffix.lower() in {".parquet", ".csv"}:
                return path
    return None


def load_source(stem: str, fallback: Path | None = None) -> tuple[pd.DataFrame, str]:
    """
    Yo cargo una fuente preferida y devuelvo también el modo de evidencia para que el reporte distinga real de fallback.
    """
    source = find_source(stem)
    if source:
        df = read_table(source)
        if not df.empty:
            return df, f"real_source:{source.name}"
    if fallback and fallback.exists():
        df = read_table(fallback)
        if not df.empty:
            return df, f"fallback:{fallback.name}"
    return pd.DataFrame(), "missing"


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """
    Yo encuentro columnas equivalentes porque Sperant, marts y reportes no siempre usan el mismo nombre.
    """
    normalized = {str(col).lower().strip(): col for col in df.columns}
    for candidate in candidates:
        key = candidate.lower().strip()
        if key in normalized:
            return normalized[key]
    return None


def numeric(series: pd.Series | Any) -> pd.Series:
    """
    Yo transformo montos, áreas y tasas a número para que la métrica sea operable.
    """
    if isinstance(series, pd.Series):
        return pd.to_numeric(series, errors="coerce").fillna(0)
    return pd.Series(dtype=float)


def to_month(series: pd.Series | Any) -> pd.Series:
    """
    Yo reduzco fechas a periodo mensual porque los dashboards ejecutivos necesitan grano comparable.
    """
    if not isinstance(series, pd.Series):
        return pd.Series(dtype="object")
    return pd.to_datetime(series, errors="coerce").dt.to_period("M").astype(str).fillna("sin_periodo")


def stable_hash(value: Any, prefix: str = "ID") -> str:
    """
    Yo convierto identificadores personales u operativos en IDs estables para poder medir sin exponer PII.
    """
    salt = os.getenv("MLU_HASH_SALT", "local-demo-salt-change-me")
    raw = f"{salt}|{str(value)}".encode("utf-8")
    return f"{prefix}_{hashlib.sha256(raw).hexdigest()[:10].upper()}"


def safe_project(value: Any) -> str:
    """
    Yo mantengo proyecto como dimensión comercial agregada; si falta, lo marco como sin proyecto.
    """
    text = str(value).strip() if value is not None else "sin_proyecto"
    return text if text and text.lower() not in {"nan", "none", "<na>"} else "sin_proyecto"


def write_csv(df: pd.DataFrame, path: Path) -> Path:
    """
    Yo escribo marts seguros en CSV para que Power BI, GitHub Actions, Railway y Colab los lean sin fricción.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    return path


def build_funnel_stage_month() -> dict[str, Any]:
    """
    Yo construyo un mart mensual de funnel usando fact_conversion_leads cuando existe; si no, uso entrenamiento/scoring como fallback trazable.
    """
    leads, mode = load_source("fact_conversion_leads")
    if leads.empty:
        leads, mode = load_source("riesgo_caida_training_model_ready", TRAINING_CSV_PATH)
    if leads.empty:
        ranking, mode = load_source("ranking_operaciones_riesgo_caida", RANKING_CSV_PATH)
        if ranking.empty:
            out = pd.DataFrame([{"periodo_mes": "sin_datos", "data_mode": "missing", "leads": 0, "separaciones": 0, "minutas": 0, "caidas": 0}])
            write_csv(out, MART_FUNNEL)
            return {"mart": "funnel", "status": "missing", "rows": 0, "mode": mode}
        date_col = find_column(ranking, ["fecha_separacion", "fecha_score", "fecha"])
        out = pd.DataFrame({"periodo_mes": to_month(ranking[date_col]) if date_col else "sin_periodo"})
        out["separaciones"] = 1
        grouped = out.groupby("periodo_mes", dropna=False).agg(separaciones=("separaciones", "sum")).reset_index()
        grouped["leads"] = 0
        grouped["minutas"] = 0
        grouped["caidas"] = 0
        grouped["lead_to_separacion_rate"] = 0.0
        grouped["separacion_to_minuta_rate"] = 0.0
        grouped["separacion_to_caida_rate"] = 0.0
        grouped["data_mode"] = mode
        write_csv(grouped, MART_FUNNEL)
        return {"mart": "funnel", "status": "proxy_from_ranking", "rows": int(len(grouped)), "mode": mode}

    date_col = find_column(leads, ["fecha_asignacion", "fecha_creacion", "fecha"])
    sep_col = find_column(leads, ["tiene_separacion", "n_separaciones"])
    firm_col = find_column(leads, ["tiene_firma", "n_firmas"])
    caida_col = find_column(leads, ["tiene_caida", "n_caidas"])
    channel_col = find_column(leads, ["agrupacion_medio_captacion", "canal_entrada", "medio_captacion", "canal"])
    work = pd.DataFrame()
    work["periodo_mes"] = to_month(leads[date_col]) if date_col else "sin_periodo"
    work["leads"] = 1
    work["separaciones"] = (numeric(leads[sep_col]) > 0).astype(int) if sep_col else 0
    work["minutas"] = (numeric(leads[firm_col]) > 0).astype(int) if firm_col else 0
    work["caidas"] = (numeric(leads[caida_col]) > 0).astype(int) if caida_col else 0
    work["canal"] = leads[channel_col].fillna("sin_canal").astype(str) if channel_col else "sin_canal"
    grouped = work.groupby(["periodo_mes", "canal"], dropna=False).agg(
        leads=("leads", "sum"),
        separaciones=("separaciones", "sum"),
        minutas=("minutas", "sum"),
        caidas=("caidas", "sum"),
    ).reset_index()
    grouped["lead_to_separacion_rate"] = (grouped["separaciones"] / grouped["leads"].replace(0, pd.NA)).fillna(0).round(6)
    grouped["separacion_to_minuta_rate"] = (grouped["minutas"] / grouped["separaciones"].replace(0, pd.NA)).fillna(0).round(6)
    grouped["separacion_to_caida_rate"] = (grouped["caidas"] / grouped["separaciones"].replace(0, pd.NA)).fillna(0).round(6)
    grouped["data_mode"] = mode
    write_csv(grouped, MART_FUNNEL)
    return {"mart": "funnel", "status": "ok", "rows": int(len(grouped)), "mode": mode}


def build_cobranza_venta() -> dict[str, Any]:
    """
    Yo construyo el mart oficial de cobranza con agregados por mes/proyecto y sin cliente, DNI, teléfono ni email.
    """
    ci, mode = load_source("fact_separacion_cuota_inicial")
    if ci.empty:
        ci, mode = load_source("procesos")
    if ci.empty:
        ranking, mode = load_source("ranking_operaciones_riesgo_caida", RANKING_CSV_PATH)
        price_col = find_column(ranking, ["precio_departamento", "precio_venta"])
        date_col = find_column(ranking, ["fecha_separacion", "fecha_score"])
        project_col = find_column(ranking, ["proyecto", "nombre_proyecto"])
        work = pd.DataFrame()
        work["periodo_mes"] = to_month(ranking[date_col]) if date_col else "sin_periodo"
        work["proyecto"] = ranking[project_col].map(safe_project) if project_col else "sin_proyecto"
        work["operaciones"] = 1
        work["valor_venta_total"] = numeric(ranking[price_col]) if price_col else 0
        work["monto_pagado_total"] = 0.0
        work["saldo_pendiente_total"] = work["valor_venta_total"]
        source_status = "proxy_from_ranking_requires_payment_source"
    else:
        date_col = find_column(ci, ["fecha_minuta", "fecha_firma", "fecha_inicio", "fecha_proforma", "fecha_separacion", "fecha_actualizacion"])
        project_col = find_column(ci, ["nombre_proyecto", "proyecto", "codigo_proyecto"])
        paid_col = find_column(ci, ["monto_pagado_cuota_inicial", "total_pagado", "monto_pagado", "pagado"])
        pending_col = find_column(ci, ["total_pendiente", "saldo_pendiente", "monto_pendiente"])
        value_col = find_column(ci, ["precio_venta", "precio_departamento", "precio_base_proforma", "valor_venta"])
        work = pd.DataFrame()
        work["periodo_mes"] = to_month(ci[date_col]) if date_col else "sin_periodo"
        work["proyecto"] = ci[project_col].map(safe_project) if project_col else "sin_proyecto"
        work["operaciones"] = 1
        work["valor_venta_total"] = numeric(ci[value_col]) if value_col else 0.0
        work["monto_pagado_total"] = numeric(ci[paid_col]) if paid_col else 0.0
        if pending_col:
            work["saldo_pendiente_total"] = numeric(ci[pending_col])
        else:
            work["saldo_pendiente_total"] = (work["valor_venta_total"] - work["monto_pagado_total"]).clip(lower=0)
        source_status = "ok" if paid_col or pending_col else "requires_payment_columns"

    grouped = work.groupby(["periodo_mes", "proyecto"], dropna=False).agg(
        operaciones=("operaciones", "sum"),
        valor_venta_total=("valor_venta_total", "sum"),
        monto_pagado_total=("monto_pagado_total", "sum"),
        saldo_pendiente_total=("saldo_pendiente_total", "sum"),
    ).reset_index()
    grouped["avance_cobranza"] = (grouped["monto_pagado_total"] / grouped["valor_venta_total"].replace(0, pd.NA)).fillna(0).round(6)
    grouped["data_mode"] = mode
    grouped["source_status"] = source_status
    write_csv(grouped, MART_COBRANZA)

    pagos_no_asignados = pd.DataFrame([{
        "periodo_mes": datetime.now().strftime("%Y-%m"),
        "pagos_no_asignados": 0,
        "monto_no_asignado": 0.0,
        "source_status": "requires_pagos_eventos_source",
        "data_mode": mode,
    }])
    write_csv(pagos_no_asignados, MART_PAGOS_NO_ASIGNADOS)
    return {"mart": "cobranza", "status": source_status, "rows": int(len(grouped)), "mode": mode}


def build_stock_inicial_mensual() -> dict[str, Any]:
    """
    Yo construyo stock por mes/proyecto/tipo usando unidades; si solo tengo snapshot actual, lo declaro como current_snapshot_real.
    """
    units, mode = load_source("unidades")
    if units.empty:
        stock, mode = load_source("product_stock_pricing")
        if stock.empty:
            out = pd.DataFrame([{"periodo_mes": datetime.now().strftime("%Y-%m"), "source_status": "missing_units_source"}])
            write_csv(out, MART_STOCK)
            return {"mart": "stock", "status": "missing_units_source", "rows": 0, "mode": mode}
        project_col = find_column(stock, ["nombre_proyecto", "proyecto"])
        type_col = find_column(stock, ["tipo_unidad"])
        state_col = find_column(stock, ["estado_comercial"])
        total_col = find_column(stock, ["total_unidades", "rows"])
        work = stock.copy()
        work["periodo_mes"] = datetime.now().strftime("%Y-%m")
        work["proyecto"] = work[project_col].map(safe_project) if project_col else "sin_proyecto"
        work["tipo_unidad"] = work[type_col].fillna("sin_tipo").astype(str) if type_col else "sin_tipo"
        work["estado_comercial"] = work[state_col].fillna("sin_estado").astype(str).str.lower() if state_col else "sin_estado"
        work["unidades"] = numeric(work[total_col]) if total_col else 0
    else:
        project_col = find_column(units, ["nombre_proyecto", "proyecto", "codigo_proyecto"])
        type_col = find_column(units, ["tipo_unidad", "tipo_unidad_principal"])
        state_col = find_column(units, ["estado_comercial", "estado"])
        date_col = find_column(units, ["fecha_actualizacion", "fecha_precio_actualizado", "fecha_inicio_venta"])
        price_col = find_column(units, ["precio_lista", "precio_venta", "precio_base_proforma"])
        area_col = find_column(units, ["area_total", "area_techada"])
        work = pd.DataFrame()
        work["periodo_mes"] = to_month(units[date_col]) if date_col else datetime.now().strftime("%Y-%m")
        work["proyecto"] = units[project_col].map(safe_project) if project_col else "sin_proyecto"
        work["tipo_unidad"] = units[type_col].fillna("sin_tipo").astype(str) if type_col else "sin_tipo"
        work["estado_comercial"] = units[state_col].fillna("sin_estado").astype(str).str.lower() if state_col else "sin_estado"
        work["unidades"] = 1
        work["precio_lista"] = numeric(units[price_col]) if price_col else 0
        work["area_total"] = numeric(units[area_col]) if area_col else 0
    grouped = work.groupby(["periodo_mes", "proyecto", "tipo_unidad"], dropna=False).agg(
        stock_total=("unidades", "sum"),
        stock_disponible=("estado_comercial", lambda s: int(s.astype(str).str.contains("disponible|libre", case=False, regex=True).sum())),
        stock_vendido=("estado_comercial", lambda s: int(s.astype(str).str.contains("vendido|venta", case=False, regex=True).sum())),
        stock_en_proceso=("estado_comercial", lambda s: int(s.astype(str).str.contains("proceso|separ", case=False, regex=True).sum())),
        stock_valorizado=("precio_lista", "sum") if "precio_lista" in work.columns else ("unidades", "sum"),
        area_total=("area_total", "sum") if "area_total" in work.columns else ("unidades", "sum"),
    ).reset_index()
    grouped["absorcion_real_proxy"] = (grouped["stock_vendido"] / grouped["stock_total"].replace(0, pd.NA)).fillna(0).round(6)
    grouped["metric_mode"] = "current_snapshot_real"
    grouped["data_mode"] = mode
    write_csv(grouped, MART_STOCK)
    return {"mart": "stock", "status": "ok", "rows": int(len(grouped)), "mode": mode}


def build_pricing_unit_m2() -> dict[str, Any]:
    """
    Yo construyo precio por m² usando área y precio reales, pero reemplazo código de unidad por hash estable.
    """
    units, mode = load_source("unidades")
    if units.empty:
        units, mode = load_source("proforma_unidad")
    if units.empty:
        out = pd.DataFrame(columns=["unit_id", "proyecto", "tipo_unidad", "estado_comercial", "precio", "area_m2", "precio_m2_calculado", "data_mode", "source_status"])
        write_csv(out, MART_PRICING)
        return {"mart": "pricing", "status": "missing_pricing_source", "rows": 0, "mode": mode}
    unit_col = find_column(units, ["codigo", "codigo_unidad", "nombre_unidad"])
    project_col = find_column(units, ["nombre_proyecto", "proyecto", "codigo_proyecto"])
    type_col = find_column(units, ["tipo_unidad", "tipo_unidad_principal"])
    price_col = find_column(units, ["precio_venta", "precio_lista", "precio_base_proforma"])
    area_col = find_column(units, ["area_total", "area_techada", "lista_metraje"])
    state_col = find_column(units, ["estado_comercial", "estado"])
    work = pd.DataFrame()
    work["unit_id"] = units[unit_col].map(lambda x: stable_hash(x, "UNIT")) if unit_col else [stable_hash(i, "UNIT") for i in range(len(units))]
    work["proyecto"] = units[project_col].map(safe_project) if project_col else "sin_proyecto"
    work["tipo_unidad"] = units[type_col].fillna("sin_tipo").astype(str) if type_col else "sin_tipo"
    work["estado_comercial"] = units[state_col].fillna("sin_estado").astype(str) if state_col else "sin_estado"
    work["precio"] = numeric(units[price_col]) if price_col else 0.0
    work["area_m2"] = numeric(units[area_col]) if area_col else 0.0
    work = work[work["area_m2"] > 0].copy()
    work["precio_m2_calculado"] = (work["precio"] / work["area_m2"].replace(0, pd.NA)).fillna(0).round(2)
    work["data_mode"] = mode
    work["source_status"] = "ok"
    write_csv(work, MART_PRICING)
    return {"mart": "pricing", "status": "ok", "rows": int(len(work)), "mode": mode}


def build_project_vs_market() -> dict[str, Any]:
    """
    Yo comparo proyecto contra mercado/distrito. Si no hay fuente externa exacta, uso benchmark interno y lo declaro.
    """
    projects, project_mode = load_source("proyectos")
    pricing = read_table(MART_PRICING)
    market, market_mode = load_source("mart_market_district_month", MARKET_CONTEXT_CSV_PATH)
    if projects.empty and pricing.empty:
        out = pd.DataFrame([{"periodo_mes": datetime.now().strftime("%Y-%m"), "source_status": "missing_project_market_sources"}])
        write_csv(out, MART_MARKET)
        return {"mart": "market", "status": "missing_project_market_sources", "rows": 0, "mode": "missing"}
    if not pricing.empty and "proyecto" in pricing.columns and "precio_m2_calculado" in pricing.columns:
        internal = pricing.groupby("proyecto", dropna=False).agg(
            precio_m2_proyecto=("precio_m2_calculado", "mean"),
            unidades_observadas=("unit_id", "nunique") if "unit_id" in pricing.columns else ("precio_m2_calculado", "size"),
        ).reset_index()
    else:
        internal = pd.DataFrame(columns=["proyecto", "precio_m2_proyecto", "unidades_observadas"])
    distrito_map = pd.DataFrame(columns=["proyecto", "distrito"])
    if not projects.empty:
        name_col = find_column(projects, ["nombre", "nombre_proyecto", "proyecto", "codigo"])
        district_col = find_column(projects, ["distrito", "zona"])
        if name_col:
            distrito_map["proyecto"] = projects[name_col].map(safe_project)
            distrito_map["distrito"] = projects[district_col].fillna("sin_distrito").astype(str) if district_col else "sin_distrito"
    out = internal.merge(distrito_map, on="proyecto", how="left") if not internal.empty else distrito_map.copy()
    out["distrito"] = out.get("distrito", pd.Series(dtype=str)).fillna("sin_distrito")
    if not market.empty and "distrito" in market.columns and "precio_m2_mercado" in market.columns:
        market_small = market.groupby("distrito", dropna=False).agg(precio_m2_mercado=("precio_m2_mercado", "mean"), oferta_activa=("oferta_activa", "sum") if "oferta_activa" in market.columns else ("precio_m2_mercado", "size")).reset_index()
        out = out.merge(market_small, on="distrito", how="left")
        comparable_source = "external_market_exact_or_partial"
    else:
        out["precio_m2_mercado"] = pd.NA
        out["oferta_activa"] = 0
        comparable_source = "internal_only_requires_market_source"
    if "precio_m2_proyecto" not in out.columns:
        out["precio_m2_proyecto"] = 0.0
    out["precio_m2_mercado"] = pd.to_numeric(out["precio_m2_mercado"], errors="coerce")
    if out["precio_m2_mercado"].isna().all() and not out["precio_m2_proyecto"].empty:
        out["precio_m2_mercado"] = out["precio_m2_proyecto"].mean()
        comparable_source = "internal_benchmark_proxy"
    out["brecha_precio_m2_pct"] = ((pd.to_numeric(out["precio_m2_proyecto"], errors="coerce") - out["precio_m2_mercado"]) / out["precio_m2_mercado"].replace(0, pd.NA)).fillna(0).round(6)
    out["periodo_mes"] = datetime.now().strftime("%Y-%m")
    out["comparable_source"] = comparable_source
    out["data_mode"] = f"projects={project_mode}; market={market_mode}"
    write_csv(out, MART_MARKET)
    return {"mart": "market", "status": "ok" if comparable_source.startswith("external") else "proxy", "rows": int(len(out)), "mode": comparable_source}


def build_feedback_interventions() -> dict[str, Any]:
    """
    Yo convierto feedback comercial en aprendizaje agregado sin publicar responsable real ni cliente.
    """
    feedback, mode = load_source("feedback_outcomes_merged")
    if feedback.empty:
        feedback, mode = load_source("feedback_log_template", FEEDBACK_TEMPLATE_CSV_PATH)
    if feedback.empty:
        out = pd.DataFrame([{"periodo_mes": datetime.now().strftime("%Y-%m"), "source_status": "missing_feedback_source", "intervenciones": 0}])
        write_csv(out, MART_FEEDBACK)
        return {"mart": "feedback", "status": "missing_feedback_source", "rows": 0, "mode": mode}
    date_col = find_column(feedback, ["fecha_accion", "fecha_score", "fecha"])
    action_col = find_column(feedback, ["accion_tomada", "accion", "action"])
    result_7_col = find_column(feedback, ["resultado_7d", "resultado"])
    result_30_col = find_column(feedback, ["resultado_30d", "outcome"])
    risk_col = find_column(feedback, ["nivel_riesgo", "prioridad", "priority"])
    resp_col = find_column(feedback, ["responsable", "asesor", "owner"])
    work = pd.DataFrame()
    work["periodo_mes"] = to_month(feedback[date_col]) if date_col else datetime.now().strftime("%Y-%m")
    work["accion_tomada"] = feedback[action_col].fillna("sin_accion").astype(str) if action_col else "sin_accion"
    work["resultado_7d"] = feedback[result_7_col].fillna("pendiente").astype(str) if result_7_col else "pendiente"
    work["resultado_30d"] = feedback[result_30_col].fillna("pendiente").astype(str) if result_30_col else "pendiente"
    work["nivel_riesgo"] = feedback[risk_col].fillna("sin_riesgo").astype(str) if risk_col else "sin_riesgo"
    work["responsable_id"] = feedback[resp_col].map(lambda x: stable_hash(x, "OWNER")) if resp_col else "OWNER_SIN_DATO"
    work["intervenciones"] = 1
    grouped = work.groupby(["periodo_mes", "accion_tomada", "resultado_7d", "resultado_30d", "nivel_riesgo", "responsable_id"], dropna=False).agg(intervenciones=("intervenciones", "sum")).reset_index()
    grouped["source_status"] = "ok"
    grouped["data_mode"] = mode
    write_csv(grouped, MART_FEEDBACK)
    return {"mart": "feedback", "status": "ok", "rows": int(len(grouped)), "mode": mode}


def build_proxy_vs_official_gap() -> dict[str, Any]:
    """
    Yo muestro qué familias ya tienen mart real y qué familias siguen en proxy para orientar el siguiente sprint.
    """
    old = read_json(FAMILY_METRICS_JSON)
    families = old.get("families", {}) if isinstance(old, dict) else {}
    mappings = [
        ("funnel", MART_FUNNEL),
        ("cobranza", MART_COBRANZA),
        ("stock_pricing", MART_STOCK),
        ("pricing", MART_PRICING),
        ("market", MART_MARKET),
        ("feedback", MART_FEEDBACK),
    ]
    rows = []
    for family, path in mappings:
        df = read_table(path)
        previous_status = (families.get(family) or {}).get("status", "unknown") if isinstance(families.get(family), dict) else "unknown"
        status = "official_mart_available" if not df.empty and not ("source_status" in df.columns and str(df["source_status"].iloc[0]).startswith("missing")) else "requires_source"
        rows.append({
            "family": family,
            "previous_metrics_status": previous_status,
            "new_mart_status": status,
            "mart_path": str(path.relative_to(PROJECT_ROOT)),
            "rows": int(len(df)),
            "gap_closed": status == "official_mart_available" and previous_status in {"proxy", "requires_payment_mart", "requires_market_data", "warning", "unknown"},
            "decision": "usar_mart_real" if status == "official_mart_available" else "conectar_fuente_real",
        })
    gap = pd.DataFrame(rows)
    write_csv(gap, MART_PROXY_GAP)
    lines = ["# Proxy vs Official Gap", "", "Yo comparo proxies antiguos contra marts reales para decidir qué métrica ya puede defenderse con evidencia dura.", ""]
    lines.append(gap.to_markdown(index=False))
    PROXY_GAP_MD.write_text("\n".join(lines), encoding="utf-8")
    return {"mart": "proxy_vs_official_gap", "status": "ok", "rows": int(len(gap)), "mode": "control"}


def build_all_real_marts() -> dict[str, Any]:
    """
    Yo construyo todos los marts reales seguros y dejo un manifiesto auditable.
    """
    REAL_MART_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    results = [
        build_funnel_stage_month(),
        build_cobranza_venta(),
        build_stock_inicial_mensual(),
        build_pricing_unit_m2(),
        build_project_vs_market(),
        build_feedback_interventions(),
    ]
    results.append(build_proxy_vs_official_gap())
    manifest = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "version": "v1.6_real_mart_expansion",
        "safe_aggregate_only": True,
        "private_data_copied_to_repo": False,
        "marts": results,
        "output_dir": str(REAL_MART_DIR.relative_to(PROJECT_ROOT)),
    }
    REAL_MART_METADATA_JSON.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_real_mart_report(manifest)
    return manifest


def forbidden_terms() -> list[str]:
    """
    Yo centralizo los nombres prohibidos para que los marts públicos o compartibles no filtren PII.
    """
    cfg = load_yaml()
    return [str(x).lower() for x in ((cfg.get("privacy") or {}).get("forbidden_output_columns") or [])]


def validate_no_pii_in_marts() -> dict[str, Any]:
    """
    Yo valido que ningún mart exportado contenga columnas sensibles ni patrones obvios de DNI, teléfono o email.
    """
    if not REAL_MART_METADATA_JSON.exists():
        build_all_real_marts()
    cfg = load_yaml()
    terms = forbidden_terms()
    patterns = [re.compile(p, flags=re.IGNORECASE) for p in ((cfg.get("privacy") or {}).get("forbidden_output_patterns") or [])]
    errors: list[str] = []
    warnings: list[str] = []
    for path in sorted(REAL_MART_DIR.glob("*.csv")):
        df = read_table(path)
        for col in df.columns:
            normalized = str(col).lower()
            if any(term == normalized or term in normalized for term in terms):
                errors.append(f"Columna prohibida en {path.name}: {col}")
        text_sample = df.head(25).astype(str).to_csv(index=False)
        for pattern in patterns:
            if pattern.search(text_sample):
                # Yo trato patrones como warning porque puede haber años o métricas; las columnas prohibidas sí son error.
                warnings.append(f"Patrón sensible posible en muestra de {path.name}: {pattern.pattern}")
    manifest = read_json(REAL_MART_METADATA_JSON)
    if not manifest:
        errors.append("No existe manifest de marts reales")
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": "ok" if not errors else "fail",
        "errors": errors,
        "warnings": warnings[:20],
        "mart_files": [str(p.relative_to(PROJECT_ROOT)) for p in sorted(REAL_MART_DIR.glob("*.csv"))],
    }
    REAL_MART_VALIDATION_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def write_real_mart_report(manifest: dict[str, Any]) -> Path:
    """
    Yo escribo el reporte ejecutivo de expansión de marts reales.
    """
    lines = [
        "# Real Mart Expansion v1.6",
        "",
        "Yo reemplazo proxies por marts reales seguros para que cada dashboard pueda defender una métrica con fuente, grano y modo de evidencia.",
        "",
        f"**Generado:** {manifest.get('generated_at')}  ",
        f"**Safe aggregate only:** {manifest.get('safe_aggregate_only')}  ",
        f"**Private data copied to repo:** {manifest.get('private_data_copied_to_repo')}",
        "",
        "## Marts generados",
        "",
        "| Mart | Estado | Filas | Modo |",
        "|---|---:|---:|---|",
    ]
    for item in manifest.get("marts", []):
        lines.append(f"| {item.get('mart')} | {item.get('status')} | {item.get('rows')} | {item.get('mode')} |")
    lines.extend([
        "",
        "## Política de privacidad",
        "",
        "No exporto cliente, documento, email, teléfono, dirección, credenciales ni filas operativas individuales. Cuando necesito trazabilidad por persona operativa, uso IDs hasheados estables.",
        "",
        "## Decisión económica",
        "",
        "Yo uso marts reales para separar lo que ya puede presentarse como evidencia dura de lo que todavía requiere una fuente oficial.",
    ])
    REAL_MART_REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    return REAL_MART_REPORT_MD


def real_mart_metadata() -> dict[str, Any]:
    """
    Yo expongo metadata mínima de marts reales para API y dashboards.
    """
    if not REAL_MART_METADATA_JSON.exists():
        build_all_real_marts()
    validation = validate_no_pii_in_marts()
    manifest = read_json(REAL_MART_METADATA_JSON)
    return {
        "version": manifest.get("version", "v1.6_real_mart_expansion"),
        "generated_at": manifest.get("generated_at"),
        "safe_aggregate_only": manifest.get("safe_aggregate_only"),
        "validation_status": validation.get("status"),
        "marts": manifest.get("marts", []),
        "report_path": str(REAL_MART_REPORT_MD.relative_to(PROJECT_ROOT)),
        "validation_path": str(REAL_MART_VALIDATION_JSON.relative_to(PROJECT_ROOT)),
    }
