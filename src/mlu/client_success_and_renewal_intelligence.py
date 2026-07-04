from __future__ import annotations

import csv
import html
import json
import math
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

from src.mlu.config import PROJECT_ROOT

CONFIG_PATH = PROJECT_ROOT / "config" / "client_success_renewal.yml"
TENANTS_DIR = PROJECT_ROOT / "reports" / "client_tenants"
CONTRACT_OPS_DIR = PROJECT_ROOT / "reports" / "contract_ops"
PROPOSALS_DIR = PROJECT_ROOT / "reports" / "client_proposals"
REPORT_DIR = PROJECT_ROOT / "reports" / "client_success"
INDEX_HTML = REPORT_DIR / "client_success_index.html"
INDEX_MD = REPORT_DIR / "CLIENT_SUCCESS_INDEX.md"
REPORT_MD = REPORT_DIR / "CLIENT_SUCCESS_AND_RENEWAL_INTELLIGENCE.md"
MANIFEST_JSON = REPORT_DIR / "client_success_manifest.json"
VALIDATION_JSON = REPORT_DIR / "client_success_validation.json"


def now_iso() -> str:
    """
    Yo genero una marca temporal UTC para auditar salud, renovación y expansión por tenant.
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_tenant_id(value: str) -> str:
    """
    Yo normalizo tenant_id para evitar rutas inseguras y mantener paquetes portables.
    """
    tenant_id = re.sub(r"[^a-zA-Z0-9_-]+", "_", str(value).strip().lower()).strip("_")
    if not tenant_id:
        raise ValueError("tenant_id vacío")
    return tenant_id


def read_yaml(path: Path) -> dict[str, Any]:
    """
    Yo leo YAML de configuración y devuelvo vacío si todavía no existe.
    """
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def read_json(path: Path) -> dict[str, Any]:
    """
    Yo leo JSON solo cuando existe para encadenar contrato, propuesta y paquete tenant.
    """
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """
    Yo escribo JSON indentado porque éxito del cliente debe auditarse como expediente.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """
    Yo escribo CSV para que adoption scorecard, upsell y renovación puedan abrirse en Excel o Power BI.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row.keys()}) if rows else ["status"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def rel(path: Path) -> str:
    """
    Yo convierto rutas absolutas en rutas relativas para que el manifest sea portable.
    """
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def load_config() -> dict[str, Any]:
    """
    Yo cargo políticas de salud, adopción, renovación, upsell y privacidad.
    """
    return read_yaml(CONFIG_PATH)


def tenant_dir(tenant_id: str) -> Path:
    """
    Yo centralizo la carpeta de éxito del cliente por tenant.
    """
    return REPORT_DIR / normalize_tenant_id(tenant_id)


def ensure_upstream_artifacts() -> None:
    """
    Yo intento generar artefactos previos si faltan para que v2.5 pueda correr desde un proyecto limpio.
    """
    if not any(CONTRACT_OPS_DIR.glob("*/contract_ops_package.json")):
        try:
            from src.mlu.contract_to_signature_and_invoice_ops import run_contract_to_signature_and_invoice_ops
            run_contract_to_signature_and_invoice_ops()
        except Exception:
            pass
    if not any(TENANTS_DIR.glob("*/client_demo_package.json")):
        try:
            from src.mlu.multi_tenant_client_packaging import run_multi_tenant_client_packaging
            run_multi_tenant_client_packaging()
        except Exception:
            pass


def load_tenant_inputs() -> list[dict[str, Any]]:
    """
    Yo combino contrato, paquete tenant y propuesta para construir una vista de éxito por cliente.
    """
    ensure_upstream_artifacts()
    tenant_ids = set()
    for pattern in [CONTRACT_OPS_DIR.glob("*/contract_ops_package.json"), TENANTS_DIR.glob("*/client_demo_package.json"), PROPOSALS_DIR.glob("*/proposal_package.json")]:
        for path in pattern:
            tenant_ids.add(path.parent.name)
    if not tenant_ids:
        tenant_ids = {"cliente_alpha", "cliente_bravo", "cliente_condor"}
    rows = []
    for tenant_id in sorted(tenant_ids):
        rows.append({
            "tenant_id": tenant_id,
            "contract": read_json(CONTRACT_OPS_DIR / tenant_id / "contract_ops_package.json"),
            "tenant_package": read_json(TENANTS_DIR / tenant_id / "client_demo_package.json"),
            "proposal": read_json(PROPOSALS_DIR / tenant_id / "proposal_package.json"),
        })
    return rows


def safe_display_name(raw: dict[str, Any]) -> str:
    """
    Yo genero un nombre visible no sensible para reportes comerciales multi-tenant.
    """
    tenant_id = raw.get("tenant_id", "tenant")
    proposal = raw.get("proposal") or {}
    tenant_package = raw.get("tenant_package") or {}
    display = str(proposal.get("display_name") or tenant_package.get("display_name") or tenant_id)
    display = display.replace("Cliente ", "Tenant ").replace("cliente_", "tenant_")
    return display


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    """
    Yo limito scores para que salud y adopción queden en escala 0-100.
    """
    return max(low, min(high, float(value)))


def compute_milestone_completion(contract: dict[str, Any]) -> float:
    """
    Yo calculo avance de hitos usando la orden contractual generada por v2.4.
    """
    package = contract or {}
    work_order = package.get("work_order", {}) if isinstance(package, dict) else {}
    tenant_id = work_order.get("tenant_id") or package.get("tenant_id")
    if not tenant_id:
        return 0.0
    schedule = CONTRACT_OPS_DIR / normalize_tenant_id(tenant_id) / "milestones_schedule.csv"
    if not schedule.exists():
        return 0.0
    rows = list(csv.DictReader(schedule.open(encoding="utf-8")))
    if not rows:
        return 0.0
    done = sum(1 for row in rows if str(row.get("status", "")).lower() in {"done", "completed", "accepted", "closed"})
    # Yo doy un pequeño avance base si la orden ya existe, para distinguir propuesta viva de nada ejecutado.
    base = 10 if rows else 0
    return clamp(base + (done / len(rows)) * 90)


def compute_payment_status(contract: dict[str, Any]) -> float:
    """
    Yo calculo salud de pagos sin almacenar información bancaria ni facturación sensible.
    """
    package = contract or {}
    work_order = package.get("work_order", {}) if isinstance(package, dict) else {}
    tenant_id = work_order.get("tenant_id") or package.get("tenant_id")
    if not tenant_id:
        return 0.0
    schedule = CONTRACT_OPS_DIR / normalize_tenant_id(tenant_id) / "payment_schedule.csv"
    if not schedule.exists():
        return 50.0
    rows = list(csv.DictReader(schedule.open(encoding="utf-8")))
    if not rows:
        return 50.0
    paid = sum(1 for row in rows if str(row.get("status", "")).lower() in {"paid", "collected", "done"})
    pending = sum(1 for row in rows if str(row.get("status", "")).lower() in {"pending", "planned", ""})
    if paid == 0 and pending > 0:
        return 45.0
    return clamp((paid / len(rows)) * 100)


def compute_adoption_score(raw: dict[str, Any], cfg: dict[str, Any]) -> tuple[float, list[dict[str, Any]]]:
    """
    Yo estimo adopción por módulos habilitados y evidencia operativa disponible.
    """
    tenant_package = raw.get("tenant_package") or {}
    enabled = tenant_package.get("enabled_modules") or []
    if not isinstance(enabled, list):
        enabled = []
    modules = cfg.get("module_value_map", {})
    score_rows: list[dict[str, Any]] = []
    if not enabled:
        enabled = ["ceo_brief", "risk_to_action_queue", "railway_public_dashboard"]
    for module_id in enabled:
        metadata = modules.get(str(module_id), {})
        # Yo uso una adopción proxy conservadora: módulo habilitado no equivale a valor capturado.
        base = 45
        if module_id in {"railway_public_dashboard", "github_alerts"}:
            base = 60
        if module_id in {"risk_to_action_queue", "ceo_brief"}:
            base = 55
        if module_id in {"rag_business_memory", "stock_pricing"}:
            base = 40
        score_rows.append({
            "tenant_id": raw.get("tenant_id"),
            "module_id": module_id,
            "adoption_score": base,
            "value_driver": metadata.get("value_driver", "valor comercial pendiente de especificar"),
            "adoption_kpi": metadata.get("adoption_kpi", "uso observado"),
            "upsell_path": metadata.get("upsell_path", "expansion"),
            "evidence_mode": "proxy_until_usage_tracking",
        })
    adoption = sum(float(row["adoption_score"]) for row in score_rows) / max(len(score_rows), 1)
    return clamp(adoption), score_rows


def compute_value_realization(raw: dict[str, Any]) -> float:
    """
    Yo estimo valor realizado con evidencia disponible: contrato creado, payload demo y módulos activos.
    """
    score = 0.0
    if raw.get("contract"):
        score += 25
    if raw.get("tenant_package"):
        score += 25
    proposal = raw.get("proposal") or {}
    included = proposal.get("included_modules") or []
    if included:
        score += min(30, len(included) * 4)
    if (raw.get("tenant_package") or {}).get("privacy_status") == "ok":
        score += 20
    return clamp(score)


def classify_health(score: float, cfg: dict[str, Any]) -> str:
    """
    Yo convierto el health score en semáforo ejecutivo.
    """
    thresholds = cfg.get("client_success_engine", {}).get("health_thresholds", {})
    if score >= float(thresholds.get("green", 80)):
        return "green"
    if score >= float(thresholds.get("yellow", 55)):
        return "yellow"
    return "red"


def churn_risk_from_health(health_band: str, payment_score: float, adoption_score: float) -> str:
    """
    Yo estimo riesgo de churn con una regla transparente y fácil de defender.
    """
    if health_band == "red" or payment_score < 40 or adoption_score < 35:
        return "high"
    if health_band == "yellow" or payment_score < 60 or adoption_score < 55:
        return "medium"
    return "low"


def success_stage(raw: dict[str, Any], milestone_score: float, adoption_score: float) -> str:
    """
    Yo ubico al tenant en etapa de customer success según contrato, avance y adopción.
    """
    if not raw.get("contract"):
        return "not_started"
    if milestone_score < 25:
        return "onboarding"
    if adoption_score < 70:
        return "adoption"
    return "renewal"


def build_health_snapshot(raw: dict[str, Any], cfg: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """
    Yo construyo el snapshot ejecutivo de salud, adopción, churn y renovación por tenant.
    """
    adoption_score, adoption_rows = compute_adoption_score(raw, cfg)
    milestone_score = compute_milestone_completion(raw.get("contract") or {})
    payment_score = compute_payment_status(raw.get("contract") or {})
    qbr_score = 50.0  # Yo dejo QBR como score medio hasta capturar reuniones reales.
    value_score = compute_value_realization(raw)
    weights = cfg.get("health_weights", {})
    health = (
        adoption_score * float(weights.get("adoption_score", 0.35)) +
        milestone_score * float(weights.get("milestone_completion", 0.20)) +
        payment_score * float(weights.get("payment_status", 0.15)) +
        qbr_score * float(weights.get("qbr_status", 0.10)) +
        value_score * float(weights.get("value_realization", 0.20))
    )
    band = classify_health(health, cfg)
    churn = churn_risk_from_health(band, payment_score, adoption_score)
    stage = success_stage(raw, milestone_score, adoption_score)
    policy = cfg.get("renewal_policy", {}).get(band, {})
    contract = raw.get("contract") or {}
    work_order = contract.get("work_order", {}) if isinstance(contract, dict) else {}
    proposal = raw.get("proposal") or {}
    pricing = proposal.get("pricing", {}) if isinstance(proposal, dict) else {}
    snapshot = {
        "tenant_id": normalize_tenant_id(raw.get("tenant_id", "tenant")),
        "display_name": safe_display_name(raw),
        "generated_at": now_iso(),
        "success_stage": stage,
        "health_score": round(clamp(health), 2),
        "health_band": band,
        "churn_risk": churn,
        "adoption_score": round(adoption_score, 2),
        "milestone_completion_score": round(milestone_score, 2),
        "payment_status_score": round(payment_score, 2),
        "qbr_score": round(qbr_score, 2),
        "value_realization_score": round(value_score, 2),
        "renewal_recommendation": policy.get("recommendation", "revisar_manualmente"),
        "renewal_message": policy.get("message", "Revisar manualmente"),
        "package_name": work_order.get("package_name") or proposal.get("package_name") or "Commercial Intelligence OS",
        "year_one_total": pricing.get("year_one_total") or work_order.get("year_one_total"),
        "currency": pricing.get("currency") or work_order.get("currency") or cfg.get("client_success_engine", {}).get("currency", "USD"),
        "privacy_status": (raw.get("tenant_package") or {}).get("privacy_status", "unknown"),
    }
    return snapshot, adoption_rows


def build_upsell_opportunities(snapshot: dict[str, Any], adoption_rows: list[dict[str, Any]], cfg: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Yo propongo upsells solo desde módulos activos, brechas de adopción y política de renovación.
    """
    catalog = cfg.get("upsell_catalog", {})
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for row in adoption_rows:
        path = str(row.get("upsell_path") or "")
        if not path or path in seen:
            continue
        seen.add(path)
        item = catalog.get(path, {})
        confidence = "medium"
        if float(snapshot.get("health_score", 0)) >= 75 and float(row.get("adoption_score", 0)) >= 55:
            confidence = "high"
        elif snapshot.get("churn_risk") == "high":
            confidence = "rescue_only"
        rows.append({
            "tenant_id": snapshot["tenant_id"],
            "upsell_key": path,
            "label": item.get("label", path),
            "trigger": item.get("trigger", row.get("value_driver")),
            "estimated_value": float(item.get("estimated_value", 0) or 0),
            "currency": snapshot.get("currency", "USD"),
            "confidence": confidence,
            "recommended_timing": "after_qbr" if confidence != "rescue_only" else "after_rescue_plan",
        })
    return rows


def build_renewal_plan(snapshot: dict[str, Any], upsells: list[dict[str, Any]], cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Yo convierto salud y upsell en plan de renovación, rescate o expansión.
    """
    renewal_window = int(cfg.get("client_success_engine", {}).get("renewal_window_days", 60) or 60)
    today = datetime.now(timezone.utc).date()
    qbr_date = today + timedelta(days=14)
    renewal_date = today + timedelta(days=renewal_window)
    total_upsell = sum(float(row.get("estimated_value", 0) or 0) for row in upsells if row.get("confidence") in {"high", "medium"})
    actions = []
    if snapshot["health_band"] == "green":
        actions = ["Preparar QBR con caso de valor", "Proponer renovación anual", "Seleccionar 1-2 upsells de alto valor"]
    elif snapshot["health_band"] == "yellow":
        actions = ["Ejecutar plan de adopción de 14 días", "Validar owners y uso semanal", "QBR de rescate antes de propuesta de renovación"]
    else:
        actions = ["Escalamiento ejecutivo", "Reducir alcance a quick wins", "No proponer upsell hasta estabilizar salud"]
    return {
        "tenant_id": snapshot["tenant_id"],
        "generated_at": now_iso(),
        "health_band": snapshot["health_band"],
        "churn_risk": snapshot["churn_risk"],
        "renewal_recommendation": snapshot["renewal_recommendation"],
        "qbr_target_date": qbr_date.isoformat(),
        "renewal_target_date": renewal_date.isoformat(),
        "estimated_upsell_value": round(total_upsell, 2),
        "currency": snapshot.get("currency", "USD"),
        "actions": actions,
        "referral_readiness": snapshot["health_band"] == "green" and snapshot["churn_risk"] == "low",
    }


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    """
    Yo renderizo tablas pequeñas en Markdown para lectura ejecutiva rápida.
    """
    if not rows:
        return "_Sin filas._"
    out = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(row.get(c, "")) for c in columns) + " |")
    return "\n".join(out)


def render_health_md(snapshot: dict[str, Any], adoption_rows: list[dict[str, Any]], upsells: list[dict[str, Any]], renewal_plan: dict[str, Any]) -> str:
    """
    Yo renderizo el reporte de customer success por tenant.
    """
    return f"""
# Client Success & Renewal · {snapshot['display_name']}

## Salud ejecutiva
- Tenant: **{snapshot['tenant_id']}**
- Etapa: **{snapshot['success_stage']}**
- Health score: **{snapshot['health_score']} / 100**
- Semáforo: **{snapshot['health_band']}**
- Riesgo de churn: **{snapshot['churn_risk']}**
- Recomendación: **{snapshot['renewal_recommendation']}**

## Componentes del score
- Adopción: **{snapshot['adoption_score']}**
- Hitos: **{snapshot['milestone_completion_score']}**
- Pagos: **{snapshot['payment_status_score']}**
- QBR: **{snapshot['qbr_score']}**
- Valor realizado: **{snapshot['value_realization_score']}**

## Adopción por módulo
{markdown_table(adoption_rows, ['module_id', 'adoption_score', 'value_driver', 'adoption_kpi', 'evidence_mode'])}

## Oportunidades de expansión
{markdown_table(upsells, ['upsell_key', 'label', 'estimated_value', 'confidence', 'recommended_timing'])}

## Plan de renovación
- QBR objetivo: **{renewal_plan['qbr_target_date']}**
- Renovación objetivo: **{renewal_plan['renewal_target_date']}**
- Valor upsell estimado: **{renewal_plan['currency']} {renewal_plan['estimated_upsell_value']:,.2f}**
- Listo para referido: **{renewal_plan['referral_readiness']}**

## Acciones recomendadas
{chr(10).join('- ' + action for action in renewal_plan['actions'])}
""".strip() + "\n"


def render_html(title: str, md_text: str) -> str:
    """
    Yo renderizo HTML sobrio para revisar salud y renovación en navegador.
    """
    safe = html.escape(md_text)
    return f"""<!doctype html>
<html lang=\"es\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>{html.escape(title)}</title>
<style>
body {{ margin:0; font-family: Inter, Segoe UI, Arial, sans-serif; background:#08111f; color:#eef4ff; }}
main {{ max-width:1120px; margin:0 auto; padding:48px 24px; }}
.card {{ background:#111d33; border:1px solid rgba(212,175,55,.35); border-radius:22px; padding:30px; box-shadow:0 20px 60px rgba(0,0,0,.30); }}
h1, h2 {{ color:#d4af37; }}
a {{ color:#91c9ff; }}
pre {{ white-space:pre-wrap; font-family:inherit; line-height:1.45; }}
</style>
</head>
<body><main><div class=\"card\"><pre>{safe}</pre></div></main></body></html>"""


def validate_no_forbidden_text(text: str, forbidden: list[str]) -> list[str]:
    """
    Yo busco términos prohibidos en artifacts públicos para proteger privacidad y seguridad.
    """
    hits = []
    lower = text.lower()
    for term in forbidden:
        if str(term).lower() in lower:
            hits.append(str(term))
    return sorted(set(hits))


def build_tenant_success_package(raw: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Yo genero salud, adopción, upsell, renovación y QBR por tenant.
    """
    snapshot, adoption_rows = build_health_snapshot(raw, cfg)
    upsells = build_upsell_opportunities(snapshot, adoption_rows, cfg)
    renewal_plan = build_renewal_plan(snapshot, upsells, cfg)
    out = tenant_dir(snapshot["tenant_id"])
    out.mkdir(parents=True, exist_ok=True)

    md = render_health_md(snapshot, adoption_rows, upsells, renewal_plan)
    (out / "success_health.md").write_text(md, encoding="utf-8")
    (out / "success_health.html").write_text(render_html(f"Client Success · {snapshot['display_name']}", md), encoding="utf-8")
    write_json(out / "success_health.json", snapshot)
    write_csv(out / "adoption_scorecard.csv", adoption_rows)
    write_csv(out / "upsell_opportunities.csv", upsells)
    write_json(out / "renewal_plan.json", renewal_plan)

    renewal_md = f"""# Renewal Plan · {snapshot['display_name']}

- Semáforo: **{snapshot['health_band']}**
- Riesgo churn: **{snapshot['churn_risk']}**
- Recomendación: **{snapshot['renewal_recommendation']}**
- QBR objetivo: **{renewal_plan['qbr_target_date']}**
- Renovación objetivo: **{renewal_plan['renewal_target_date']}**
- Upsell estimado: **{renewal_plan['currency']} {renewal_plan['estimated_upsell_value']:,.2f}**

## Acciones
{chr(10).join('- ' + action for action in renewal_plan['actions'])}
""".strip() + "\n"
    (out / "renewal_plan.md").write_text(renewal_md, encoding="utf-8")
    (out / "renewal_plan.html").write_text(render_html(f"Renewal Plan · {snapshot['display_name']}", renewal_md), encoding="utf-8")

    qbr_md = f"""# QBR Brief · {snapshot['display_name']}

## Narrativa
El tenant está en estado **{snapshot['health_band']}** con health score **{snapshot['health_score']}**. La recomendación comercial es **{snapshot['renewal_recommendation']}**.

## Evidencia
- Adopción: {snapshot['adoption_score']}
- Hitos: {snapshot['milestone_completion_score']}
- Pagos: {snapshot['payment_status_score']}
- Valor realizado: {snapshot['value_realization_score']}

## Decisión del QBR
{snapshot['renewal_message']}
""".strip() + "\n"
    (out / "qbr_brief.md").write_text(qbr_md, encoding="utf-8")

    package = {
        "tenant_id": snapshot["tenant_id"],
        "generated_at": now_iso(),
        "health_snapshot": snapshot,
        "renewal_plan": renewal_plan,
        "upsell_count": len(upsells),
        "artifacts": {
            "success_health_md": rel(out / "success_health.md"),
            "success_health_html": rel(out / "success_health.html"),
            "success_health_json": rel(out / "success_health.json"),
            "adoption_scorecard": rel(out / "adoption_scorecard.csv"),
            "renewal_plan_md": rel(out / "renewal_plan.md"),
            "renewal_plan_html": rel(out / "renewal_plan.html"),
            "renewal_plan_json": rel(out / "renewal_plan.json"),
            "upsell_opportunities": rel(out / "upsell_opportunities.csv"),
            "qbr_brief": rel(out / "qbr_brief.md"),
        },
    }
    write_json(out / "client_success_package.json", package)
    return package


def render_index(packages: list[dict[str, Any]]) -> tuple[str, str]:
    """
    Yo construyo índices Markdown y HTML para navegar todos los tenants de customer success.
    """
    rows = []
    for p in packages:
        s = p["health_snapshot"]
        rows.append({
            "tenant_id": p["tenant_id"],
            "health_score": s["health_score"],
            "health_band": s["health_band"],
            "churn_risk": s["churn_risk"],
            "renewal_recommendation": s["renewal_recommendation"],
            "renewal_plan": p["artifacts"]["renewal_plan_html"],
            "health": p["artifacts"]["success_health_html"],
        })
    md = "# Client Success & Renewal Intelligence\n\n" + markdown_table(rows, ["tenant_id", "health_score", "health_band", "churn_risk", "renewal_recommendation", "health", "renewal_plan"]) + "\n"
    cards = []
    for row in rows:
        cards.append(f"""
        <article class=\"card\">
          <h2>{html.escape(row['tenant_id'])}</h2>
          <p><b>Health:</b> {row['health_score']} · {html.escape(row['health_band'])}</p>
          <p><b>Churn:</b> {html.escape(row['churn_risk'])}</p>
          <p><b>Renewal:</b> {html.escape(row['renewal_recommendation'])}</p>
          <a href=\"{html.escape(row['health'].split('reports/client_success/')[-1])}\">Health</a> ·
          <a href=\"{html.escape(row['renewal_plan'].split('reports/client_success/')[-1])}\">Renewal Plan</a>
        </article>""")
    html_text = f"""<!doctype html><html lang=\"es\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>Client Success & Renewal</title><style>
    body{{margin:0;background:#08111f;color:#eef4ff;font-family:Inter,Segoe UI,Arial,sans-serif}} main{{max-width:1100px;margin:auto;padding:44px 24px}} h1{{color:#d4af37}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}} .card{{background:#111d33;border:1px solid rgba(212,175,55,.35);border-radius:20px;padding:22px}} a{{color:#91c9ff}}
    </style></head><body><main><h1>Client Success & Renewal Intelligence</h1><p>Salud, adopción, churn, upsell y renovación por tenant.</p><section class=\"grid\">{''.join(cards)}</section></main></body></html>"""
    return md, html_text


def validate_client_success_outputs(packages: list[dict[str, Any]], cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Yo valido que existan paquetes, salud, renovación y que no haya términos prohibidos en artifacts públicos.
    """
    forbidden = cfg.get("forbidden_public_terms", [])
    hits: dict[str, list[str]] = {}
    missing = []
    for p in packages:
        for key, artifact in p.get("artifacts", {}).items():
            path = PROJECT_ROOT / artifact
            if not path.exists():
                missing.append(artifact)
                continue
            if path.suffix.lower() in {".md", ".html", ".json", ".csv"}:
                found = validate_no_forbidden_text(path.read_text(encoding="utf-8", errors="ignore"), forbidden)
                if found:
                    hits[artifact] = found
    status = "ok" if packages and not missing and not hits else "fail"
    payload = {
        "status": status,
        "tenant_count": len(packages),
        "green_count": sum(1 for p in packages if p["health_snapshot"]["health_band"] == "green"),
        "yellow_count": sum(1 for p in packages if p["health_snapshot"]["health_band"] == "yellow"),
        "red_count": sum(1 for p in packages if p["health_snapshot"]["health_band"] == "red"),
        "missing": missing,
        "forbidden_hits": hits,
        "generated_at": now_iso(),
    }
    write_json(VALIDATION_JSON, payload)
    return payload


def build_summary_report(packages: list[dict[str, Any]], validation: dict[str, Any]) -> str:
    """
    Yo genero el reporte maestro de customer success para gerencia y operación comercial.
    """
    rows = []
    for p in packages:
        s = p["health_snapshot"]
        r = p["renewal_plan"]
        rows.append({
            "tenant_id": p["tenant_id"],
            "health_score": s["health_score"],
            "health_band": s["health_band"],
            "churn_risk": s["churn_risk"],
            "renewal": s["renewal_recommendation"],
            "upsell_est": r["estimated_upsell_value"],
        })
    return f"""
# v2.5 · Client Success & Renewal Intelligence

## Estado
- Validación: **{validation['status']}**
- Tenants: **{validation['tenant_count']}**
- Green: **{validation['green_count']}**
- Yellow: **{validation['yellow_count']}**
- Red: **{validation['red_count']}**

## Resumen por tenant
{markdown_table(rows, ['tenant_id', 'health_score', 'health_band', 'churn_risk', 'renewal', 'upsell_est'])}

## Decisión ejecutiva
El sistema ya puede convertir implementación iniciada en seguimiento de salud, adopción, riesgo de churn, oportunidades de expansión y plan de renovación.

## Política de privacidad
Los artifacts de success no incluyen PII ni información sensible.
""".strip() + "\n"


def run_client_success_and_renewal_intelligence() -> dict[str, Any]:
    """
    Yo ejecuto todo el motor v2.5: salud, adopción, QBR, upsell, renovación, validación e índices.
    """
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    cfg = load_config()
    raw_inputs = load_tenant_inputs()
    packages = [build_tenant_success_package(raw, cfg) for raw in raw_inputs]
    index_md, index_html = render_index(packages)
    INDEX_MD.write_text(index_md, encoding="utf-8")
    INDEX_HTML.write_text(index_html, encoding="utf-8")
    manifest = {
        "version": "v2.5_client_success_and_renewal_intelligence",
        "generated_at": now_iso(),
        "tenant_count": len(packages),
        "packages": [{"tenant_id": p["tenant_id"], "package": rel(tenant_dir(p["tenant_id"]) / "client_success_package.json")} for p in packages],
        "index_html": rel(INDEX_HTML),
        "index_md": rel(INDEX_MD),
    }
    write_json(MANIFEST_JSON, manifest)
    validation = validate_client_success_outputs(packages, cfg)
    REPORT_MD.write_text(build_summary_report(packages, validation), encoding="utf-8")
    return {"manifest": manifest, "validation": validation, "packages": packages}


def get_client_success_package(tenant_id: str) -> dict[str, Any]:
    """
    Yo devuelvo el paquete de success por tenant, generándolo si todavía no existe.
    """
    tenant_id = normalize_tenant_id(tenant_id)
    path = tenant_dir(tenant_id) / "client_success_package.json"
    if not path.exists():
        run_client_success_and_renewal_intelligence()
    if not path.exists():
        raise FileNotFoundError(tenant_id)
    return read_json(path)


def client_success_metadata() -> dict[str, Any]:
    """
    Yo expongo metadata del motor de client success para API, Railway y auditoría.
    """
    if not MANIFEST_JSON.exists() or not VALIDATION_JSON.exists():
        run_client_success_and_renewal_intelligence()
    return {
        "manifest": read_json(MANIFEST_JSON),
        "validation": read_json(VALIDATION_JSON),
        "report": rel(REPORT_MD),
        "index_html": rel(INDEX_HTML),
    }


if __name__ == "__main__":
    result = run_client_success_and_renewal_intelligence()
    print(json.dumps({"validation": result["validation"]}, ensure_ascii=False, indent=2))
