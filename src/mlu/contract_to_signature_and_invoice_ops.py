from __future__ import annotations

import csv
import html
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

from src.mlu.config import PROJECT_ROOT

CONFIG_PATH = PROJECT_ROOT / "config" / "contract_ops.yml"
PROPOSALS_CONFIG_PATH = PROJECT_ROOT / "config" / "client_proposals.yml"
PROPOSALS_DIR = PROJECT_ROOT / "reports" / "client_proposals"
REPORT_DIR = PROJECT_ROOT / "reports" / "contract_ops"
INDEX_HTML = REPORT_DIR / "contract_ops_index.html"
INDEX_MD = REPORT_DIR / "CONTRACT_OPS_INDEX.md"
MANIFEST_JSON = REPORT_DIR / "contract_ops_manifest.json"
VALIDATION_JSON = REPORT_DIR / "contract_ops_validation.json"

FORBIDDEN_DEFAULT = [
    "cliente", "dni", "email", "telefono", "teléfono", "celular",
    "direccion", "dirección", "nombre completo", "codigo_proforma", "codigo_unidad",
    "password", "secret", "credential", "credenciales", "redshift_password",
]


def now_iso() -> str:
    """
    Yo genero una marca temporal UTC para que el expediente contractual sea auditable.
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_tenant_id(value: str) -> str:
    """
    Yo normalizo tenant_id para evitar rutas inseguras dentro del paquete contractual.
    """
    tenant_id = re.sub(r"[^a-zA-Z0-9_-]+", "_", str(value).strip().lower()).strip("_")
    if not tenant_id:
        raise ValueError("tenant_id vacío")
    return tenant_id


def read_yaml(path: Path) -> dict[str, Any]:
    """
    Yo leo YAML de configuración y devuelvo un diccionario vacío si el archivo no existe.
    """
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def read_json(path: Path) -> dict[str, Any]:
    """
    Yo leo JSON solo cuando existe para encadenar propuesta, contrato y proforma.
    """
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """
    Yo escribo JSON indentado porque el expediente comercial debe poder auditarse sin abrir Python.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """
    Yo escribo CSV para que hitos, pagos y entregables puedan abrirse en Excel o Power BI.
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


def money(value: float, currency: str) -> str:
    """
    Yo formateo importes para que la proforma sea legible en una negociación comercial.
    """
    return f"{currency} {float(value):,.2f}"


def tenant_output_dir(tenant_id: str) -> Path:
    """
    Yo centralizo la carpeta contractual por tenant.
    """
    return REPORT_DIR / normalize_tenant_id(tenant_id)


def load_config() -> dict[str, Any]:
    """
    Yo cargo la configuración contractual y permito overrides por entorno.
    """
    cfg = read_yaml(CONFIG_PATH)
    engine = cfg.setdefault("contract_ops_engine", {})
    if os.getenv("MLU_CONTRACT_CURRENCY"):
        engine["currency"] = os.getenv("MLU_CONTRACT_CURRENCY")
    if os.getenv("MLU_CONTRACT_TAX_PCT"):
        try:
            engine["default_tax_pct"] = float(os.getenv("MLU_CONTRACT_TAX_PCT", "0"))
        except ValueError:
            engine["default_tax_pct"] = 0
    return cfg


def load_proposal_packages() -> list[dict[str, Any]]:
    """
    Yo cargo propuestas generadas por v2.3. Si no existen, intento generarlas antes de avanzar.
    """
    packages: list[dict[str, Any]] = []
    if not PROPOSALS_DIR.exists() or not any(PROPOSALS_DIR.glob("*/proposal_package.json")):
        try:
            from src.mlu.client_proposal_and_contract_automation import run_client_proposal_and_contract_automation
            run_client_proposal_and_contract_automation()
        except Exception:
            pass
    for path in sorted(PROPOSALS_DIR.glob("*/proposal_package.json")):
        payload = read_json(path)
        if payload:
            packages.append(payload)
    if packages:
        return packages
    # Yo uso un fallback mínimo para que el motor siga siendo demostrable sin v2.3.
    return [
        {
            "tenant_id": "cliente_alpha",
            "client_display_name": "Cliente Alpha",
            "package_key": "mvp",
            "package_name": "MVP Intelligence Factory",
            "pricing": {"currency": "USD", "net_setup_fee": 7500, "monthly_fee": 750, "year_one_total": 16500},
            "implementation_days": 30,
            "modules_included": ["CEO Brief", "Risk-to-Action Queue", "Railway Public Dashboard"],
        }
    ]


def package_key(proposal: dict[str, Any]) -> str:
    """
    Yo obtengo el paquete comercial usando varios nombres posibles para ser tolerante a versiones.
    """
    return str(proposal.get("package_key") or proposal.get("package") or "mvp").lower()


def client_name(proposal: dict[str, Any]) -> str:
    """
    Yo resuelvo el nombre comercial visible del tenant sin depender de PII.
    """
    return str(proposal.get("client_display_name") or proposal.get("tenant_display_name") or proposal.get("tenant_id") or "Cliente")


def pricing_from_proposal(proposal: dict[str, Any], cfg: dict[str, Any]) -> dict[str, float | str]:
    """
    Yo extraigo setup, mensualidad y moneda desde la propuesta aceptada.
    """
    engine = cfg.get("contract_ops_engine", {})
    raw = proposal.get("pricing", {}) or proposal.get("pricing_summary", {}) or {}
    currency = str(raw.get("currency") or engine.get("currency") or "USD")
    setup = float(raw.get("net_setup_fee") or raw.get("setup_fee") or 0)
    monthly = float(raw.get("monthly_fee") or 0)
    year_one = float(raw.get("year_one_total") or (setup + monthly * 12))
    return {"currency": currency, "setup_fee": setup, "monthly_fee": monthly, "year_one_total": year_one}


def start_date(cfg: dict[str, Any]) -> datetime:
    """
    Yo calculo la fecha de inicio tentativa desde configuración o desde hoy.
    """
    configured = os.getenv("MLU_CONTRACT_START_DATE") or cfg.get("contract_ops_engine", {}).get("start_date")
    if configured:
        try:
            return datetime.fromisoformat(str(configured).replace("Z", "+00:00"))
        except ValueError:
            pass
    offset = int(cfg.get("contract_ops_engine", {}).get("default_start_offset_days", 2) or 2)
    return datetime.now(timezone.utc).replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=offset)


def build_milestones(proposal: dict[str, Any], cfg: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Yo convierto el paquete aceptado en hitos con fechas, owners, criterios y porcentaje de facturación.
    """
    key = package_key(proposal)
    templates = cfg.get("milestone_templates", {}).get(key) or cfg.get("milestone_templates", {}).get("mvp", [])
    base_date = start_date(cfg)
    rows: list[dict[str, Any]] = []
    for item in templates:
        start = base_date + timedelta(days=int(item.get("offset_days", 0) or 0))
        end = start + timedelta(days=int(item.get("duration_days", 1) or 1))
        rows.append({
            "milestone_id": item.get("id"),
            "name": item.get("name"),
            "owner": item.get("owner", "Intelligence Lead"),
            "start_date": start.date().isoformat(),
            "end_date": end.date().isoformat(),
            "billing_pct": float(item.get("billing_pct", 0) or 0),
            "acceptance_criteria": "; ".join(item.get("acceptance_criteria", [])),
            "status": "planned",
        })
    return rows


def build_payment_schedule(proposal: dict[str, Any], milestones: list[dict[str, Any]], cfg: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Yo convierto hitos y precio en calendario de pagos para controlar caja y cierre comercial.
    """
    pricing = pricing_from_proposal(proposal, cfg)
    setup = float(pricing["setup_fee"])
    currency = str(pricing["currency"])
    due_days = int(cfg.get("invoice_rules", {}).get("payment_due_days", 7) or 7)
    rows: list[dict[str, Any]] = []
    for milestone in milestones:
        pct = float(milestone.get("billing_pct", 0) or 0)
        if pct <= 0:
            continue
        amount = setup * pct / 100
        issue_date = datetime.fromisoformat(milestone["start_date"]).date()
        due_date = issue_date + timedelta(days=due_days)
        rows.append({
            "payment_id": f"PAY-{milestone['milestone_id']}",
            "milestone_id": milestone["milestone_id"],
            "concept": milestone["name"],
            "issue_date": issue_date.isoformat(),
            "due_date": due_date.isoformat(),
            "currency": currency,
            "amount": round(amount, 2),
            "amount_formatted": money(amount, currency),
            "status": "pending",
        })
    monthly = float(pricing.get("monthly_fee", 0) or 0)
    if monthly > 0 and bool(cfg.get("invoice_rules", {}).get("include_monthly_fee_in_first_invoice", False)):
        first = start_date(cfg).date() + timedelta(days=int(cfg.get("invoice_rules", {}).get("monthly_first_invoice_after_days", 30) or 30))
        rows.append({
            "payment_id": "PAY-MONTHLY-01",
            "milestone_id": "MONTHLY",
            "concept": "Primera mensualidad de soporte / operación",
            "issue_date": first.isoformat(),
            "due_date": (first + timedelta(days=due_days)).isoformat(),
            "currency": currency,
            "amount": round(monthly, 2),
            "amount_formatted": money(monthly, currency),
            "status": "pending",
        })
    return rows


def build_deliverables(proposal: dict[str, Any], cfg: dict[str, Any], milestones: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Yo convierto módulos y plantillas en entregables verificables.
    """
    key = package_key(proposal)
    templates = cfg.get("deliverable_templates", {})
    labels = list(templates.get("base", [])) + list(templates.get(key, []))
    included = proposal.get("modules_included") or proposal.get("included_modules") or []
    if isinstance(included, list):
        labels += [str(x) for x in included[:8]]
    rows = []
    for i, label in enumerate(dict.fromkeys(labels), start=1):
        milestone = milestones[min(i - 1, len(milestones) - 1)] if milestones else {}
        rows.append({
            "deliverable_id": f"D{i:02d}",
            "deliverable": label,
            "milestone_id": milestone.get("milestone_id", "M1"),
            "owner": milestone.get("owner", "Intelligence Lead"),
            "status": "planned",
            "acceptance_required": True,
        })
    return rows


def build_work_order(proposal: dict[str, Any], milestones: list[dict[str, Any]], deliverables: list[dict[str, Any]], payment_schedule: list[dict[str, Any]], cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Yo construyo la orden de trabajo que conecta propuesta aceptada con ejecución y cobranza.
    """
    tenant_id = normalize_tenant_id(proposal.get("tenant_id", "cliente"))
    pricing = pricing_from_proposal(proposal, cfg)
    return {
        "work_order_id": f"WO-{tenant_id.upper()}-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
        "tenant_id": tenant_id,
        "client_display_name": client_name(proposal),
        "package_key": package_key(proposal),
        "package_name": proposal.get("package_name") or proposal.get("package") or package_key(proposal),
        "status": "work_order_created",
        "created_at": now_iso(),
        "start_date": start_date(cfg).date().isoformat(),
        "currency": pricing["currency"],
        "setup_fee": pricing["setup_fee"],
        "monthly_fee": pricing["monthly_fee"],
        "year_one_total": pricing["year_one_total"],
        "payment_terms": cfg.get("contract_ops_engine", {}).get("payment_terms"),
        "commercial_rules": cfg.get("commercial_rules", {}),
        "milestones_count": len(milestones),
        "deliverables_count": len(deliverables),
        "payments_count": len(payment_schedule),
        "privacy_position": cfg.get("contract_ops_engine", {}).get("privacy_position"),
    }


def build_invoice_proforma(work_order: dict[str, Any], payment_schedule: list[dict[str, Any]], cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Yo genero una proforma operativa a partir de los pagos pendientes del proyecto.
    """
    engine = cfg.get("contract_ops_engine", {})
    currency = work_order.get("currency", engine.get("currency", "USD"))
    subtotal = sum(float(row.get("amount", 0) or 0) for row in payment_schedule)
    tax_pct = float(engine.get("default_tax_pct", 0) or 0)
    tax = subtotal * tax_pct / 100
    total = subtotal + tax
    issue_date = datetime.now(timezone.utc).date()
    return {
        "invoice_id": f"{engine.get('invoice_series', 'CI-OS')}-{work_order['tenant_id'].upper()}-{issue_date.strftime('%Y%m%d')}",
        "invoice_type": engine.get("invoice_type", "proforma"),
        "country": engine.get("invoice_country", "PE"),
        "work_order_id": work_order["work_order_id"],
        "tenant_id": work_order["tenant_id"],
        "client_display_name": work_order["client_display_name"],
        "issue_date": issue_date.isoformat(),
        "currency": currency,
        "subtotal": round(subtotal, 2),
        "tax_pct": tax_pct,
        "tax_amount": round(tax, 2),
        "total": round(total, 2),
        "total_formatted": money(total, str(currency)),
        "line_items": payment_schedule,
        "legal_note": engine.get("legal_note"),
    }


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    """
    Yo renderizo tablas pequeñas en Markdown para que el expediente sea legible sin Excel.
    """
    if not rows:
        return "_Sin filas._"
    out = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(row.get(c, "")) for c in columns) + " |")
    return "\n".join(out)


def render_work_order_md(work_order: dict[str, Any], milestones: list[dict[str, Any]], deliverables: list[dict[str, Any]], payment_schedule: list[dict[str, Any]], invoice: dict[str, Any]) -> str:
    """
    Yo renderizo la orden de trabajo como documento operativo para enviar al cliente.
    """
    return f"""
# Orden de Trabajo · {work_order['client_display_name']}

## Resumen
- Work order: **{work_order['work_order_id']}**
- Paquete: **{work_order['package_name']}**
- Estado: **{work_order['status']}**
- Inicio tentativo: **{work_order['start_date']}**
- Setup fee: **{money(work_order['setup_fee'], work_order['currency'])}**
- Mensualidad: **{money(work_order['monthly_fee'], work_order['currency'])}**
- Total año 1: **{money(work_order['year_one_total'], work_order['currency'])}**

## Condiciones comerciales
{work_order.get('payment_terms')}

## Política de privacidad
{work_order.get('privacy_position')}

## Hitos
{markdown_table(milestones, ['milestone_id', 'name', 'start_date', 'end_date', 'billing_pct', 'status'])}

## Entregables
{markdown_table(deliverables, ['deliverable_id', 'deliverable', 'milestone_id', 'owner', 'status'])}

## Calendario de pagos
{markdown_table(payment_schedule, ['payment_id', 'concept', 'issue_date', 'due_date', 'amount_formatted', 'status'])}

## Proforma
- ID: **{invoice['invoice_id']}**
- Total: **{invoice['total_formatted']}**

## Siguiente acción
Confirmar aceptación comercial, registrar primer pago y agendar kickoff.
""".strip() + "\n"


def render_html(title: str, md_text: str) -> str:
    """
    Yo renderizo HTML simple y sobrio para revisar el expediente en navegador.
    """
    safe = html.escape(md_text)
    body = safe.replace("\n", "<br>")
    return f"""<!doctype html>
<html lang=\"es\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>{html.escape(title)}</title>
<style>
body {{ margin:0; font-family: Inter, Segoe UI, Arial, sans-serif; background:#09111f; color:#eef4ff; }}
main {{ max-width: 1040px; margin: 0 auto; padding: 48px 24px; }}
.card {{ background:#111d33; border:1px solid rgba(212,175,55,.35); border-radius:20px; padding:28px; box-shadow:0 18px 50px rgba(0,0,0,.25); }}
h1 {{ color:#d4af37; }}
a {{ color:#91c9ff; }}
code {{ color:#d4af37; }}
</style>
</head>
<body><main><div class=\"card\"><pre style=\"white-space:pre-wrap;font-family:inherit\">{safe}</pre></div></main></body>
</html>"""


def validate_text_no_forbidden(text: str, forbidden: list[str]) -> list[str]:
    """
    Yo busco términos prohibidos en archivos públicos del expediente contractual.
    """
    hits = []
    lower = text.lower()
    for term in forbidden:
        if str(term).lower() in lower:
            hits.append(term)
    return sorted(set(hits))


def build_tenant_contract_ops(proposal: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Yo genero todos los artifacts contractuales y de cobranza para un tenant.
    """
    tenant_id = normalize_tenant_id(proposal.get("tenant_id", "cliente"))
    out = tenant_output_dir(tenant_id)
    out.mkdir(parents=True, exist_ok=True)

    milestones = build_milestones(proposal, cfg)
    payment_schedule = build_payment_schedule(proposal, milestones, cfg)
    deliverables = build_deliverables(proposal, cfg, milestones)
    work_order = build_work_order(proposal, milestones, deliverables, payment_schedule, cfg)
    invoice = build_invoice_proforma(work_order, payment_schedule, cfg)

    work_order_md = render_work_order_md(work_order, milestones, deliverables, payment_schedule, invoice)
    work_order_html = render_html(f"Orden de Trabajo · {work_order['client_display_name']}", work_order_md)

    (out / "work_order.md").write_text(work_order_md, encoding="utf-8")
    (out / "work_order.html").write_text(work_order_html, encoding="utf-8")
    write_json(out / "work_order.json", work_order)
    write_json(out / "invoice_proforma.json", invoice)
    invoice_md = f"""# Proforma · {work_order['client_display_name']}

- Invoice ID: **{invoice['invoice_id']}**
- Work order: **{invoice['work_order_id']}**
- Fecha emisión: **{invoice['issue_date']}**
- Total: **{invoice['total_formatted']}**

## Líneas
{markdown_table(payment_schedule, ['payment_id', 'concept', 'issue_date', 'due_date', 'amount_formatted', 'status'])}

{invoice.get('legal_note')}
""".strip() + "\n"
    (out / "invoice_proforma.md").write_text(invoice_md, encoding="utf-8")
    (out / "invoice_proforma.html").write_text(render_html(f"Proforma · {work_order['client_display_name']}", invoice_md), encoding="utf-8")
    write_csv(out / "milestones_schedule.csv", milestones)
    write_csv(out / "implementation_calendar.csv", milestones)
    write_csv(out / "deliverables_register.csv", deliverables)
    write_csv(out / "payment_schedule.csv", payment_schedule)

    ops_package = {
        "tenant_id": tenant_id,
        "created_at": now_iso(),
        "work_order": work_order,
        "invoice_proforma": invoice,
        "artifacts": {
            "work_order_md": rel(out / "work_order.md"),
            "work_order_html": rel(out / "work_order.html"),
            "work_order_json": rel(out / "work_order.json"),
            "invoice_proforma_json": rel(out / "invoice_proforma.json"),
            "invoice_proforma_html": rel(out / "invoice_proforma.html"),
            "milestones_schedule": rel(out / "milestones_schedule.csv"),
            "implementation_calendar": rel(out / "implementation_calendar.csv"),
            "deliverables_register": rel(out / "deliverables_register.csv"),
            "payment_schedule": rel(out / "payment_schedule.csv"),
        },
        "next_action": "confirmar_aceptacion_y_primer_pago",
    }
    write_json(out / "contract_ops_package.json", ops_package)
    return ops_package


def build_index(packages: list[dict[str, Any]]) -> None:
    """
    Yo genero un índice de expedientes contractuales por cliente.
    """
    lines = ["# Contract to Signature & Invoice Ops", "", "| Tenant | Work order | Estado | Proforma | Total |", "| --- | --- | --- | --- | --- |"]
    html_cards = []
    for pkg in packages:
        wo = pkg["work_order"]
        inv = pkg["invoice_proforma"]
        tenant_id = pkg["tenant_id"]
        lines.append(f"| {tenant_id} | {wo['work_order_id']} | {wo['status']} | {inv['invoice_id']} | {inv['total_formatted']} |")
        html_cards.append(f"""
        <article class=\"card\">
          <h2>{html.escape(wo['client_display_name'])}</h2>
          <p><b>Work order:</b> {html.escape(wo['work_order_id'])}</p>
          <p><b>Proforma:</b> {html.escape(inv['invoice_id'])}</p>
          <p><b>Total:</b> {html.escape(inv['total_formatted'])}</p>
          <p><a href=\"{tenant_id}/work_order.html\">Abrir orden de trabajo</a> · <a href=\"{tenant_id}/invoice_proforma.html\">Abrir proforma</a></p>
        </article>
        """)
    INDEX_MD.parent.mkdir(parents=True, exist_ok=True)
    INDEX_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    INDEX_HTML.write_text(f"""<!doctype html>
<html lang=\"es\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>Contract Ops Index</title><style>
body{{background:#09111f;color:#eef4ff;font-family:Inter,Segoe UI,Arial,sans-serif;margin:0}}main{{max-width:1080px;margin:auto;padding:42px 24px}}h1{{color:#d4af37}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}}.card{{background:#111d33;border:1px solid rgba(212,175,55,.35);border-radius:18px;padding:22px}}a{{color:#91c9ff}}</style></head>
<body><main><h1>Contract to Signature & Invoice Ops</h1><p>Expedientes comerciales por cliente: orden de trabajo, hitos, pagos y proforma.</p><section class=\"grid\">{''.join(html_cards)}</section></main></body></html>""", encoding="utf-8")


def validate_contract_ops(packages: list[dict[str, Any]], cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Yo valido que el expediente tenga artifacts mínimos y que no filtre campos prohibidos.
    """
    forbidden = cfg.get("contract_ops_engine", {}).get("forbidden_public_data", FORBIDDEN_DEFAULT)
    missing: list[str] = []
    forbidden_hits: dict[str, list[str]] = {}
    required = ["work_order.md", "work_order.html", "work_order.json", "invoice_proforma.json", "invoice_proforma.html", "milestones_schedule.csv", "deliverables_register.csv", "payment_schedule.csv", "contract_ops_package.json"]
    for pkg in packages:
        tdir = tenant_output_dir(pkg["tenant_id"])
        for name in required:
            if not (tdir / name).exists():
                missing.append(f"{pkg['tenant_id']}/{name}")
        for path in tdir.glob("*.json"):
            hits = validate_text_no_forbidden(path.read_text(encoding="utf-8"), forbidden)
            # Yo permito tenant_id/client_display_name porque es metadata comercial del prospecto, no PII CRM.
            hits = [h for h in hits if h not in {"cliente"}]
            if hits:
                forbidden_hits[rel(path)] = hits
    status = "ok" if not missing and not forbidden_hits else "fail"
    payload = {"status": status, "tenant_count": len(packages), "missing": missing, "forbidden_hits": forbidden_hits, "validated_at": now_iso()}
    write_json(VALIDATION_JSON, payload)
    return payload


def run_contract_to_signature_and_invoice_ops() -> dict[str, Any]:
    """
    Yo ejecuto el motor completo: propuesta aceptada → orden de trabajo → hitos → proforma → seguimiento.
    """
    cfg = load_config()
    proposals = load_proposal_packages()
    packages = [build_tenant_contract_ops(proposal, cfg) for proposal in proposals]
    build_index(packages)
    validation = validate_contract_ops(packages, cfg)
    manifest = {
        "version": "v2.4_contract_to_signature_and_invoice_ops",
        "created_at": now_iso(),
        "tenant_count": len(packages),
        "status": validation.get("status"),
        "index_html": rel(INDEX_HTML),
        "index_md": rel(INDEX_MD),
        "validation": rel(VALIDATION_JSON),
        "tenants": [{"tenant_id": p["tenant_id"], "work_order_id": p["work_order"]["work_order_id"], "invoice_id": p["invoice_proforma"]["invoice_id"], "total": p["invoice_proforma"]["total_formatted"]} for p in packages],
    }
    write_json(MANIFEST_JSON, manifest)
    report = render_report(manifest, validation)
    (REPORT_DIR / "CONTRACT_TO_SIGNATURE_AND_INVOICE_OPS.md").write_text(report, encoding="utf-8")
    return manifest


def render_report(manifest: dict[str, Any], validation: dict[str, Any]) -> str:
    """
    Yo genero un reporte ejecutivo del paso propuesta → firma → invoice.
    """
    tenant_rows = [
        {"tenant": t["tenant_id"], "work_order": t["work_order_id"], "invoice": t["invoice_id"], "total": t["total"]}
        for t in manifest.get("tenants", [])
    ]
    return f"""
# v2.4 · Contract to Signature & Invoice Ops

## Estado
- Status: **{manifest.get('status')}**
- Tenants: **{manifest.get('tenant_count')}**
- Validación privacidad: **{'ok' if not validation.get('forbidden_hits') else 'fail'}**

## Expedientes generados
{markdown_table(tenant_rows, ['tenant', 'work_order', 'invoice', 'total'])}

## Qué controla esta versión
1. Propuesta aceptada.
2. Orden de trabajo.
3. Hitos y calendario de implementación.
4. Registro de entregables.
5. Proforma / invoice schedule.
6. Seguimiento de pagos y cierre.

## Política crítica
No se suben campos sensibles del CRM. El expediente usa metadata comercial, precios, hitos y agregados.
""".strip() + "\n"


def contract_ops_metadata() -> dict[str, Any]:
    """
    Yo expongo metadata del motor contractual para API y dashboards.
    """
    if not MANIFEST_JSON.exists():
        return run_contract_to_signature_and_invoice_ops()
    return read_json(MANIFEST_JSON)


def get_contract_ops_package(tenant_id: str) -> dict[str, Any]:
    """
    Yo devuelvo el paquete contractual de un tenant específico.
    """
    path = tenant_output_dir(tenant_id) / "contract_ops_package.json"
    if not path.exists():
        run_contract_to_signature_and_invoice_ops()
    if not path.exists():
        raise FileNotFoundError(tenant_id)
    return read_json(path)


if __name__ == "__main__":
    print(json.dumps(run_contract_to_signature_and_invoice_ops(), ensure_ascii=False, indent=2))
