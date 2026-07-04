from __future__ import annotations

import hashlib
import json
import math
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.mlu.config import PROJECT_ROOT

CONFIG_PATH = PROJECT_ROOT / "config" / "experimentation_causal_impact_lab.yml"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "experiments"
REPORT_DIR = PROJECT_ROOT / "reports" / "experiments"

EXPERIMENT_DESIGN_JSON = OUTPUT_DIR / "experiment_design.json"
ASSIGNMENT_CSV = OUTPUT_DIR / "experiment_assignment_safe.csv"
OUTCOMES_SAFE_CSV = OUTPUT_DIR / "experiment_outcomes_safe.csv"
IMPACT_SUMMARY_CSV = OUTPUT_DIR / "causal_impact_summary.csv"
IMPACT_SUMMARY_JSON = OUTPUT_DIR / "causal_impact_summary.json"
MANIFEST_JSON = REPORT_DIR / "causal_impact_manifest.json"
VALIDATION_JSON = REPORT_DIR / "causal_impact_validation.json"
REPORT_MD = REPORT_DIR / "EXPERIMENTATION_CAUSAL_IMPACT_LAB.md"

ACTION_QUEUE_CSV = PROJECT_ROOT / "data" / "processed" / "action_feedback" / "decision_action_queue_safe.csv"
FEEDBACK_EVENTS_SAFE_CSV = PROJECT_ROOT / "data" / "processed" / "action_feedback" / "feedback_events_safe.csv"


def load_yaml(path: Path = CONFIG_PATH) -> dict[str, Any]:
    """
    Yo cargo la configuración experimental para que el diseño causal no quede escondido en scripts.
    """
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def write_json(payload: dict[str, Any], path: Path) -> Path:
    """
    Yo escribo JSON auditable porque cada corrida debe dejar evidencia trazable.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def read_json(path: Path) -> dict[str, Any]:
    """
    Yo leo JSON sin romper el pipeline cuando todavía no existe el artefacto.
    """
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def read_table(path: Path) -> pd.DataFrame:
    """
    Yo leo CSV o Parquet porque mis laboratorios pueden producir artefactos en ambos formatos.
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


def normalize_text(value: Any, default: str = "sin_dato") -> str:
    """
    Yo normalizo texto para agrupar sin romper por nulos o valores ambiguos.
    """
    if value is None:
        return default
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "<na>"}:
        return default
    return text


def to_number(series: pd.Series | Any, default: float = 0.0) -> pd.Series:
    """
    Yo convierto columnas a número para calcular tasas, riesgo y valor esperado.
    """
    if isinstance(series, pd.Series):
        return pd.to_numeric(series, errors="coerce").fillna(default)
    return pd.Series(dtype=float)


def deterministic_fraction(value: Any, seed: int = 42) -> float:
    """
    Yo creo una pseudoaleatorización reproducible desde IDs seguros, sin usar datos personales.
    """
    raw = f"{seed}|{value}".encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()[:12]
    return int(digest, 16) / float(16 ** 12)


def risk_band(score: float, cfg: dict[str, Any]) -> str:
    """
    Yo traduzco riesgo continuo en bandas para estratificar el experimento.
    """
    bands = ((cfg.get("experiment") or {}).get("risk_bands") or {})
    if score >= float(bands.get("very_high", 0.70)):
        return "very_high"
    if score >= float(bands.get("high", 0.50)):
        return "high"
    if score >= float(bands.get("medium", 0.35)):
        return "medium"
    return "low"


def build_experiment_design() -> dict[str, Any]:
    """
    Yo defino el protocolo experimental antes de asignar operaciones, para no confundir operación con evidencia causal.
    """
    cfg = load_yaml()
    experiment = cfg.get("experiment") or {}
    outcomes = cfg.get("outcomes") or {}
    impact = cfg.get("impact") or {}
    design = {
        "version": "v1.8_experimentation_causal_impact_lab",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "experiment_id": experiment.get("id", "riesgo_caida_action_impact_v1"),
        "name": experiment.get("name", "Intervención comercial sobre riesgo de caída"),
        "objective": experiment.get("objective"),
        "unit_of_analysis": experiment.get("unit_of_analysis", "operation_id"),
        "eligible_priorities": experiment.get("eligible_priorities", ["P0", "P1"]),
        "assignment_method": experiment.get("assignment_method", "deterministic_hash_stratified"),
        "treatment_share": float(experiment.get("treatment_share", 0.70)),
        "ethical_policy": experiment.get("ethical_policy", {}),
        "primary_metric": outcomes.get("primary_metric", "negative_rate_30d"),
        "secondary_metrics": outcomes.get("secondary_metrics", []),
        "estimator": impact.get("estimator", "difference_in_means"),
        "confidence_note": impact.get("confidence_note"),
        "minimum_sample_per_arm": int(experiment.get("min_sample_size_per_arm", 10)),
        "privacy_mode": "safe_ids_only_no_pii",
    }
    write_json(design, EXPERIMENT_DESIGN_JSON)
    return design


def load_action_queue() -> pd.DataFrame:
    """
    Yo cargo la cola de acción segura; si no existe, intento regenerarla desde el laboratorio anterior.
    """
    df = read_table(ACTION_QUEUE_CSV)
    if not df.empty:
        return df
    try:
        from src.mlu.decision_action_feedback_lab import run_decision_action_feedback_lab
        run_decision_action_feedback_lab()
        return read_table(ACTION_QUEUE_CSV)
    except Exception:
        return pd.DataFrame()


def assign_treatment_control() -> dict[str, Any]:
    """
    Yo asigno tratamiento/control sobre IDs seguros para medir impacto sin exponer clientes ni códigos internos.
    """
    cfg = load_yaml()
    exp = cfg.get("experiment") or {}
    queue = load_action_queue()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if queue.empty:
        empty_cols = [
            "operation_id", "proyecto", "asesor_id", "canal", "prioridad", "riesgo_caida",
            "risk_band", "experiment_arm", "eligible", "holdout_reason", "valor_esperado_en_riesgo",
            "accion_recomendada", "assignment_score", "data_mode",
        ]
        pd.DataFrame(columns=empty_cols).to_csv(ASSIGNMENT_CSV, index=False, encoding="utf-8")
        return {"status": "missing_action_queue", "rows": 0, "artifact": str(ASSIGNMENT_CSV)}

    max_rows = int(exp.get("max_assignment_rows", 500))
    eligible_priorities = {str(x).upper() for x in exp.get("eligible_priorities", ["P0", "P1"])}
    treatment_share = float(exp.get("treatment_share", 0.70))
    seed = int(exp.get("random_seed", 42))
    ethical = exp.get("ethical_policy") or {}
    allow_holdout_for_p0 = bool(ethical.get("allow_holdout_for_p0", False))

    work = queue.copy().head(max_rows)
    if "riesgo_caida" not in work.columns:
        work["riesgo_caida"] = 0.0
    if "prioridad" not in work.columns:
        work["prioridad"] = "P3"
    if "valor_esperado_en_riesgo" not in work.columns:
        work["valor_esperado_en_riesgo"] = 0.0
    for col in ["operation_id", "proyecto", "asesor_id", "canal", "accion_recomendada", "data_mode"]:
        if col not in work.columns:
            work[col] = "sin_dato"

    work["riesgo_caida"] = to_number(work["riesgo_caida"]).round(6)
    work["valor_esperado_en_riesgo"] = to_number(work["valor_esperado_en_riesgo"]).round(2)
    work["risk_band"] = work["riesgo_caida"].map(lambda x: risk_band(float(x), cfg))
    work["eligible"] = work["prioridad"].astype(str).str.upper().isin(eligible_priorities)
    work["assignment_score"] = work["operation_id"].map(lambda x: round(deterministic_fraction(x, seed), 6))

    def choose_arm(row: pd.Series) -> str:
        priority = str(row.get("prioridad", "")).upper()
        if not bool(row.get("eligible", False)):
            return "not_eligible"
        if priority == "P0" and not allow_holdout_for_p0:
            return "treatment"
        return "treatment" if float(row.get("assignment_score", 1.0)) <= treatment_share else "control"

    work["experiment_arm"] = work.apply(choose_arm, axis=1)
    work["holdout_reason"] = ""
    work.loc[work["experiment_arm"] == "control", "holdout_reason"] = "holdout_control_para_medir_impacto"
    work.loc[work["experiment_arm"] == "not_eligible", "holdout_reason"] = "prioridad_no_elegible"
    work["experiment_id"] = exp.get("id", "riesgo_caida_action_impact_v1")
    work["assigned_at"] = datetime.now(timezone.utc).isoformat()

    safe_cols = [
        "experiment_id", "operation_id", "assigned_at", "proyecto", "asesor_id", "canal",
        "prioridad", "riesgo_caida", "risk_band", "valor_esperado_en_riesgo", "accion_recomendada",
        "eligible", "experiment_arm", "assignment_score", "holdout_reason", "data_mode",
    ]
    assignment = work[[c for c in safe_cols if c in work.columns]].copy()
    assignment.to_csv(ASSIGNMENT_CSV, index=False, encoding="utf-8")
    counts = assignment["experiment_arm"].value_counts().to_dict() if not assignment.empty else {}
    return {"status": "ok", "rows": int(len(assignment)), "arm_counts": counts, "artifact": str(ASSIGNMENT_CSV)}


def _outcome_class(value: Any, cfg: dict[str, Any]) -> str:
    """
    Yo clasifico resultados operativos en positivo, negativo o pendiente para estimar impacto.
    """
    text = normalize_text(value, default="pendiente").lower()
    outcomes = cfg.get("outcomes") or {}
    positive = {str(x).lower() for x in outcomes.get("positive_outcomes", [])}
    negative = {str(x).lower() for x in outcomes.get("negative_outcomes", [])}
    pending = {str(x).lower() for x in outcomes.get("pending_values", ["pendiente", ""])}
    if text in positive:
        return "positive"
    if text in negative:
        return "negative"
    if text in pending:
        return "pending"
    return "other"


def build_experiment_outcomes() -> dict[str, Any]:
    """
    Yo junto asignación y feedback para crear una tabla segura de resultados por brazo experimental.
    """
    cfg = load_yaml()
    assignment = read_table(ASSIGNMENT_CSV)
    if assignment.empty:
        assign_treatment_control()
        assignment = read_table(ASSIGNMENT_CSV)
    feedback = read_table(FEEDBACK_EVENTS_SAFE_CSV)
    if feedback.empty:
        try:
            from src.mlu.decision_action_feedback_lab import ingest_feedback_actions
            ingest_feedback_actions()
            feedback = read_table(FEEDBACK_EVENTS_SAFE_CSV)
        except Exception:
            feedback = pd.DataFrame()

    if assignment.empty:
        pd.DataFrame().to_csv(OUTCOMES_SAFE_CSV, index=False, encoding="utf-8")
        return {"status": "missing_assignment", "rows": 0, "artifact": str(OUTCOMES_SAFE_CSV)}

    if feedback.empty or "operation_id" not in feedback.columns:
        joined = assignment.copy()
        joined["accion_tomada"] = "pendiente"
        joined["resultado_7d"] = "pendiente"
        joined["resultado_30d"] = "pendiente"
        joined["caida_real_30d"] = ""
    else:
        keep = [c for c in ["operation_id", "fecha_accion", "accion_tomada", "resultado_7d", "resultado_30d", "caida_real_30d", "source_mode"] if c in feedback.columns]
        joined = assignment.merge(feedback[keep], on="operation_id", how="left")
        for col in ["accion_tomada", "resultado_7d", "resultado_30d", "caida_real_30d"]:
            if col not in joined.columns:
                joined[col] = "pendiente"
            joined[col] = joined[col].fillna("pendiente")

    joined["outcome_class_7d"] = joined["resultado_7d"].map(lambda x: _outcome_class(x, cfg))
    joined["outcome_class_30d"] = joined["resultado_30d"].map(lambda x: _outcome_class(x, cfg))
    joined["is_positive_30d"] = (joined["outcome_class_30d"] == "positive").astype(int)
    joined["is_negative_30d"] = (joined["outcome_class_30d"] == "negative").astype(int)
    joined["is_pending_30d"] = (joined["outcome_class_30d"] == "pending").astype(int)
    joined["treatment_contacted"] = (~joined["accion_tomada"].fillna("pendiente").astype(str).str.lower().isin({"pendiente", "", "nan"})).astype(int)
    joined["valor_esperado_en_riesgo"] = to_number(joined.get("valor_esperado_en_riesgo", pd.Series(dtype=float))).round(2)
    safe_cols = [
        "experiment_id", "operation_id", "proyecto", "asesor_id", "canal", "prioridad", "riesgo_caida", "risk_band",
        "valor_esperado_en_riesgo", "experiment_arm", "eligible", "accion_tomada", "resultado_7d", "resultado_30d",
        "outcome_class_7d", "outcome_class_30d", "is_positive_30d", "is_negative_30d", "is_pending_30d", "treatment_contacted",
    ]
    out = joined[[c for c in safe_cols if c in joined.columns]].copy()
    out.to_csv(OUTCOMES_SAFE_CSV, index=False, encoding="utf-8")
    return {"status": "ok", "rows": int(len(out)), "artifact": str(OUTCOMES_SAFE_CSV)}


def _safe_rate(num: float, den: float) -> float:
    """
    Yo calculo tasas sin dividir por cero.
    """
    return float(num / den) if den else 0.0


def evaluate_causal_impact() -> dict[str, Any]:
    """
    Yo estimo impacto descriptivo tratamiento vs control; declaro insuficiencia cuando no hay muestra real.
    """
    cfg = load_yaml()
    exp = cfg.get("experiment") or {}
    impact_cfg = cfg.get("impact") or {}
    min_n = int(exp.get("min_sample_size_per_arm", 10))
    outcomes = read_table(OUTCOMES_SAFE_CSV)
    if outcomes.empty:
        build_experiment_outcomes()
        outcomes = read_table(OUTCOMES_SAFE_CSV)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    arms = ["treatment", "control"]
    rows: list[dict[str, Any]] = []
    for arm in arms:
        arm_df = outcomes[outcomes.get("experiment_arm", pd.Series(dtype=str)).astype(str) == arm].copy() if not outcomes.empty else pd.DataFrame()
        n = int(len(arm_df))
        positive = int(to_number(arm_df.get("is_positive_30d", pd.Series(dtype=float))).sum()) if n else 0
        negative = int(to_number(arm_df.get("is_negative_30d", pd.Series(dtype=float))).sum()) if n else 0
        pending = int(to_number(arm_df.get("is_pending_30d", pd.Series(dtype=float))).sum()) if n else 0
        contacted = int(to_number(arm_df.get("treatment_contacted", pd.Series(dtype=float))).sum()) if n else 0
        value = float(to_number(arm_df.get("valor_esperado_en_riesgo", pd.Series(dtype=float))).sum()) if n else 0.0
        rows.append({
            "experiment_arm": arm,
            "n": n,
            "positive_30d": positive,
            "negative_30d": negative,
            "pending_30d": pending,
            "positive_rate_30d": round(_safe_rate(positive, n), 6),
            "negative_rate_30d": round(_safe_rate(negative, n), 6),
            "pending_rate_30d": round(_safe_rate(pending, n), 6),
            "contact_rate": round(_safe_rate(contacted, n), 6),
            "valor_esperado_en_riesgo": round(value, 2),
        })

    summary = pd.DataFrame(rows)
    t = summary[summary["experiment_arm"] == "treatment"].iloc[0].to_dict() if not summary.empty else {}
    c = summary[summary["experiment_arm"] == "control"].iloc[0].to_dict() if not summary.empty else {}
    positive_uplift = float(t.get("positive_rate_30d", 0)) - float(c.get("positive_rate_30d", 0))
    negative_reduction = float(c.get("negative_rate_30d", 0)) - float(t.get("negative_rate_30d", 0))
    treated_value = float(t.get("valor_esperado_en_riesgo", 0))
    saved_value_proxy = treated_value * max(0.0, negative_reduction)
    enough_sample = int(t.get("n", 0)) >= min_n and int(c.get("n", 0)) >= min_n
    has_observed_outcomes = (int(t.get("positive_30d", 0)) + int(t.get("negative_30d", 0)) + int(c.get("positive_30d", 0)) + int(c.get("negative_30d", 0))) > 0
    status = "estimated" if enough_sample and has_observed_outcomes else impact_cfg.get("insufficient_sample_status", "needs_more_feedback")

    delta_row = {
        "experiment_arm": "impact_delta",
        "n": int(t.get("n", 0)) + int(c.get("n", 0)),
        "positive_30d": int(t.get("positive_30d", 0)) - int(c.get("positive_30d", 0)),
        "negative_30d": int(c.get("negative_30d", 0)) - int(t.get("negative_30d", 0)),
        "pending_30d": int(t.get("pending_30d", 0)) + int(c.get("pending_30d", 0)),
        "positive_rate_30d": round(positive_uplift, 6),
        "negative_rate_30d": round(negative_reduction, 6),
        "pending_rate_30d": 0.0,
        "contact_rate": round(float(t.get("contact_rate", 0)) - float(c.get("contact_rate", 0)), 6),
        "valor_esperado_en_riesgo": round(saved_value_proxy, 2),
    }
    summary = pd.concat([summary, pd.DataFrame([delta_row])], ignore_index=True)
    summary.to_csv(IMPACT_SUMMARY_CSV, index=False, encoding="utf-8")
    payload = {
        "version": "v1.8_experimentation_causal_impact_lab",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "treatment_n": int(t.get("n", 0)),
        "control_n": int(c.get("n", 0)),
        "positive_uplift_pp": round(positive_uplift * 100, 3),
        "negative_reduction_pp": round(negative_reduction * 100, 3),
        "saved_value_proxy": round(saved_value_proxy, 2),
        "enough_sample": bool(enough_sample),
        "has_observed_outcomes": bool(has_observed_outcomes),
        "confidence_note": impact_cfg.get("confidence_note"),
        "recommendation": "seguir_recolectando_feedback" if status != "estimated" else "analizar_impacto_y_escalar_experimento",
    }
    write_json(payload, IMPACT_SUMMARY_JSON)
    return payload


def build_manifest() -> dict[str, Any]:
    """
    Yo construyo el manifiesto del laboratorio causal para que cada archivo sea rastreable.
    """
    assignment = read_table(ASSIGNMENT_CSV)
    outcomes = read_table(OUTCOMES_SAFE_CSV)
    summary = read_table(IMPACT_SUMMARY_CSV)
    impact = read_json(IMPACT_SUMMARY_JSON)
    design = read_json(EXPERIMENT_DESIGN_JSON)
    payload = {
        "version": "v1.8_experimentation_causal_impact_lab",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "experiment_id": design.get("experiment_id"),
        "status": impact.get("status", "not_evaluated"),
        "counts": {
            "assignment_rows": int(len(assignment)),
            "outcome_rows": int(len(outcomes)),
            "summary_rows": int(len(summary)),
        },
        "impact": impact,
        "artifacts": {
            "experiment_design_json": str(EXPERIMENT_DESIGN_JSON.relative_to(PROJECT_ROOT)),
            "assignment_csv": str(ASSIGNMENT_CSV.relative_to(PROJECT_ROOT)),
            "outcomes_safe_csv": str(OUTCOMES_SAFE_CSV.relative_to(PROJECT_ROOT)),
            "impact_summary_csv": str(IMPACT_SUMMARY_CSV.relative_to(PROJECT_ROOT)),
            "impact_summary_json": str(IMPACT_SUMMARY_JSON.relative_to(PROJECT_ROOT)),
            "report_md": str(REPORT_MD.relative_to(PROJECT_ROOT)),
        },
        "privacy_mode": "safe_ids_and_aggregates_only",
    }
    write_json(payload, MANIFEST_JSON)
    return payload


def validate_no_pii_in_outputs() -> dict[str, Any]:
    """
    Yo valido que el laboratorio causal no publique PII ni credenciales.
    """
    cfg = load_yaml()
    privacy = cfg.get("privacy") or {}
    forbidden_cols = {str(c).strip().lower() for c in privacy.get("forbidden_output_columns", [])}
    patterns = [re.compile(str(p), flags=re.IGNORECASE) for p in privacy.get("forbidden_output_patterns", [])]
    files = [EXPERIMENT_DESIGN_JSON, ASSIGNMENT_CSV, OUTCOMES_SAFE_CSV, IMPACT_SUMMARY_CSV, IMPACT_SUMMARY_JSON, REPORT_MD]
    errors: list[dict[str, Any]] = []
    for path in files:
        if not path.exists():
            errors.append({"path": str(path), "issue": "missing"})
            continue
        if path.suffix == ".csv":
            df = read_table(path)
            bad_cols = sorted({str(c).strip().lower() for c in df.columns} & forbidden_cols)
            if bad_cols:
                errors.append({"path": str(path.relative_to(PROJECT_ROOT)), "issue": "forbidden_columns", "columns": bad_cols})
            text_cols = [c for c in df.columns if df[c].dtype == "object"]
            sample_text = df[text_cols].head(100).to_csv(index=False) if text_cols else ""
        else:
            sample_text = path.read_text(encoding="utf-8")[:30000]
        for pattern in patterns:
            if sample_text and pattern.search(sample_text):
                errors.append({"path": str(path.relative_to(PROJECT_ROOT)), "issue": "forbidden_pattern", "pattern": pattern.pattern})
    payload = {
        "version": "v1.8_experimentation_causal_impact_lab",
        "status": "ok" if not errors else "fail",
        "errors": errors,
        "checked_files": [str(p.relative_to(PROJECT_ROOT)) for p in files],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json(payload, VALIDATION_JSON)
    return payload


def generate_report() -> Path:
    """
    Yo genero el reporte ejecutivo que explica si la intervención comercial tiene evidencia de impacto.
    """
    manifest = build_manifest()
    design = read_json(EXPERIMENT_DESIGN_JSON)
    impact = read_json(IMPACT_SUMMARY_JSON)
    assignment = read_table(ASSIGNMENT_CSV)
    summary = read_table(IMPACT_SUMMARY_CSV)
    arm_counts = assignment.get("experiment_arm", pd.Series(dtype=str)).value_counts().to_dict() if not assignment.empty else {}
    p0_treatment = 0
    if not assignment.empty and {"prioridad", "experiment_arm"}.issubset(assignment.columns):
        p0_treatment = int(((assignment["prioridad"].astype(str).str.upper() == "P0") & (assignment["experiment_arm"] == "treatment")).sum())
    lines = [
        "# Experimentation Causal Impact Lab · v1.8",
        "",
        "## Escena ejecutiva",
        "Yo convierto la cola de riesgo en un experimento operativo: tratamiento, control, resultado y aprendizaje económico.",
        "",
        "## Diseño experimental",
        f"- Experimento: **{design.get('experiment_id', 'sin_id')}**",
        f"- Unidad de análisis: **{design.get('unit_of_analysis', 'operation_id')}**",
        f"- Método de asignación: **{design.get('assignment_method', 'sin_metodo')}**",
        f"- Métrica principal: **{design.get('primary_metric', 'negative_rate_30d')}**",
        f"- Nota de confianza: {design.get('confidence_note', 'MVP descriptivo')}",
        "",
        "## Asignación",
        f"- Filas asignadas: **{manifest.get('counts', {}).get('assignment_rows', 0)}**",
        f"- Brazos: **{arm_counts}**",
        f"- P0 en tratamiento obligatorio: **{p0_treatment}**",
        "",
        "## Impacto estimado",
        f"- Estado: **{impact.get('status', 'not_evaluated')}**",
        f"- Tratamiento n: **{impact.get('treatment_n', 0)}**",
        f"- Control n: **{impact.get('control_n', 0)}**",
        f"- Uplift positivo 30d: **{impact.get('positive_uplift_pp', 0)} pp**",
        f"- Reducción caída/pérdida 30d: **{impact.get('negative_reduction_pp', 0)} pp**",
        f"- Valor salvado proxy: **S/ {float(impact.get('saved_value_proxy', 0)):,.2f}**",
        f"- Recomendación: **{impact.get('recommendation', 'sin_recomendacion')}**",
        "",
        "## Tabla de resumen",
    ]
    if summary.empty:
        lines.append("Aún no hay resumen de impacto.")
    else:
        lines.append(summary.to_markdown(index=False))
    lines.extend([
        "",
        "## Interpretación económica",
        "Si tratamiento reduce la tasa negativa frente a control, el sistema puede estimar valor salvado. Si no hay muestra suficiente, la decisión correcta no es inventar impacto: es seguir capturando feedback.",
        "",
        "## Privacidad",
        "No exporto clientes, DNI, teléfonos, emails, direcciones, códigos de proforma/unidad ni credenciales. Trabajo con `operation_id` y `asesor_id` seguros.",
        "",
        "## Próxima acción",
        "Yo ejecutaría el experimento por cohortes semanales, completaría resultados 7d/30d y recién después movería presupuesto, SLA o política de intervención.",
    ])
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    return REPORT_MD


def run_experimentation_causal_impact_lab() -> dict[str, Any]:
    """
    Yo ejecuto el laboratorio completo: diseño, asignación, outcomes, impacto, reporte y validación anti-PII.
    """
    design = build_experiment_design()
    assignment = assign_treatment_control()
    outcomes = build_experiment_outcomes()
    impact = evaluate_causal_impact()
    report = generate_report()
    validation = validate_no_pii_in_outputs()
    manifest = read_json(MANIFEST_JSON)
    return {
        "design": design,
        "assignment": assignment,
        "outcomes": outcomes,
        "impact": impact,
        "report": str(report),
        "validation": validation,
        "manifest": manifest,
    }


def experimentation_metadata() -> dict[str, Any]:
    """
    Yo expongo metadata segura del laboratorio causal para API, dashboards y GitHub Actions.
    """
    if not MANIFEST_JSON.exists():
        run_experimentation_causal_impact_lab()
    return read_json(MANIFEST_JSON)
