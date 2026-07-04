from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.mlu.config import PROJECT_ROOT

CONFIG_PATH = PROJECT_ROOT / "config" / "experiment_power_policy_engine.yml"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "policy_engine"
REPORT_DIR = PROJECT_ROOT / "reports" / "policy_engine"

POWER_JSON = OUTPUT_DIR / "experiment_power_analysis.json"
COMPLIANCE_CSV = OUTPUT_DIR / "treatment_compliance_summary.csv"
SEGMENT_IMPACT_CSV = OUTPUT_DIR / "segment_policy_impact.csv"
SLA_RECOMMENDATIONS_JSON = OUTPUT_DIR / "sla_capacity_recommendations.json"
ESCALATION_POLICY_JSON = OUTPUT_DIR / "escalation_policy.json"
MANIFEST_JSON = REPORT_DIR / "policy_engine_manifest.json"
VALIDATION_JSON = REPORT_DIR / "policy_engine_validation.json"
REPORT_MD = REPORT_DIR / "EXPERIMENT_POWER_AND_POLICY_ENGINE.md"

ASSIGNMENT_CSV = PROJECT_ROOT / "data" / "processed" / "experiments" / "experiment_assignment_safe.csv"
OUTCOMES_CSV = PROJECT_ROOT / "data" / "processed" / "experiments" / "experiment_outcomes_safe.csv"
IMPACT_SUMMARY_JSON = PROJECT_ROOT / "data" / "processed" / "experiments" / "causal_impact_summary.json"


def load_yaml(path: Path = CONFIG_PATH) -> dict[str, Any]:
    """
    Yo cargo la política experimental para separar decisión comercial de código operativo.
    """
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def write_json(payload: dict[str, Any], path: Path) -> Path:
    """
    Yo escribo JSON auditable para que cada recomendación de política tenga evidencia.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def read_json(path: Path) -> dict[str, Any]:
    """
    Yo leo JSON sin romper la fábrica cuando un artefacto aún no fue generado.
    """
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def read_table(path: Path) -> pd.DataFrame:
    """
    Yo leo tablas seguras del laboratorio experimental, nunca tablas con PII.
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


def to_number(series: pd.Series | Any, default: float = 0.0) -> pd.Series:
    """
    Yo convierto columnas a número para calcular tasas, cumplimiento e impacto.
    """
    if isinstance(series, pd.Series):
        return pd.to_numeric(series, errors="coerce").fillna(default)
    return pd.Series(dtype=float)


def safe_rate(num: float, den: float) -> float:
    """
    Yo calculo tasas sin dividir por cero.
    """
    return float(num / den) if den else 0.0


def ensure_experiment_outputs() -> None:
    """
    Yo regenero el laboratorio causal previo si faltan asignaciones o resultados seguros.
    """
    if ASSIGNMENT_CSV.exists() and OUTCOMES_CSV.exists():
        return
    try:
        from src.mlu.experimentation_causal_impact_lab import run_experimentation_causal_impact_lab
        run_experimentation_causal_impact_lab()
    except Exception:
        return


def compute_power_analysis() -> dict[str, Any]:
    """
    Yo estimo poder estadístico mínimo para saber si el experimento puede sostener una decisión comercial.
    """
    cfg = load_yaml()
    pwr = cfg.get("power_analysis") or {}
    ensure_experiment_outputs()
    assignment = read_table(ASSIGNMENT_CSV)
    outcomes = read_table(OUTCOMES_CSV)
    impact = read_json(IMPACT_SUMMARY_JSON)

    baseline = float(pwr.get("baseline_negative_rate", 0.15))
    mde_pp = float(pwr.get("minimum_detectable_effect_pp", 5.0))
    mde = max(mde_pp / 100.0, 0.0001)
    z_alpha = float(pwr.get("z_alpha_over_2", 1.96))
    z_power = float(pwr.get("z_power", 0.84))
    required_n = math.ceil(((z_alpha + z_power) ** 2) * 2 * baseline * (1 - baseline) / (mde ** 2))

    arm_counts = assignment.get("experiment_arm", pd.Series(dtype=str)).value_counts().to_dict() if not assignment.empty else {}
    treatment_n = int(arm_counts.get("treatment", 0))
    control_n = int(arm_counts.get("control", 0))
    observed_n_per_arm = min(treatment_n, control_n)
    power_ready = observed_n_per_arm >= required_n

    observed_negative_rate = baseline
    if not outcomes.empty and "is_negative_30d" in outcomes.columns:
        observed_negative_rate = float(to_number(outcomes["is_negative_30d"]).mean())
    se = math.sqrt(max(0.000001, 2 * observed_negative_rate * (1 - observed_negative_rate) / max(observed_n_per_arm, 1)))
    detectable_pp_current = round((z_alpha + z_power) * se * 100, 3)

    payload = {
        "version": "v1.9_experiment_power_and_policy_engine",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "alpha": float(pwr.get("alpha", 0.05)),
        "target_power": float(pwr.get("power", 0.80)),
        "baseline_negative_rate": round(baseline, 6),
        "minimum_detectable_effect_pp": round(mde_pp, 3),
        "required_n_per_arm": int(required_n),
        "observed_treatment_n": treatment_n,
        "observed_control_n": control_n,
        "observed_min_n_per_arm": int(observed_n_per_arm),
        "detectable_effect_pp_with_current_sample": detectable_pp_current,
        "power_ready": bool(power_ready),
        "impact_status": impact.get("status", "not_evaluated"),
        "decision": "listo_para_politica" if power_ready else "seguir_acumulando_muestra_y_feedback",
    }
    write_json(payload, POWER_JSON)
    return payload


def build_treatment_compliance() -> pd.DataFrame:
    """
    Yo mido si el equipo comercial ejecutó el tratamiento antes de exigir conclusiones causales.
    """
    cfg = load_yaml()
    comp = cfg.get("compliance") or {}
    ensure_experiment_outputs()
    assignment = read_table(ASSIGNMENT_CSV)
    outcomes = read_table(OUTCOMES_CSV)

    if assignment.empty:
        out = pd.DataFrame([{"metric": "assignment_rows", "value": 0, "target": 1, "status": "fail"}])
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        out.to_csv(COMPLIANCE_CSV, index=False, encoding="utf-8")
        return out

    rows: list[dict[str, Any]] = []
    treatment = assignment[assignment.get("experiment_arm", pd.Series(dtype=str)).astype(str) == "treatment"].copy()
    control = assignment[assignment.get("experiment_arm", pd.Series(dtype=str)).astype(str) == "control"].copy()
    p0 = assignment[assignment.get("prioridad", pd.Series(dtype=str)).astype(str).str.upper() == "P0"].copy()
    p0_t = p0[p0.get("experiment_arm", pd.Series(dtype=str)).astype(str) == "treatment"].copy()

    if outcomes.empty:
        outcomes = pd.DataFrame(columns=["experiment_arm", "treatment_contacted", "is_pending_30d"])
    tr_out = outcomes[outcomes.get("experiment_arm", pd.Series(dtype=str)).astype(str) == "treatment"].copy()
    ctrl_out = outcomes[outcomes.get("experiment_arm", pd.Series(dtype=str)).astype(str) == "control"].copy()

    treatment_contact_rate = safe_rate(float(to_number(tr_out.get("treatment_contacted", pd.Series(dtype=float))).sum()), float(len(tr_out)))
    control_contact_rate = safe_rate(float(to_number(ctrl_out.get("treatment_contacted", pd.Series(dtype=float))).sum()), float(len(ctrl_out)))
    p0_coverage = safe_rate(float(len(p0_t)), float(len(p0)))
    feedback_completion = 1 - safe_rate(float(to_number(outcomes.get("is_pending_30d", pd.Series(dtype=float))).sum()), float(len(outcomes))) if len(outcomes) else 0.0

    metrics = [
        ("treatment_contact_rate", treatment_contact_rate, float(comp.get("min_treatment_contact_rate", 0.80)), ">="),
        ("p0_treatment_coverage", p0_coverage, float(comp.get("min_p0_treatment_coverage", 1.00)), ">="),
        ("control_contamination_rate", control_contact_rate, float(comp.get("max_control_contamination_rate", 0.10)), "<="),
        ("feedback_completion_30d", feedback_completion, float(comp.get("min_feedback_completion_30d", 0.60)), ">="),
    ]
    for name, value, target, direction in metrics:
        ok = value >= target if direction == ">=" else value <= target
        rows.append({
            "metric": name,
            "value": round(value, 6),
            "target": round(target, 6),
            "direction": direction,
            "status": "ok" if ok else "warning",
            "decision_use": "si falla, no culpo al modelo; primero corrijo ejecución comercial",
        })
    rows.append({"metric": "treatment_rows", "value": int(len(treatment)), "target": 1, "direction": ">=", "status": "ok" if len(treatment) else "fail", "decision_use": "muestra operacional"})
    rows.append({"metric": "control_rows", "value": int(len(control)), "target": 1, "direction": ">=", "status": "ok" if len(control) else "warning", "decision_use": "contrafactual operativo"})

    out = pd.DataFrame(rows)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(COMPLIANCE_CSV, index=False, encoding="utf-8")
    return out


def _segment_summary(df: pd.DataFrame, dimension: str, min_n: int, max_segments: int) -> pd.DataFrame:
    """
    Yo calculo impacto por segmento para convertir el experimento en política comercial específica.
    """
    if df.empty or dimension not in df.columns:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    work = df.copy()
    work[dimension] = work[dimension].fillna("sin_dato").astype(str)
    top_values = work[dimension].value_counts().head(max_segments).index.tolist()
    for value in top_values:
        sub = work[work[dimension] == value].copy()
        t = sub[sub.get("experiment_arm", pd.Series(dtype=str)).astype(str) == "treatment"]
        c = sub[sub.get("experiment_arm", pd.Series(dtype=str)).astype(str) == "control"]
        tn, cn = int(len(t)), int(len(c))
        t_neg = safe_rate(float(to_number(t.get("is_negative_30d", pd.Series(dtype=float))).sum()), tn)
        c_neg = safe_rate(float(to_number(c.get("is_negative_30d", pd.Series(dtype=float))).sum()), cn)
        t_pos = safe_rate(float(to_number(t.get("is_positive_30d", pd.Series(dtype=float))).sum()), tn)
        c_pos = safe_rate(float(to_number(c.get("is_positive_30d", pd.Series(dtype=float))).sum()), cn)
        value_risk = float(to_number(sub.get("valor_esperado_en_riesgo", pd.Series(dtype=float))).sum())
        negative_reduction = c_neg - t_neg
        positive_uplift = t_pos - c_pos
        sample_ready = tn >= min_n and cn >= min_n
        rows.append({
            "dimension": dimension,
            "segment": value,
            "treatment_n": tn,
            "control_n": cn,
            "sample_ready": bool(sample_ready),
            "treatment_negative_rate_30d": round(t_neg, 6),
            "control_negative_rate_30d": round(c_neg, 6),
            "negative_reduction_pp": round(negative_reduction * 100, 3),
            "positive_uplift_pp": round(positive_uplift * 100, 3),
            "valor_en_riesgo_segmento": round(value_risk, 2),
            "valor_salvado_proxy": round(max(0.0, negative_reduction) * value_risk, 2),
            "policy_signal": "escalar_segmento" if sample_ready and negative_reduction > 0 else ("recolectar_mas_feedback" if not sample_ready else "no_escalar_aun"),
        })
    return pd.DataFrame(rows)


def build_segment_policy_impact() -> pd.DataFrame:
    """
    Yo calculo impacto por proyecto, canal, asesor y prioridad para que la política no sea genérica.
    """
    cfg = load_yaml()
    seg = cfg.get("segments") or {}
    ensure_experiment_outputs()
    outcomes = read_table(OUTCOMES_CSV)
    dimensions = seg.get("groupby", ["proyecto", "canal", "asesor_id", "prioridad", "risk_band"])
    min_n = int(seg.get("min_segment_n_per_arm", 5))
    max_segments = int(seg.get("max_segments_per_dimension", 20))
    frames = [_segment_summary(outcomes, str(dim), min_n, max_segments) for dim in dimensions]
    frames = [f for f in frames if not f.empty]
    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=["dimension", "segment"])
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(SEGMENT_IMPACT_CSV, index=False, encoding="utf-8")
    return out


def build_sla_capacity_recommendations() -> dict[str, Any]:
    """
    Yo convierto volumen de riesgo en recomendación de SLA y capacidad diaria comercial.
    """
    cfg = load_yaml()
    cap = cfg.get("capacity_policy") or {}
    ensure_experiment_outputs()
    assignment = read_table(ASSIGNMENT_CSV)
    if assignment.empty:
        payload = {"version": "v1.9_experiment_power_and_policy_engine", "status": "missing_assignment", "recommendation": "generar_asignaciones_primero"}
        write_json(payload, SLA_RECOMMENDATIONS_JSON)
        return payload

    daily_capacity = int(cap.get("team_daily_capacity", 30))
    working_days = int(cap.get("working_days_per_week", 5))
    max_p0_share = float(cap.get("max_daily_p0_share", 0.60))
    p0 = int((assignment.get("prioridad", pd.Series(dtype=str)).astype(str).str.upper() == "P0").sum())
    p1 = int((assignment.get("prioridad", pd.Series(dtype=str)).astype(str).str.upper() == "P1").sum())
    p2 = int((assignment.get("prioridad", pd.Series(dtype=str)).astype(str).str.upper() == "P2").sum())
    p0_daily_capacity = max(1, int(round(daily_capacity * max_p0_share)))
    p1_daily_capacity = max(1, daily_capacity - p0_daily_capacity)
    p0_days = math.ceil(p0 / p0_daily_capacity) if p0 else 0
    p1_days = math.ceil(p1 / p1_daily_capacity) if p1 else 0
    total_days = max(p0_days, p1_days)
    backlog_warning_days = int(cap.get("backlog_warning_days", 3))
    status = "ok" if total_days <= backlog_warning_days else "capacity_warning"
    recommended_daily_capacity = daily_capacity
    if status != "ok":
        recommended_daily_capacity = math.ceil((p0 + p1) / max(1, backlog_warning_days))

    payload = {
        "version": "v1.9_experiment_power_and_policy_engine",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "current_team_daily_capacity": daily_capacity,
        "recommended_daily_capacity": int(recommended_daily_capacity),
        "p0_count": p0,
        "p1_count": p1,
        "p2_count": p2,
        "p0_sla_hours": int(cap.get("p0_sla_hours", 4)),
        "p1_sla_hours": int(cap.get("p1_sla_hours", 24)),
        "p2_sla_hours": int(cap.get("p2_sla_hours", 72)),
        "estimated_days_to_clear_p0_p1": int(total_days),
        "p0_daily_capacity": int(p0_daily_capacity),
        "p1_daily_capacity": int(p1_daily_capacity),
        "recommendation": "aumentar_capacidad_o_subir_umbral_p0" if status != "ok" else "capacidad_suficiente_para_politica_actual",
    }
    write_json(payload, SLA_RECOMMENDATIONS_JSON)
    return payload


def build_escalation_policy() -> dict[str, Any]:
    """
    Yo publico una política de escalamiento P0/P1/P2 lista para operación comercial.
    """
    cfg = load_yaml()
    policy = cfg.get("escalation_policy") or {}
    power = read_json(POWER_JSON) if POWER_JSON.exists() else compute_power_analysis()
    compliance = read_table(COMPLIANCE_CSV) if COMPLIANCE_CSV.exists() else build_treatment_compliance()
    capacity = read_json(SLA_RECOMMENDATIONS_JSON) if SLA_RECOMMENDATIONS_JSON.exists() else build_sla_capacity_recommendations()
    compliance_warnings = int((compliance.get("status", pd.Series(dtype=str)).astype(str) != "ok").sum()) if not compliance.empty else 1
    payload = {
        "version": "v1.9_experiment_power_and_policy_engine",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy_mode": "mvp_operational_policy",
        "power_decision": power.get("decision"),
        "capacity_status": capacity.get("status"),
        "compliance_warnings": compliance_warnings,
        "rules": policy,
        "executive_decision": "operar_politica_con_medicion" if compliance_warnings <= 2 else "corregir_cumplimiento_antes_de_escalar",
        "privacy_mode": "safe_ids_and_aggregates_only",
    }
    write_json(payload, ESCALATION_POLICY_JSON)
    return payload


def build_manifest() -> dict[str, Any]:
    """
    Yo construyo el manifiesto para auditar qué produjo el motor de política experimental.
    """
    power = read_json(POWER_JSON)
    capacity = read_json(SLA_RECOMMENDATIONS_JSON)
    policy = read_json(ESCALATION_POLICY_JSON)
    compliance = read_table(COMPLIANCE_CSV)
    segments = read_table(SEGMENT_IMPACT_CSV)
    payload = {
        "version": "v1.9_experiment_power_and_policy_engine",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "ok",
        "power_ready": power.get("power_ready", False),
        "capacity_status": capacity.get("status"),
        "executive_decision": policy.get("executive_decision"),
        "counts": {
            "compliance_metrics": int(len(compliance)),
            "segment_rows": int(len(segments)),
        },
        "artifacts": {
            "power_json": str(POWER_JSON.relative_to(PROJECT_ROOT)),
            "compliance_csv": str(COMPLIANCE_CSV.relative_to(PROJECT_ROOT)),
            "segment_impact_csv": str(SEGMENT_IMPACT_CSV.relative_to(PROJECT_ROOT)),
            "sla_recommendations_json": str(SLA_RECOMMENDATIONS_JSON.relative_to(PROJECT_ROOT)),
            "escalation_policy_json": str(ESCALATION_POLICY_JSON.relative_to(PROJECT_ROOT)),
            "report_md": str(REPORT_MD.relative_to(PROJECT_ROOT)),
        },
        "privacy_mode": "safe_aggregates_only",
    }
    write_json(payload, MANIFEST_JSON)
    return payload


def validate_policy_engine_outputs() -> dict[str, Any]:
    """
    Yo valido que los outputs de política no expongan PII ni credenciales.
    """
    cfg = load_yaml()
    privacy = cfg.get("privacy") or {}
    forbidden_cols = {str(c).strip().lower() for c in privacy.get("forbidden_output_columns", [])}
    patterns = [re.compile(str(p), flags=re.IGNORECASE) for p in privacy.get("forbidden_output_patterns", [])]
    files = [POWER_JSON, COMPLIANCE_CSV, SEGMENT_IMPACT_CSV, SLA_RECOMMENDATIONS_JSON, ESCALATION_POLICY_JSON, MANIFEST_JSON, REPORT_MD]
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
            sample_text = path.read_text(encoding="utf-8")[:50000]
        for pattern in patterns:
            if sample_text and pattern.search(sample_text):
                # Yo permito números agregados en JSON/Markdown, pero bloqueo patrones sensibles en CSV de texto.
                if path.suffix == ".csv":
                    errors.append({"path": str(path.relative_to(PROJECT_ROOT)), "issue": "forbidden_pattern", "pattern": pattern.pattern})
    payload = {
        "version": "v1.9_experiment_power_and_policy_engine",
        "status": "ok" if not errors else "fail",
        "errors": errors,
        "checked_files": [str(p.relative_to(PROJECT_ROOT)) for p in files],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json(payload, VALIDATION_JSON)
    return payload


def generate_report() -> Path:
    """
    Yo genero el reporte ejecutivo que convierte experimento en política comercial accionable.
    """
    power = read_json(POWER_JSON) if POWER_JSON.exists() else compute_power_analysis()
    compliance = read_table(COMPLIANCE_CSV) if COMPLIANCE_CSV.exists() else build_treatment_compliance()
    segments = read_table(SEGMENT_IMPACT_CSV) if SEGMENT_IMPACT_CSV.exists() else build_segment_policy_impact()
    capacity = read_json(SLA_RECOMMENDATIONS_JSON) if SLA_RECOMMENDATIONS_JSON.exists() else build_sla_capacity_recommendations()
    policy = read_json(ESCALATION_POLICY_JSON) if ESCALATION_POLICY_JSON.exists() else build_escalation_policy()
    validation = read_json(VALIDATION_JSON) if VALIDATION_JSON.exists() else {"status": "pending"}

    top_segments = segments.sort_values("valor_salvado_proxy", ascending=False).head(10) if not segments.empty and "valor_salvado_proxy" in segments.columns else pd.DataFrame()
    lines = [
        "# Experiment Power & Policy Engine · v1.9",
        "",
        "## Escena ejecutiva",
        "Yo convierto el experimento de riesgo de caída en política comercial: poder estadístico, cumplimiento, segmentos, SLA, capacidad y escalamiento.",
        "",
        "## Power analysis",
        f"- MDE objetivo: **{power.get('minimum_detectable_effect_pp', 0)} pp**",
        f"- N requerido por brazo: **{power.get('required_n_per_arm', 0)}**",
        f"- N observado mínimo por brazo: **{power.get('observed_min_n_per_arm', 0)}**",
        f"- Efecto detectable con muestra actual: **{power.get('detectable_effect_pp_with_current_sample', 0)} pp**",
        f"- Decisión: **{power.get('decision', 'sin_decision')}**",
        "",
        "## Compliance de tratamiento",
    ]
    if compliance.empty:
        lines.append("No hay compliance calculado.")
    else:
        lines.append(compliance.to_markdown(index=False))
    lines.extend([
        "",
        "## SLA y capacidad",
        f"- Estado: **{capacity.get('status', 'sin_estado')}**",
        f"- Capacidad diaria actual: **{capacity.get('current_team_daily_capacity', 0)}**",
        f"- Capacidad diaria recomendada: **{capacity.get('recommended_daily_capacity', 0)}**",
        f"- P0: **{capacity.get('p0_count', 0)}** con SLA **{capacity.get('p0_sla_hours', 4)}h**",
        f"- P1: **{capacity.get('p1_count', 0)}** con SLA **{capacity.get('p1_sla_hours', 24)}h**",
        f"- Días estimados para limpiar P0/P1: **{capacity.get('estimated_days_to_clear_p0_p1', 0)}**",
        f"- Recomendación: **{capacity.get('recommendation', 'sin_recomendacion')}**",
        "",
        "## Política de escalamiento",
        f"- Decisión ejecutiva: **{policy.get('executive_decision', 'sin_decision')}**",
        f"- P0: tratamiento obligatorio, SLA corto, sin holdout.",
        f"- P1: tratamiento/control permitido de forma controlada, SLA 24h.",
        f"- P2: monitoreo y escalamiento si sube el riesgo.",
        "",
        "## Top segmentos por valor salvado proxy",
    ])
    if top_segments.empty:
        lines.append("Aún no hay segmentos con suficiente feedback para ranking de política.")
    else:
        lines.append(top_segments.to_markdown(index=False))
    lines.extend([
        "",
        "## Interpretación económica",
        "Si el experimento aún no tiene poder, la fábrica no debe prometer causalidad. Debe operar política MVP, medir cumplimiento, completar feedback 7d/30d y recién escalar reglas por segmento.",
        "",
        "## Privacidad",
        f"Validación de privacidad: **{validation.get('status', 'pending')}**. No publico clientes, documentos, teléfonos, emails, direcciones ni credenciales.",
        "",
        "## Próxima acción",
        "Yo usaría esta política para definir capacidad diaria, SLA por prioridad y qué segmentos merecen intervención reforzada en la próxima reunión comercial.",
    ])
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    return REPORT_MD


def run_experiment_power_policy_engine() -> dict[str, Any]:
    """
    Yo ejecuto el motor completo de poder experimental y política comercial.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    power = compute_power_analysis()
    compliance = build_treatment_compliance()
    segments = build_segment_policy_impact()
    capacity = build_sla_capacity_recommendations()
    policy = build_escalation_policy()
    manifest = build_manifest()
    report = generate_report()
    validation = validate_policy_engine_outputs()
    manifest["validation_status"] = validation.get("status")
    write_json(manifest, MANIFEST_JSON)
    return {
        "power": power,
        "compliance_rows": int(len(compliance)),
        "segment_rows": int(len(segments)),
        "capacity": capacity,
        "policy": policy,
        "manifest": manifest,
        "validation": validation,
        "report": str(report.relative_to(PROJECT_ROOT)),
    }


def experiment_power_policy_metadata() -> dict[str, Any]:
    """
    Yo expongo metadata segura del motor de política para API y dashboards.
    """
    if not MANIFEST_JSON.exists():
        run_experiment_power_policy_engine()
    return read_json(MANIFEST_JSON)
