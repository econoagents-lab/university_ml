from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.mlu.config import PROJECT_ROOT

CONFIG_PATH = PROJECT_ROOT / "config" / "decision_action_feedback_lab.yml"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "action_feedback"
REPORT_DIR = PROJECT_ROOT / "reports" / "action_feedback"

QUEUE_CSV = OUTPUT_DIR / "decision_action_queue_safe.csv"
ASSIGNMENT_TEMPLATE_CSV = OUTPUT_DIR / "action_assignment_template.csv"
FEEDBACK_EVENTS_SAFE_CSV = OUTPUT_DIR / "feedback_events_safe.csv"
OUTCOMES_CSV = OUTPUT_DIR / "action_outcomes_summary.csv"
RETRAINING_SIGNAL_JSON = OUTPUT_DIR / "retraining_signal.json"
MANIFEST_JSON = REPORT_DIR / "action_feedback_manifest.json"
REPORT_MD = REPORT_DIR / "DECISION_ACTION_FEEDBACK_LAB.md"
VALIDATION_JSON = REPORT_DIR / "action_feedback_validation.json"

RANKING_CSV = PROJECT_ROOT / "data" / "processed" / "scoring" / "ranking_operaciones_riesgo_caida.csv"
RANKING_PARQUET = PROJECT_ROOT / "data" / "processed" / "scoring" / "ranking_operaciones_riesgo_caida.parquet"
FEEDBACK_LOG = PROJECT_ROOT / "data" / "feedback" / "action_feedback_log.csv"
FEEDBACK_TEMPLATE = PROJECT_ROOT / "data" / "feedback" / "feedback_log_template.csv"
REAL_FEEDBACK_MART = PROJECT_ROOT / "data" / "processed" / "real_marts" / "mart_feedback_interventions.csv"
PUBLIC_PAYLOAD = PROJECT_ROOT / "reports" / "public" / "decision_dashboard_payload_public.json"


def load_yaml(path: Path = CONFIG_PATH) -> dict[str, Any]:
    """
    Yo cargo las reglas del laboratorio de acciones para no esconder decisiones operativas en el código.
    """
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def read_json(path: Path) -> dict[str, Any]:
    """
    Yo leo JSON de forma segura porque algunos artefactos pueden no existir en una primera corrida.
    """
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_json(payload: dict[str, Any], path: Path) -> Path:
    """
    Yo escribo JSON con indentación para que los artefactos sean auditables por humanos y máquinas.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def read_table(path: Path) -> pd.DataFrame:
    """
    Yo leo CSV o Parquet sin asumir formato único porque el CRM puede llegar por varios pipelines.
    """
    if not path.exists():
        return pd.DataFrame()
    try:
        if path.suffix.lower() == ".parquet":
            return pd.read_parquet(path)
        if path.suffix.lower() == ".csv":
            return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()
    return pd.DataFrame()


def source_roots() -> list[Path]:
    """
    Yo busco primero en la carpeta privada declarada por entorno y luego en rutas seguras del proyecto.
    """
    cfg = load_yaml()
    roots: list[Path] = []
    env_var = (cfg.get("source_policy") or {}).get("private_data_env_var", "MLU_PRIVATE_DATA_DIR")
    env_value = os.getenv(env_var)
    if env_value:
        roots.append(Path(env_value))
    for raw in (cfg.get("source_policy") or {}).get("allowed_source_dirs", []):
        roots.append(PROJECT_ROOT / raw)
    roots.extend([
        PROJECT_ROOT / "data" / "processed" / "scoring",
        PROJECT_ROOT / "data" / "processed" / "real_marts",
        PROJECT_ROOT / "data" / "feedback",
    ])
    return [root for root in roots if root.exists()]


def find_source(stem: str) -> Path | None:
    """
    Yo encuentro una fuente por nombre base para que el usuario pueda guardar parquets en una carpeta privada.
    """
    for root in source_roots():
        for suffix in [".parquet", ".csv"]:
            direct = root / f"{stem}{suffix}"
            if direct.exists():
                return direct
        try:
            for path in root.rglob("*"):
                if path.stem == stem and path.suffix.lower() in {".parquet", ".csv"}:
                    return path
        except OSError:
            continue
    return None


def load_source(stem: str, fallback: Path | None = None) -> tuple[pd.DataFrame, str]:
    """
    Yo cargo una fuente y devuelvo el modo de evidencia para declarar si viene de CRM real, fallback o ausencia.
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
    Yo encuentro columnas equivalentes para tolerar nombres distintos entre CRM, marts y plantillas.
    """
    normalized = {str(col).strip().lower(): col for col in df.columns}
    for candidate in candidates:
        key = candidate.strip().lower()
        if key in normalized:
            return normalized[key]
    return None


def numeric(series: pd.Series | Any) -> pd.Series:
    """
    Yo convierto series a número porque riesgo, valor y tasas deben calcularse sin ambigüedad.
    """
    if isinstance(series, pd.Series):
        return pd.to_numeric(series, errors="coerce").fillna(0)
    return pd.Series(dtype=float)


def clean_text(value: Any, default: str = "sin_dato") -> str:
    """
    Yo normalizo texto operacional sin dejar que valores nulos rompan agregaciones.
    """
    text = str(value).strip() if value is not None else default
    if not text or text.lower() in {"nan", "none", "<na>"}:
        return default
    return text


def stable_hash(value: Any, prefix: str = "ID") -> str:
    """
    Yo convierto identificadores operativos o personales en IDs estables para medir sin exponer identidad.
    """
    cfg = load_yaml()
    privacy = cfg.get("privacy") or {}
    salt = os.getenv(privacy.get("hash_salt_env_var", "MLU_HASH_SALT"), privacy.get("default_hash_salt", "local-demo-salt-change-me"))
    raw = f"{salt}|{str(value)}".encode("utf-8")
    return f"{prefix}_{hashlib.sha256(raw).hexdigest()[:10].upper()}"


def operation_hash(row: pd.Series) -> str:
    """
    Yo creo una llave segura de operación usando campos internos, pero jamás exporto esos campos crudos.
    """
    values = []
    for candidate in ["codigo_proforma", "codigo_unidad", "id_operacion", "operation_id"]:
        if candidate in row.index:
            values.append(str(row.get(candidate, "")))
    if not values:
        values = [str(row.name)]
    return stable_hash("|".join(values), prefix="OP")


def priority_from_score(score: float, cfg: dict[str, Any]) -> str:
    """
    Yo traduzco probabilidad en prioridad operativa porque el modelo debe terminar en acción, no en score.
    """
    thresholds = ((cfg.get("rules") or {}).get("priority_thresholds") or {})
    if score >= float(thresholds.get("p0", 0.70)):
        return "P0"
    if score >= float(thresholds.get("p1", 0.50)):
        return "P1"
    if score >= float(thresholds.get("p2", 0.35)):
        return "P2"
    return "P3"


def sla_from_priority(priority: str, cfg: dict[str, Any]) -> int:
    """
    Yo asigno SLA por prioridad para convertir riesgo en reloj operativo.
    """
    sla = ((cfg.get("rules") or {}).get("sla_hours") or {})
    return int(sla.get(priority.lower(), sla.get(priority, 168)))


def action_from_priority(priority: str, cfg: dict[str, Any]) -> str:
    """
    Yo asigno una acción recomendada según prioridad para que el asesor sepa qué hacer.
    """
    catalog = ((cfg.get("rules") or {}).get("action_catalog") or {})
    return str(catalog.get(priority.lower(), catalog.get(priority, "Seguimiento regular.")))


def build_decision_action_queue() -> dict[str, Any]:
    """
    Yo construyo una cola segura de acciones desde el ranking de riesgo, sin clientes ni códigos crudos.
    """
    cfg = load_yaml()
    ranking, mode = load_source("ranking_operaciones_riesgo_caida", RANKING_CSV)
    if ranking.empty and RANKING_PARQUET.exists():
        ranking = read_table(RANKING_PARQUET)
        mode = "fallback:ranking_operaciones_riesgo_caida.parquet" if not ranking.empty else mode

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if ranking.empty:
        empty = pd.DataFrame(columns=[
            "operation_id", "fecha_score", "proyecto", "asesor_id", "canal", "riesgo_caida",
            "prioridad", "sla_horas", "valor_esperado_en_riesgo", "accion_recomendada", "data_mode",
        ])
        empty.to_csv(QUEUE_CSV, index=False, encoding="utf-8")
        return {"artifact": str(QUEUE_CSV), "rows": 0, "status": "missing_ranking", "data_mode": mode}

    risk_col = find_column(ranking, ["riesgo_caida", "riesgo", "risk_score", "probabilidad_caida"])
    value_col = find_column(ranking, ["valor_esperado_en_riesgo", "valor_riesgo", "expected_value_at_risk", "precio_departamento"])
    project_col = find_column(ranking, ["proyecto", "project"])
    advisor_col = find_column(ranking, ["asesor", "responsable", "advisor"])
    channel_col = find_column(ranking, ["canal_agrupado", "canal", "medio_captacion", "medio"])
    rank_col = find_column(ranking, ["ranking_prioridad", "rank", "ranking"])

    work = pd.DataFrame()
    work["operation_id"] = ranking.apply(operation_hash, axis=1)
    work["fecha_score"] = datetime.now(timezone.utc).date().isoformat()
    work["proyecto"] = ranking[project_col].map(clean_text) if project_col else "sin_proyecto"
    work["asesor_id"] = ranking[advisor_col].map(lambda x: stable_hash(x, prefix="ASESOR")) if advisor_col else "ASESOR_SIN_DATO"
    work["canal"] = ranking[channel_col].map(clean_text) if channel_col else "sin_canal"
    scores = numeric(ranking[risk_col]) if risk_col else pd.Series([0.0] * len(ranking))
    work["riesgo_caida"] = scores.round(6)
    work["prioridad"] = work["riesgo_caida"].map(lambda x: priority_from_score(float(x), cfg))
    work["sla_horas"] = work["prioridad"].map(lambda p: sla_from_priority(str(p), cfg))
    work["valor_esperado_en_riesgo"] = numeric(ranking[value_col]).round(2) if value_col else 0.0
    work["accion_recomendada"] = work["prioridad"].map(lambda p: action_from_priority(str(p), cfg))
    work["ranking_prioridad"] = numeric(ranking[rank_col]).astype(int) if rank_col else range(1, len(work) + 1)
    work["data_mode"] = mode
    work = work.sort_values(["prioridad", "riesgo_caida", "valor_esperado_en_riesgo"], ascending=[True, False, False])
    work.to_csv(QUEUE_CSV, index=False, encoding="utf-8")
    return {"artifact": str(QUEUE_CSV), "rows": int(len(work)), "status": "ok", "data_mode": mode}


def generate_action_assignment_template(limit: int | None = None) -> dict[str, Any]:
    """
    Yo genero una plantilla para que comercial registre acciones sin tocar datos personales.
    """
    cfg = load_yaml()
    queue = read_table(QUEUE_CSV)
    if queue.empty:
        build_decision_action_queue()
        queue = read_table(QUEUE_CSV)
    capacity = ((cfg.get("rules") or {}).get("daily_capacity") or {})
    default_limit = int(capacity.get("max_total_actions", 80))
    n = int(limit or default_limit)
    cols = ["operation_id", "fecha_score", "proyecto", "asesor_id", "canal", "riesgo_caida", "prioridad", "sla_horas", "valor_esperado_en_riesgo", "accion_recomendada"]
    template = queue[[c for c in cols if c in queue.columns]].head(n).copy() if not queue.empty else pd.DataFrame(columns=cols)
    template["accion_tomada"] = "pendiente"
    template["fecha_accion"] = ""
    template["resultado_7d"] = "pendiente"
    template["resultado_30d"] = "pendiente"
    template["caida_real_30d"] = ""
    template["comentario_operativo"] = ""
    template.to_csv(ASSIGNMENT_TEMPLATE_CSV, index=False, encoding="utf-8")
    return {"artifact": str(ASSIGNMENT_TEMPLATE_CSV), "rows": int(len(template)), "status": "ok"}


def _feedback_from_raw_template(df: pd.DataFrame) -> pd.DataFrame:
    """
    Yo convierto plantillas antiguas con códigos crudos en eventos seguros hasheados.
    """
    if df.empty:
        return pd.DataFrame()
    safe = pd.DataFrame()
    safe["operation_id"] = df.apply(operation_hash, axis=1)
    safe["fecha_accion"] = df.get("fecha_accion", "")
    safe["accion_tomada"] = df.get("accion_tomada", "pendiente")
    safe["resultado_7d"] = df.get("resultado_7d", "pendiente")
    safe["resultado_30d"] = df.get("resultado_30d", "pendiente")
    safe["caida_real_30d"] = df.get("caida_real_30d", "")
    safe["comentario_operativo"] = df.get("comentario", "")
    safe["source_mode"] = "raw_template_sanitized"
    return safe


def ingest_feedback_actions() -> dict[str, Any]:
    """
    Yo ingiero acciones registradas y exporto solo una versión segura para análisis y aprendizaje.
    """
    cfg = load_yaml()
    feedback, mode = load_source("action_feedback_log", FEEDBACK_LOG)
    if feedback.empty:
        feedback, mode = load_source("feedback_log_template", FEEDBACK_TEMPLATE)
    if feedback.empty and ASSIGNMENT_TEMPLATE_CSV.exists():
        feedback = read_table(ASSIGNMENT_TEMPLATE_CSV)
        mode = "fallback:action_assignment_template.csv"

    if feedback.empty:
        safe = pd.DataFrame(columns=["operation_id", "fecha_accion", "accion_tomada", "resultado_7d", "resultado_30d", "caida_real_30d", "comentario_operativo", "source_mode"])
    elif "operation_id" in feedback.columns:
        keep = ["operation_id", "fecha_accion", "accion_tomada", "resultado_7d", "resultado_30d", "caida_real_30d", "comentario_operativo"]
        safe = feedback[[c for c in keep if c in feedback.columns]].copy()
        safe["source_mode"] = mode
    else:
        safe = _feedback_from_raw_template(feedback)
        safe["source_mode"] = mode

    accepted = set(((cfg.get("rules") or {}).get("accepted_actions") or []))
    if "accion_tomada" in safe.columns and accepted:
        safe["accion_tomada"] = safe["accion_tomada"].fillna("pendiente").astype(str)
        safe.loc[~safe["accion_tomada"].isin(accepted), "accion_tomada"] = "pendiente"
    safe.to_csv(FEEDBACK_EVENTS_SAFE_CSV, index=False, encoding="utf-8")
    return {"artifact": str(FEEDBACK_EVENTS_SAFE_CSV), "rows": int(len(safe)), "status": "ok", "data_mode": mode}


def evaluate_action_outcomes() -> dict[str, Any]:
    """
    Yo evalúo si las acciones registradas terminaron en señales positivas, negativas o pendientes.
    """
    cfg = load_yaml()
    queue = read_table(QUEUE_CSV)
    feedback = read_table(FEEDBACK_EVENTS_SAFE_CSV)
    if queue.empty:
        build_decision_action_queue()
        queue = read_table(QUEUE_CSV)
    if feedback.empty:
        ingest_feedback_actions()
        feedback = read_table(FEEDBACK_EVENTS_SAFE_CSV)

    positive = set(((cfg.get("rules") or {}).get("positive_outcomes") or []))
    negative = set(((cfg.get("rules") or {}).get("negative_outcomes") or []))
    if feedback.empty:
        summary = pd.DataFrame([{"metric": "feedback_events", "value": 0, "status": "missing_feedback"}])
    else:
        joined = feedback.merge(queue[["operation_id", "prioridad", "riesgo_caida", "valor_esperado_en_riesgo"]], on="operation_id", how="left") if not queue.empty else feedback.copy()
        for col in ["resultado_7d", "resultado_30d"]:
            if col not in joined.columns:
                joined[col] = "pendiente"
        joined["is_positive_30d"] = joined["resultado_30d"].fillna("pendiente").astype(str).isin(positive).astype(int)
        joined["is_negative_30d"] = joined["resultado_30d"].fillna("pendiente").astype(str).isin(negative).astype(int)
        joined["is_pending_30d"] = ((joined["is_positive_30d"] == 0) & (joined["is_negative_30d"] == 0)).astype(int)
        summary = joined.groupby("prioridad", dropna=False).agg(
            feedback_events=("operation_id", "count"),
            positive_30d=("is_positive_30d", "sum"),
            negative_30d=("is_negative_30d", "sum"),
            pending_30d=("is_pending_30d", "sum"),
            avg_risk=("riesgo_caida", "mean"),
            value_at_risk=("valor_esperado_en_riesgo", "sum"),
        ).reset_index()
        summary["positive_rate_30d"] = (summary["positive_30d"] / summary["feedback_events"].replace(0, pd.NA)).fillna(0).round(6)
        summary["negative_rate_30d"] = (summary["negative_30d"] / summary["feedback_events"].replace(0, pd.NA)).fillna(0).round(6)
    OUTCOMES_CSV.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUTCOMES_CSV, index=False, encoding="utf-8")
    return {"artifact": str(OUTCOMES_CSV), "rows": int(len(summary)), "status": "ok"}


def build_retraining_signal() -> dict[str, Any]:
    """
    Yo traduzco feedback operativo en una señal de aprendizaje para decidir si conviene recalibrar o reentrenar.
    """
    cfg = load_yaml()
    learning = cfg.get("learning") or {}
    outcomes = read_table(OUTCOMES_CSV)
    feedback = read_table(FEEDBACK_EVENTS_SAFE_CSV)
    queue = read_table(QUEUE_CSV)
    feedback_events = int(len(feedback)) if not feedback.empty else 0
    min_events = int(learning.get("min_feedback_events_for_signal", 10))
    high_caida_rate = float(learning.get("high_caida_rate_threshold", 0.18))
    negative_rate = 0.0
    if not outcomes.empty and "negative_rate_30d" in outcomes.columns and "feedback_events" in outcomes.columns:
        total_events = pd.to_numeric(outcomes["feedback_events"], errors="coerce").fillna(0).sum()
        negative_events = (pd.to_numeric(outcomes.get("negative_30d", 0), errors="coerce").fillna(0)).sum()
        negative_rate = float(negative_events / total_events) if total_events else 0.0

    reasons: list[str] = []
    if feedback_events < min_events:
        reasons.append("feedback_insuficiente")
    if negative_rate >= high_caida_rate:
        reasons.append("tasa_caida_post_accion_alta")
    if not queue.empty and "prioridad" in queue.columns:
        p0_count = int((queue["prioridad"] == "P0").sum())
        if p0_count > int(((cfg.get("rules") or {}).get("daily_capacity") or {}).get("max_p0_actions", 25)):
            reasons.append("capacidad_p0_superada")
    should_retrain = feedback_events >= min_events and negative_rate >= high_caida_rate
    payload = {
        "version": "v1.7_decision_action_feedback_lab",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "feedback_events": feedback_events,
        "negative_rate_30d": round(negative_rate, 6),
        "should_retrain_or_recalibrate": bool(should_retrain),
        "recommendation": "recalibrar_o_reentrenar" if should_retrain else "continuar_recolectando_feedback",
        "reasons": reasons,
        "policy_path": learning.get("retraining_policy_path", "contracts/retraining_policy.yml"),
    }
    write_json(payload, RETRAINING_SIGNAL_JSON)
    return payload


def build_manifest() -> dict[str, Any]:
    """
    Yo construyo el manifiesto del laboratorio para que cada artefacto quede trazable.
    """
    queue = read_table(QUEUE_CSV)
    feedback = read_table(FEEDBACK_EVENTS_SAFE_CSV)
    outcomes = read_table(OUTCOMES_CSV)
    signal = read_json(RETRAINING_SIGNAL_JSON)
    payload = {
        "version": "v1.7_decision_action_feedback_lab",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifacts": {
            "queue_csv": str(QUEUE_CSV.relative_to(PROJECT_ROOT)),
            "assignment_template_csv": str(ASSIGNMENT_TEMPLATE_CSV.relative_to(PROJECT_ROOT)),
            "feedback_events_safe_csv": str(FEEDBACK_EVENTS_SAFE_CSV.relative_to(PROJECT_ROOT)),
            "outcomes_csv": str(OUTCOMES_CSV.relative_to(PROJECT_ROOT)),
            "retraining_signal_json": str(RETRAINING_SIGNAL_JSON.relative_to(PROJECT_ROOT)),
            "report_md": str(REPORT_MD.relative_to(PROJECT_ROOT)),
        },
        "counts": {
            "queue_rows": int(len(queue)),
            "feedback_events": int(len(feedback)),
            "outcome_rows": int(len(outcomes)),
        },
        "retraining_signal": signal,
        "privacy_mode": "aggregated_or_hashed_only",
    }
    write_json(payload, MANIFEST_JSON)
    return payload


def generate_report() -> Path:
    """
    Yo genero un reporte ejecutivo para explicar qué acciones existen, qué feedback volvió y qué aprendizaje se activa.
    """
    manifest = build_manifest()
    queue = read_table(QUEUE_CSV)
    outcomes = read_table(OUTCOMES_CSV)
    signal = manifest.get("retraining_signal", {})
    p0 = int((queue.get("prioridad", pd.Series(dtype=str)) == "P0").sum()) if not queue.empty else 0
    p1 = int((queue.get("prioridad", pd.Series(dtype=str)) == "P1").sum()) if not queue.empty else 0
    value_total = float(pd.to_numeric(queue.get("valor_esperado_en_riesgo", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if not queue.empty else 0.0
    lines = [
        "# Decision Action Feedback Lab · v1.7",
        "",
        "## Escena ejecutiva",
        "Yo cierro el ciclo entre alerta, acción, responsable, resultado y aprendizaje.",
        "",
        "## Cola de decisión",
        f"- Operaciones en cola segura: **{manifest['counts']['queue_rows']}**",
        f"- P0: **{p0}**",
        f"- P1: **{p1}**",
        f"- Valor esperado en riesgo: **S/ {value_total:,.2f}**",
        "",
        "## Feedback registrado",
        f"- Eventos seguros de feedback: **{manifest['counts']['feedback_events']}**",
        f"- Filas de outcome: **{manifest['counts']['outcome_rows']}**",
        "",
        "## Resultado por prioridad",
    ]
    if outcomes.empty:
        lines.append("Sin outcomes disponibles todavía.")
    else:
        lines.append(outcomes.to_markdown(index=False))
    lines.extend([
        "",
        "## Señal de aprendizaje",
        f"- Recomendación: **{signal.get('recommendation', 'sin_signal')}**",
        f"- Reentrenar o recalibrar: **{signal.get('should_retrain_or_recalibrate', False)}**",
        f"- Razones: **{', '.join(signal.get('reasons', [])) or 'sin_alertas'}**",
        "",
        "## Privacidad",
        "No exporto clientes, DNI, teléfonos, emails, direcciones, códigos de proforma/unidad ni credenciales. Uso `operation_id` y `asesor_id` hasheados.",
        "",
        "## Próxima acción",
        "Yo usaría `action_assignment_template.csv` en la reunión comercial, completaría `accion_tomada`, `resultado_7d` y `resultado_30d`, y volvería a correr el pipeline.",
    ])
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    return REPORT_MD


def validate_no_pii_in_outputs() -> dict[str, Any]:
    """
    Yo valido que los artefactos del laboratorio no publiquen columnas o patrones sensibles.
    """
    cfg = load_yaml()
    privacy = cfg.get("privacy") or {}
    forbidden_cols = {str(c).lower() for c in privacy.get("forbidden_output_columns", [])}
    patterns = [re.compile(p, flags=re.IGNORECASE) for p in privacy.get("forbidden_output_patterns", [])]
    files = [QUEUE_CSV, ASSIGNMENT_TEMPLATE_CSV, FEEDBACK_EVENTS_SAFE_CSV, OUTCOMES_CSV, REPORT_MD]
    errors: list[dict[str, Any]] = []
    for path in files:
        if not path.exists():
            errors.append({"path": str(path), "issue": "missing"})
            continue
        if path.suffix == ".csv":
            df = read_table(path)
            bad_cols = sorted(set(str(c).lower() for c in df.columns) & forbidden_cols)
            if bad_cols:
                errors.append({"path": str(path), "issue": "forbidden_columns", "columns": bad_cols})
            # Yo reviso patrones sensibles solo en columnas de texto para no confundir montos o decimales con DNI.
            text_columns = [c for c in df.columns if df[c].dtype == "object"]
            sample_text = df[text_columns].head(50).to_csv(index=False) if text_columns else ""
        else:
            sample_text = path.read_text(encoding="utf-8")[:20000]
        for pattern in patterns:
            if sample_text and pattern.search(sample_text):
                errors.append({"path": str(path), "issue": "forbidden_pattern", "pattern": pattern.pattern})
    payload = {
        "version": "v1.7_decision_action_feedback_lab",
        "status": "ok" if not errors else "fail",
        "errors": errors,
        "checked_files": [str(p.relative_to(PROJECT_ROOT)) for p in files],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json(payload, VALIDATION_JSON)
    return payload


def run_decision_action_feedback_lab() -> dict[str, Any]:
    """
    Yo ejecuto el laboratorio completo: cola, plantilla, feedback seguro, outcomes, señal de aprendizaje y validación.
    """
    queue = build_decision_action_queue()
    template = generate_action_assignment_template()
    feedback = ingest_feedback_actions()
    outcomes = evaluate_action_outcomes()
    signal = build_retraining_signal()
    report = generate_report()
    validation = validate_no_pii_in_outputs()
    manifest = read_json(MANIFEST_JSON)
    return {
        "queue": queue,
        "template": template,
        "feedback": feedback,
        "outcomes": outcomes,
        "signal": signal,
        "report": str(report),
        "validation": validation,
        "manifest": manifest,
    }


def action_feedback_metadata() -> dict[str, Any]:
    """
    Yo expongo metadata segura para API y dashboards sin abrir datos sensibles.
    """
    if not MANIFEST_JSON.exists():
        run_decision_action_feedback_lab()
    return read_json(MANIFEST_JSON)
