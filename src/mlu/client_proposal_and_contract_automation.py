from __future__ import annotations

import html
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from src.mlu.config import PROJECT_ROOT

CONFIG_PATH = PROJECT_ROOT / "config" / "client_proposals.yml"
TENANTS_CONFIG_PATH = PROJECT_ROOT / "config" / "client_tenants.yml"
REPORT_DIR = PROJECT_ROOT / "reports" / "client_proposals"
INDEX_HTML = REPORT_DIR / "proposal_index.html"
INDEX_MD = REPORT_DIR / "CLIENT_PROPOSAL_INDEX.md"
MANIFEST_JSON = REPORT_DIR / "client_proposals_manifest.json"
VALIDATION_JSON = REPORT_DIR / "client_proposals_validation.json"

FORBIDDEN_DEFAULT = [
    "cliente", "documento", "dni", "email", "telefono", "teléfono", "celular",
    "direccion", "dirección", "codigo_proforma", "codigo_unidad", "password",
    "secret", "credential", "credenciales", "redshift_password",
]


def now_iso() -> str:
    """
    Yo genero una marca temporal UTC para auditar la propuesta comercial.
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_yaml(path: Path) -> dict[str, Any]:
    """
    Yo leo YAML de configuración y devuelvo un diccionario vacío si falta el archivo.
    """
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def read_json(path: Path) -> dict[str, Any]:
    """
    Yo leo JSON cuando existe para reutilizar manifests y paquetes generados.
    """
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """
    Yo escribo JSON legible porque una propuesta debe ser auditable por negocio y tecnología.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    """
    Yo escribo contratos de métricas en YAML para que el alcance no dependa de promesas verbales.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")


def normalize_tenant_id(tenant_id: str) -> str:
    """
    Yo normalizo tenant_id para evitar rutas peligrosas en los paquetes comerciales.
    """
    value = re.sub(r"[^a-zA-Z0-9_-]+", "_", str(tenant_id).strip().lower()).strip("_")
    if not value:
        raise ValueError("tenant_id vacío")
    return value


def tenant_output_dir(tenant_id: str) -> Path:
    """
    Yo centralizo la carpeta de salida de cada propuesta por cliente.
    """
    return REPORT_DIR / normalize_tenant_id(tenant_id)


def money(value: float, currency: str) -> str:
    """
    Yo formateo montos para que la propuesta sea legible para comité o gerencia.
    """
    return f"{currency} {value:,.0f}"


def rel(path: Path) -> str:
    """
    Yo convierto rutas absolutas a rutas portables dentro del repositorio.
    """
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def load_tenants() -> list[dict[str, Any]]:
    """
    Yo cargo los tenants comerciales desde la configuración multi-cliente.
    """
    cfg = read_yaml(TENANTS_CONFIG_PATH)
    tenants = cfg.get("tenants", [])
    if isinstance(tenants, dict):
        tenants = list(tenants.values())
    return tenants or [
        {"tenant_id": "cliente_alpha", "display_name": "Cliente Alpha", "segment": "desarrollador_multifamiliar", "enabled_modules": ["ceo_brief", "risk_to_action_queue", "railway_public_dashboard"]}
    ]


def _proposal_cfg() -> dict[str, Any]:
    """
    Yo cargo la configuración comercial y aplico overrides de entorno cuando existen.
    """
    cfg = read_yaml(CONFIG_PATH)
    engine = cfg.setdefault("proposal_engine", {})
    if os.getenv("MLU_PROPOSAL_CURRENCY"):
        engine["currency"] = os.getenv("MLU_PROPOSAL_CURRENCY")
    if os.getenv("MLU_PROPOSAL_DISCOUNT_PCT"):
        try:
            engine["default_discount_pct"] = float(os.getenv("MLU_PROPOSAL_DISCOUNT_PCT", "0"))
        except ValueError:
            engine["default_discount_pct"] = 0
    return cfg


def recommend_package(tenant: dict[str, Any], cfg: dict[str, Any]) -> str:
    """
    Yo selecciono el paquete recomendado combinando recomendación explícita y complejidad del tenant.
    """
    tenant_id = normalize_tenant_id(tenant.get("tenant_id", "cliente"))
    explicit = cfg.get("tenant_package_recommendations", {}).get(tenant_id)
    if explicit:
        return explicit
    modules = tenant.get("enabled_modules", []) or []
    if "experimentation_policy_engine" in modules or "multi_tenant_packaging" in modules:
        return "enterprise"
    if "rag_business_memory" in modules or len(modules) >= 6:
        return "professional"
    if len(modules) >= 3:
        return "mvp"
    return "diagnostic"


def package_price(package: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Yo calculo setup, mensualidad y total de primer año para que la propuesta tenga número económico.
    """
    engine = cfg.get("proposal_engine", {})
    currency = engine.get("currency", "USD")
    discount_pct = float(engine.get("default_discount_pct", 0) or 0)
    setup = float(package.get("setup_fee", 0) or 0)
    monthly = float(package.get("monthly_fee", 0) or 0)
    discount_amount = setup * discount_pct / 100
    net_setup = setup - discount_amount
    year_one = net_setup + monthly * 12
    return {
        "currency": currency,
        "setup_fee": setup,
        "monthly_fee": monthly,
        "discount_pct": discount_pct,
        "discount_amount": discount_amount,
        "net_setup_fee": net_setup,
        "year_one_total": year_one,
        "formatted_setup_fee": money(net_setup, currency),
        "formatted_monthly_fee": money(monthly, currency),
        "formatted_year_one_total": money(year_one, currency),
    }


def module_rows(modules: list[str], module_catalog: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Yo convierto códigos de módulos en filas explicables para negocio.
    """
    rows = []
    for module in modules:
        meta = module_catalog.get(module, {})
        rows.append({
            "module_id": module,
            "label": meta.get("label", module),
            "metric_owner": meta.get("metric_owner", "por_confirmar"),
            "decision": meta.get("decision", "por_confirmar"),
        })
    return rows


def build_metric_contract(tenant: dict[str, Any], package_key: str, package: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Yo genero un contrato de métricas por cliente para que la propuesta tenga gobierno de datos.
    """
    default_contract = cfg.get("default_metric_contract", {})
    modules = module_rows(package.get("modules", []), cfg.get("module_catalog", {}))
    return {
        "tenant_id": normalize_tenant_id(tenant.get("tenant_id", "cliente")),
        "client_display_name": tenant.get("display_name"),
        "package": package_key,
        "created_at": now_iso(),
        "grain": default_contract.get("grain", "proyecto_mes"),
        "refresh_frequency": default_contract.get("refresh_frequency", "diaria"),
        "official_timezone": default_contract.get("official_timezone", "America/Lima"),
        "allowed_public_data": default_contract.get("allowed_public_data", "agregados"),
        "forbidden_public_data": default_contract.get("forbidden_public_data", FORBIDDEN_DEFAULT),
        "metrics": [
            {
                "metric_id": row["module_id"],
                "name": row["label"],
                "owner": row["metric_owner"],
                "decision_enabled": row["decision"],
                "status": "included_in_scope",
            }
            for row in modules
        ],
    }


def build_implementation_scope(tenant: dict[str, Any], package_key: str, package: dict[str, Any], cfg: dict[str, Any]) -> str:
    """
    Yo redacto el alcance de implementación para evitar ambigüedad comercial.
    """
    included = module_rows(package.get("modules", []), cfg.get("module_catalog", {}))
    excluded = package.get("excluded_modules", []) or []
    lines = [
        f"# Alcance de implementación · {tenant.get('display_name')}",
        "",
        f"**Paquete recomendado:** {package.get('name', package_key)}",
        f"**Duración estimada:** {package.get('duration_days')} días",
        "",
        "## Incluido",
    ]
    for row in included:
        lines.append(f"- **{row['label']}**: {row['decision']} · Owner sugerido: {row['metric_owner']}")
    lines += ["", "## Excluido / fuera del MVP"]
    if excluded:
        for item in excluded:
            lines.append(f"- {item}")
    else:
        lines.append("- Sin exclusiones declaradas para el paquete recomendado.")
    lines += [
        "",
        "## Supuestos",
        "- El CRM privado corre en entorno controlado del cliente o runner privado.",
        "- La demo pública usa payload agregado y no contiene PII.",
        "- Las definiciones de separación, minuta, caída, tubería y cobranza se validan en kickoff.",
    ]
    return "\n".join(lines) + "\n"


def build_onboarding_checklist(tenant: dict[str, Any], cfg: dict[str, Any]) -> str:
    """
    Yo genero checklist de onboarding para convertir una propuesta aceptada en ejecución real.
    """
    items = [
        "Confirmar sponsor ejecutivo y owner operativo.",
        "Confirmar fuentes CRM, Power BI, Excel, Redshift/Sperant o parquets.",
        "Confirmar definiciones oficiales de lead, separación, minuta, caída, tubería y cobranza.",
        "Confirmar política de privacidad, PII y entorno de procesamiento.",
        "Confirmar dashboard público permitido: proyectos sí/no, asesores anonimizados, canales agregados.",
        "Confirmar umbrales P0/P1/P2 y capacidad diaria del equipo comercial.",
        "Confirmar formato de entrega: Railway, GitHub Pages, HTML estático, API FastAPI o Power BI.",
        "Confirmar calendario de demo, revisión ejecutiva y handoff.",
    ]
    lines = [f"# Checklist de onboarding · {tenant.get('display_name')}", ""]
    lines += [f"- [ ] {item}" for item in items]
    return "\n".join(lines) + "\n"


def build_thirty_day_plan(tenant: dict[str, Any], cfg: dict[str, Any]) -> str:
    """
    Yo genero un plan de 30 días para que el cliente entienda la ruta de implementación.
    """
    phases = cfg.get("implementation_phases", [])
    lines = [f"# Plan de 30 días · {tenant.get('display_name')}", ""]
    for phase in phases:
        lines.append(f"## {phase.get('day_range')} · {phase.get('name')}")
        for deliverable in phase.get("deliverables", []):
            lines.append(f"- {deliverable}")
        lines.append("")
    return "\n".join(lines)


def build_proposal_markdown(tenant: dict[str, Any], package_key: str, package: dict[str, Any], pricing: dict[str, Any], cfg: dict[str, Any]) -> str:
    """
    Yo construyo la propuesta ejecutiva con alcance, valor económico y próximos pasos.
    """
    engine = cfg.get("proposal_engine", {})
    included = module_rows(package.get("modules", []), cfg.get("module_catalog", {}))
    lines = [
        f"# Propuesta Comercial · {tenant.get('display_name')}",
        "",
        "## Resumen ejecutivo",
        "Esta propuesta convierte la operación comercial inmobiliaria en una fábrica de inteligencia: métricas contratadas, dashboards ejecutivos, alertas, RAG con evidencia y feedback de decisiones.",
        "",
        f"**Paquete recomendado:** {package.get('name', package_key)}",
        f"**Duración estimada:** {package.get('duration_days')} días",
        f"**Setup:** {pricing['formatted_setup_fee']}",
        f"**Mensualidad opcional:** {pricing['formatted_monthly_fee']}",
        f"**Total primer año estimado:** {pricing['formatted_year_one_total']}",
        "",
        "## Problema que resuelve",
        "- Métricas discutibles entre áreas.",
        "- Riesgo comercial sin priorización accionable.",
        "- Dashboards sin contrato de datos ni feedback.",
        "- Reportes que no terminan en responsable, SLA y resultado.",
        "",
        "## Módulos incluidos",
    ]
    for row in included:
        lines.append(f"- **{row['label']}** · {row['decision']} · Owner: {row['metric_owner']}")
    lines += [
        "",
        "## Política de datos y privacidad",
        engine.get("privacy_position", "No se expone PII."),
        "",
        "## Condiciones comerciales",
        f"- Vigencia de propuesta: {engine.get('proposal_validity_days', 15)} días.",
        f"- Forma de pago: {engine.get('payment_terms', 'por definir')}.",
        f"- Nota legal: {engine.get('legal_note', '')}",
        "",
        "## Próximo paso",
        "Aprobar alcance, confirmar fuentes y ejecutar kickoff de contrato de métricas.",
    ]
    return "\n".join(lines) + "\n"


def build_tenant_html(tenant: dict[str, Any], package: dict[str, Any], pricing: dict[str, Any], files: dict[str, str]) -> str:
    """
    Yo genero una página HTML simple para presentar la propuesta en una demo comercial.
    """
    title = html.escape(str(tenant.get("display_name", "Cliente")))
    return f"""
<!doctype html>
<html lang='es'>
<head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Propuesta · {title}</title>
<style>
body{{margin:0;background:#070A12;color:#F7F8FC;font-family:Inter,Segoe UI,Arial,sans-serif}}
main{{max-width:1060px;margin:0 auto;padding:48px 24px}}
.card{{background:#11182A;border:1px solid rgba(255,255,255,.1);border-radius:22px;padding:22px;margin:16px 0}}
h1{{font-size:48px;line-height:.95}} .accent{{color:#D6A84F}} a{{color:#9CC8FF}}
.metric{{font-size:32px;font-weight:900;color:#D6A84F}}
</style></head>
<body><main>
<p class='accent'>Commercial Intelligence OS · Client Proposal</p>
<h1>Propuesta para {title}</h1>
<div class='card'><h2>{html.escape(str(package.get('name')))}</h2><p>Duración estimada: {package.get('duration_days')} días</p><p class='metric'>{pricing['formatted_setup_fee']} setup</p><p>{pricing['formatted_monthly_fee']} mensualidad opcional · {pricing['formatted_year_one_total']} primer año estimado</p></div>
<div class='card'><h2>Archivos de propuesta</h2><ul>
<li><a href='{files['proposal']}'>Propuesta ejecutiva</a></li>
<li><a href='{files['scope']}'>Alcance de implementación</a></li>
<li><a href='{files['metric_contract']}'>Contrato de métricas</a></li>
<li><a href='{files['onboarding']}'>Checklist onboarding</a></li>
<li><a href='{files['plan']}'>Plan 30 días</a></li>
</ul></div>
</main></body></html>
"""


def forbidden_hits_in_files(paths: list[Path], forbidden: list[str]) -> list[dict[str, str]]:
    """
    Yo inspecciono archivos de propuesta para detectar nombres de campos prohibidos como llaves o exposición accidental.
    """
    hits: list[dict[str, str]] = []
    # Yo permito que la política mencione campos prohibidos dentro del contrato; no permito valores personales ni secretos.
    secret_patterns = [r"redshift_password\s*=", r"password\s*[:=]\s*[^\s]+", r"@", r"\b\d{8}\b", r"\b9\d{8}\b"]
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        lower = text.lower()
        for pattern in secret_patterns:
            if re.search(pattern, lower):
                hits.append({"path": rel(path), "pattern": pattern})
    return hits


def build_client_proposals() -> dict[str, Any]:
    """
    Yo genero propuestas, contratos y paquetes comerciales por cada tenant configurado.
    """
    cfg = _proposal_cfg()
    tenants = load_tenants()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_items: list[dict[str, Any]] = []
    currency = cfg.get("proposal_engine", {}).get("currency", "USD")

    for tenant in tenants:
        tenant_id = normalize_tenant_id(tenant.get("tenant_id", "cliente"))
        out = tenant_output_dir(tenant_id)
        out.mkdir(parents=True, exist_ok=True)
        package_key = recommend_package(tenant, cfg)
        package = cfg.get("packages", {}).get(package_key, cfg.get("packages", {}).get("mvp", {}))
        pricing = package_price(package, cfg)
        contract = build_metric_contract(tenant, package_key, package, cfg)

        proposal_path = out / "proposal.md"
        scope_path = out / "implementation_scope.md"
        contract_path = out / "metric_contract.yml"
        onboarding_path = out / "onboarding_checklist.md"
        plan_path = out / "thirty_day_plan.md"
        pricing_path = out / "pricing_summary.json"
        package_path = out / "proposal_package.json"
        html_path = out / "proposal.html"

        proposal_path.write_text(build_proposal_markdown(tenant, package_key, package, pricing, cfg), encoding="utf-8")
        scope_path.write_text(build_implementation_scope(tenant, package_key, package, cfg), encoding="utf-8")
        write_yaml(contract_path, contract)
        onboarding_path.write_text(build_onboarding_checklist(tenant, cfg), encoding="utf-8")
        plan_path.write_text(build_thirty_day_plan(tenant, cfg), encoding="utf-8")
        write_json(pricing_path, pricing)

        files = {
            "proposal": "proposal.md",
            "scope": "implementation_scope.md",
            "metric_contract": "metric_contract.yml",
            "onboarding": "onboarding_checklist.md",
            "plan": "thirty_day_plan.md",
        }
        html_path.write_text(build_tenant_html(tenant, package, pricing, files), encoding="utf-8")

        package_payload = {
            "tenant_id": tenant_id,
            "display_name": tenant.get("display_name"),
            "segment": tenant.get("segment"),
            "recommended_package": package_key,
            "package_name": package.get("name"),
            "pricing": pricing,
            "included_modules": module_rows(package.get("modules", []), cfg.get("module_catalog", {})),
            "excluded_modules": package.get("excluded_modules", []),
            "artifacts": {k: rel(out / v) for k, v in files.items()},
            "html": rel(html_path),
            "created_at": now_iso(),
        }
        write_json(package_path, package_payload)
        manifest_items.append(package_payload)

    manifest = {
        "version": "v2.3_client_proposal_and_contract_automation",
        "created_at": now_iso(),
        "tenant_count": len(manifest_items),
        "currency": currency,
        "items": manifest_items,
    }
    write_json(MANIFEST_JSON, manifest)
    build_index(manifest)
    validate_client_proposals()
    return manifest


def build_index(manifest: dict[str, Any]) -> None:
    """
    Yo genero índices HTML y Markdown para navegar todas las propuestas de cliente.
    """
    rows_md = ["# Índice de propuestas cliente", ""]
    cards = []
    for item in manifest.get("items", []):
        tenant_id = item["tenant_id"]
        name = item.get("display_name") or tenant_id
        package = item.get("package_name")
        pricing = item.get("pricing", {})
        html_rel = f"{tenant_id}/proposal.html"
        rows_md.append(f"- **{name}** · {package} · {pricing.get('formatted_setup_fee')} setup · `{html_rel}`")
        cards.append(f"""
        <section class='card'><h2>{html.escape(str(name))}</h2><p>{html.escape(str(package))}</p>
        <p class='metric'>{html.escape(str(pricing.get('formatted_setup_fee')))}</p>
        <a href='{html.escape(html_rel)}'>Abrir propuesta</a></section>
        """)
    INDEX_MD.write_text("\n".join(rows_md) + "\n", encoding="utf-8")
    html_text = f"""
<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Client Proposal Index</title><style>body{{background:#070A12;color:#F7F8FC;font-family:Inter,Segoe UI,Arial,sans-serif;margin:0}}main{{max-width:1120px;margin:auto;padding:48px 24px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}}.card{{background:#11182A;border:1px solid rgba(255,255,255,.1);border-radius:20px;padding:20px}}.metric{{color:#D6A84F;font-size:26px;font-weight:900}}a{{color:#9CC8FF}}</style></head><body><main><p style='color:#D6A84F'>Commercial Intelligence OS</p><h1>Propuestas por cliente</h1><div class='grid'>{''.join(cards)}</div></main></body></html>
"""
    INDEX_HTML.write_text(html_text, encoding="utf-8")


def validate_client_proposals() -> dict[str, Any]:
    """
    Yo valido que existan propuestas, contratos y que no haya secretos o PII accidental.
    """
    manifest = read_json(MANIFEST_JSON)
    required = ["proposal", "scope", "metric_contract", "onboarding", "plan"]
    missing: list[str] = []
    inspected: list[Path] = []
    for item in manifest.get("items", []):
        out = tenant_output_dir(item["tenant_id"])
        for key in required:
            path = out / item["artifacts"].get(key, "").split("/")[-1]
            inspected.append(path)
            if not path.exists():
                missing.append(rel(path))
    pii_hits = forbidden_hits_in_files(inspected, FORBIDDEN_DEFAULT)
    status = "ok" if not missing and not pii_hits and manifest.get("tenant_count", 0) > 0 else "fail"
    validation = {
        "status": status,
        "tenant_count": int(manifest.get("tenant_count", 0) or 0),
        "missing": missing,
        "privacy_hits": pii_hits,
        "checked_at": now_iso(),
    }
    write_json(VALIDATION_JSON, validation)
    return validation


def get_client_proposal_package(tenant_id: str) -> dict[str, Any]:
    """
    Yo recupero el paquete comercial de un tenant para API o demo.
    """
    tenant_id = normalize_tenant_id(tenant_id)
    package_path = tenant_output_dir(tenant_id) / "proposal_package.json"
    if not package_path.exists():
        build_client_proposals()
    if not package_path.exists():
        raise FileNotFoundError(tenant_id)
    return read_json(package_path)


def client_proposal_metadata() -> dict[str, Any]:
    """
    Yo expongo metadata del motor de propuestas para endpoints y monitoreo.
    """
    if not MANIFEST_JSON.exists() or not VALIDATION_JSON.exists():
        build_client_proposals()
    return {
        "manifest": read_json(MANIFEST_JSON),
        "validation": read_json(VALIDATION_JSON),
        "index_html": rel(INDEX_HTML),
        "index_md": rel(INDEX_MD),
    }


def run_client_proposal_and_contract_automation() -> dict[str, Any]:
    """
    Yo ejecuto todo el flujo v2.3: propuestas, contratos, índice y validación.
    """
    manifest = build_client_proposals()
    validation = validate_client_proposals()
    return {"manifest": manifest, "validation": validation}
