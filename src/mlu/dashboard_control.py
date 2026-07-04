from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from src.mlu.config import PROJECT_ROOT

CATALOG_PATH = PROJECT_ROOT / "config" / "dashboard_catalog.yml"
DASHBOARD_PARAMS_PATH = PROJECT_ROOT / "config" / "dashboard_params.yml"
PRIVACY_POLICY_PATH = PROJECT_ROOT / "config" / "privacy_policy.yml"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "dashboard_control"
CONTROL_PANEL_PATH = OUTPUT_DIR / "DASHBOARD_CONTROL_PANEL.md"
INPUTS_TO_CONFIRM_PATH = OUTPUT_DIR / "INPUTS_TO_CONFIRM.md"
VALIDATION_REPORT_PATH = OUTPUT_DIR / "dashboard_parameter_validation.json"


@dataclass(frozen=True)
class DashboardCatalogItem:
    id: str
    number: int
    name: str
    owner: str
    audience: str
    economic_question: str
    output_path: str
    params_ref: str
    priority: str
    status: str


def load_yaml(path: Path) -> dict[str, Any]:
    """
    Yo cargo archivos YAML de configuración para mantener la estrategia fuera del código.
    """
    if not path.exists():
        raise FileNotFoundError(f"No encuentro configuración requerida: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_dashboard_catalog(path: Path = CATALOG_PATH) -> dict[str, Any]:
    """
    Yo cargo el catálogo de dashboards como inventario gobernado de productos de decisión.
    """
    return load_yaml(path)


def load_dashboard_params(path: Path = DASHBOARD_PARAMS_PATH) -> dict[str, Any]:
    """
    Yo cargo los parámetros editables para no modificar código ante cambios de negocio.
    """
    return load_yaml(path)


def load_privacy_policy(path: Path = PRIVACY_POLICY_PATH) -> dict[str, Any]:
    """
    Yo cargo la política de privacidad para impedir que Railway, GitHub o RAG expongan PII.
    """
    return load_yaml(path)


def parse_param_ref(ref: str) -> tuple[Path | None, str | None]:
    """
    Yo separo una referencia tipo config/dashboard_params.yml#ceo_brief en archivo y sección.
    """
    if "#" not in ref:
        return (PROJECT_ROOT / ref, None) if ref.endswith((".yml", ".yaml", ".json")) else (None, None)
    file_part, section = ref.split("#", 1)
    return PROJECT_ROOT / file_part, section


def validate_dashboard_catalog() -> dict[str, Any]:
    """
    Yo valido que cada dashboard tenga dueño, pregunta económica, output y referencia de parámetros.
    """
    catalog = load_dashboard_catalog()
    dashboards = catalog.get("dashboards", [])
    errors: list[str] = []
    warnings: list[str] = []
    required_fields = ["id", "name", "owner", "audience", "economic_question", "output_path", "params_ref"]

    seen_ids: set[str] = set()
    for item in dashboards:
        for field in required_fields:
            if not item.get(field):
                errors.append(f"dashboard {item.get('id', '<sin_id>')} no tiene {field}")
        dashboard_id = str(item.get("id"))
        if dashboard_id in seen_ids:
            errors.append(f"dashboard id duplicado: {dashboard_id}")
        seen_ids.add(dashboard_id)

        params_ref = str(item.get("params_ref", ""))
        param_path, section = parse_param_ref(params_ref)
        if param_path is not None and not param_path.exists():
            warnings.append(f"params_ref apunta a archivo inexistente: {params_ref}")
        elif param_path is not None and section:
            data = load_yaml(param_path) if param_path.suffix in {".yml", ".yaml"} else {}
            if section not in data:
                warnings.append(f"params_ref sin sección encontrada: {params_ref}")

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_dashboards": len(dashboards),
        "errors": errors,
        "warnings": warnings,
        "status": "ok" if not errors else "fail",
    }


def validate_recommended_decisions() -> dict[str, Any]:
    """
    Yo valido que las decisiones recomendadas queden codificadas como parámetros explícitos.
    """
    params = load_dashboard_params()
    privacy = load_privacy_policy()
    decisions = params.get("validated_decisions", {})
    prod = privacy.get("production_decisions", {})
    public = privacy.get("public_dashboard", {})

    checks = {
        "project_names_public": decisions.get("project_names_public") is True and prod.get("public_project_names_allowed") is True,
        "advisors_public_anonymized": decisions.get("advisors_public_anonymized") is True and public.get("anonymize_advisors_public") is True,
        "channels_public_visible": decisions.get("channels_public_visible") is True and prod.get("public_channel_names_allowed") is True,
        "aggregated_value_at_risk_public": decisions.get("aggregated_value_at_risk_public") is True and prod.get("public_expected_value_at_risk_allowed") is True,
        "top_operations_public_blocked": decisions.get("top_operations_public") is False and prod.get("public_top_operations_allowed") is False,
        "pii_public_blocked": decisions.get("pii_public") is False,
        "railway_aggregated_only": decisions.get("railway_data_strategy") == "aggregated_public_payload_only",
        "lenovo_private_crm": decisions.get("lenovo_data_strategy") == "private_full_crm_runner",
        "github_aggregated_artifacts": decisions.get("github_artifacts_strategy") == "aggregated_or_anonymized_only",
    }
    return {"checks": checks, "status": "ok" if all(checks.values()) else "fail"}


def build_inputs_to_confirm_rows() -> list[dict[str, str]]:
    """
    Yo genero la tabla de inputs críticos que debo revisar antes de presentar o vender el sistema.
    """
    return [
        {"input":"MLU_ENV", "decision":"Comportamiento local/producción", "recommended":"production en Railway", "where":"Variables Railway / .env"},
        {"input":"MLU_DISABLE_SAMPLE_FALLBACK", "decision":"Bloquear demo en producción", "recommended":"true", "where":"Variables Railway / .env"},
        {"input":"data_mode", "decision":"Demo vs CRM real", "recommended":"crm", "where":"config/environment.yml"},
        {"input":"Horizonte riesgo caída", "decision":"Target del modelo", "recommended":"30 días", "where":"config/model_params.yml > riesgo_caida.horizon_days"},
        {"input":"Threshold P0", "decision":"Operaciones a intervenir hoy", "recommended":"0.70 o calibrado por capacidad", "where":"config/model_params.yml > riesgo_caida.thresholds.p0"},
        {"input":"Threshold P1", "decision":"Intervenir en 24h", "recommended":"0.50", "where":"config/model_params.yml > riesgo_caida.thresholds.p1"},
        {"input":"Threshold P2", "decision":"Monitoreo 72h", "recommended":"0.35", "where":"config/model_params.yml > riesgo_caida.thresholds.p2"},
        {"input":"Capacidad diaria equipo", "decision":"Cuántos P0 se pueden atender", "recommended":"20-50", "where":"config/alert_thresholds.yml > commercial_risk"},
        {"input":"Tipo de unidad foco", "decision":"No mezclar depas con cocheras", "recommended":"departamento", "where":"config/model_params.yml > riesgo_caida.unit_focus"},
        {"input":"Separación válida", "decision":"Base comercial", "recommended":"congelar contrato oficial", "where":"config/business_rules.yml > separacion_valida"},
        {"input":"Minuta válida", "decision":"Definición de venta", "recommended":"congelar contrato oficial", "where":"config/business_rules.yml > minuta_valida"},
        {"input":"Caída válida", "decision":"Definición del target", "recommended":"congelar contrato oficial", "where":"config/business_rules.yml > caida_valida"},
        {"input":"Columnas prohibidas ML", "decision":"Anti-leakage", "recommended":"fecha_caida, fecha_firma, fecha_anulacion", "where":"config/model_params.yml > riesgo_caida.forbidden_columns"},
        {"input":"Columnas prohibidas públicas", "decision":"Privacidad", "recommended":"cliente, DNI, teléfono, email, dirección, credenciales", "where":"config/privacy_policy.yml > forbidden_public_fields"},
        {"input":"Top N dashboard público", "decision":"Exposición agregada", "recommended":"5", "where":"config/dashboard_params.yml > public_dashboard.top_n"},
        {"input":"Proyectos reales en Railway", "decision":"Demo comercial", "recommended":"sí, agregados", "where":"config/privacy_policy.yml > public_dashboard.expose_project_names"},
        {"input":"Asesores reales en Railway", "decision":"Privacidad comercial", "recommended":"no, anonimizar", "where":"config/privacy_policy.yml > public_dashboard.anonymize_advisors_public"},
        {"input":"Canales públicos", "decision":"Demo sin PII", "recommended":"sí, agregados", "where":"config/dashboard_params.yml > public_dashboard.include_channel_names"},
        {"input":"Top operaciones públicas", "decision":"Privacidad", "recommended":"no", "where":"config/dashboard_params.yml > public_dashboard.include_row_level_operations"},
        {"input":"RAG CRM access", "decision":"Seguridad", "recommended":"solo tablas anonimizadas/agregadas", "where":"config/rag_sql_policy.yml"},
        {"input":"Railway data strategy", "decision":"Despliegue público", "recommended":"payload agregado, no CRM live", "where":"config/privacy_policy.yml > production_decisions"},
        {"input":"Lenovo data strategy", "decision":"Extracción real CRM", "recommended":"private_full_crm_runner", "where":"config/environment.yml > lenovo_self_hosted"},
        {"input":"GitHub artifacts", "decision":"No filtrar CRM", "recommended":"solo agregados o anonimizados", "where":"config/privacy_policy.yml > production_decisions"},
        {"input":"RAG faithfulness mínimo", "decision":"Calidad demo UNI", "recommended":"0.75", "where":"config/alert_thresholds.yml > rag_quality"},
        {"input":"Trap refusal mínimo", "decision":"Seguridad RAG", "recommended":"1.00", "where":"config/alert_thresholds.yml > rag_quality"},
        {"input":"Railway URL", "decision":"Smoke test API", "recommended":"URL Railway", "where":"GitHub Secret MLU_RAILWAY_BASE_URL"},
        {"input":"Fuente mercado precio m²", "decision":"Pricing gap", "recommended":"scraping/CSV/API", "where":"config/market_sources.yml"},
        {"input":"Stock lento días", "decision":"Alerta stock", "recommended":"90/120/180", "where":"config/alert_thresholds.yml > stock_lento"},
        {"input":"Drift PSI warning/fail", "decision":"Monitoreo modelo", "recommended":"0.10 / 0.25", "where":"config/drift_thresholds.yml"},
        {"input":"Retraining max age", "decision":"Reentrenamiento", "recommended":"30 días", "where":"contracts/retraining_policy.yml"},
    ]


def generate_inputs_to_confirm() -> Path:
    """
    Yo escribo una tabla ejecutiva con cada parámetro importante y dónde cambiarlo.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = build_inputs_to_confirm_rows()
    lines = [
        "# Inputs críticos a confirmar",
        "",
        "Esta tabla convierte dudas de negocio en parámetros editables.",
        "",
        "| Input | Decisión que afecta | Recomendación tomada | Donde cambiar |",
        "|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['input']} | {r['decision']} | {r['recommended']} | `{r['where']}` |")
    INPUTS_TO_CONFIRM_PATH.write_text("\n".join(lines), encoding="utf-8")
    return INPUTS_TO_CONFIRM_PATH


def generate_control_panel() -> Path:
    """
    Yo genero el panel maestro de dashboards para presentar la fábrica como catálogo de productos de decisión.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    catalog = load_dashboard_catalog()
    validation = validate_dashboard_catalog()
    decisions = validate_recommended_decisions()
    rows = catalog.get("dashboards", [])

    lines = [
        "# Dashboard Control Panel v1.3",
        "",
        "Yo uso este panel para gobernar dashboards, parámetros y decisiones sin tocar código.",
        "",
        f"- Total dashboards catalogados: **{len(rows)}**",
        f"- Estado catálogo: **{validation['status']}**",
        f"- Estado decisiones recomendadas: **{decisions['status']}**",
        "",
        "## Decisiones recomendadas ya tomadas",
        "",
        "- Railway sirve solo payload agregado CRM, no CRM live.",
        "- Lenovo queda como runner privado para CRM completo.",
        "- GitHub conserva artifacts agregados o anonimizados.",
        "- Proyectos pueden mostrarse públicamente solo agregados.",
        "- Asesores se anonimizan en público.",
        "- Clientes, documentos, teléfonos, emails, direcciones y credenciales nunca salen al payload público.",
        "- RAG consulta CRM solo como tablas anonimizadas/agregadas.",
        "",
        "## Catálogo",
        "",
        "| # | Dashboard | Pregunta económica | Owner | Prioridad | Donde cambiar |",
        "|---:|---|---|---|---|---|",
    ]
    for d in rows:
        lines.append(f"| {d.get('number')} | {d.get('name')} | {d.get('economic_question')} | {d.get('owner')} | {d.get('priority')} | `{d.get('params_ref')}` |")

    if validation.get("warnings"):
        lines += ["", "## Warnings de configuración", ""]
        for w in validation["warnings"]:
            lines.append(f"- {w}")
    if validation.get("errors"):
        lines += ["", "## Errores", ""]
        for e in validation["errors"]:
            lines.append(f"- {e}")

    CONTROL_PANEL_PATH.write_text("\n".join(lines), encoding="utf-8")
    VALIDATION_REPORT_PATH.write_text(json.dumps({"catalog": validation, "recommended_decisions": decisions}, ensure_ascii=False, indent=2), encoding="utf-8")
    generate_inputs_to_confirm()
    return CONTROL_PANEL_PATH


def dashboard_control_metadata() -> dict[str, Any]:
    """
    Yo expongo metadata para API o GitHub Actions sobre el catálogo de dashboards.
    """
    catalog = load_dashboard_catalog()
    validation = validate_dashboard_catalog()
    decisions = validate_recommended_decisions()
    return {
        "version": catalog.get("version"),
        "total_dashboards": len(catalog.get("dashboards", [])),
        "validation_status": validation.get("status"),
        "recommended_decisions_status": decisions.get("status"),
        "control_panel_path": str(CONTROL_PANEL_PATH),
        "inputs_to_confirm_path": str(INPUTS_TO_CONFIRM_PATH),
    }
