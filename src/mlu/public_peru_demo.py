from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from src.mlu.config import PROJECT_ROOT
from src.mlu.client_ready_branding_and_deployment import build_brand_css, read_json

CONFIG_PATH = PROJECT_ROOT / "config" / "public_peru_client_examples.yml"
REPORT_DIR = PROJECT_ROOT / "reports" / "client_ready_branding"
LANDING_HTML = REPORT_DIR / "LANDING_PAGE_CLIENT_DEMO.html"
PUBLIC_EXAMPLES_JSON = REPORT_DIR / "public_peru_client_examples.json"
PUBLIC_PAYLOAD = PROJECT_ROOT / "reports" / "public" / "decision_dashboard_payload_public.json"

FORBIDDEN_PUBLIC_TERMS = {
    "dni",
    "documento",
    "telefono",
    "teléfono",
    "email",
    "correo",
    "direccion",
    "dirección",
    "codigo_proforma",
    "codigo_unidad",
    "password",
    "secret",
    "redshift",
}


def now_iso() -> str:
    """
    Yo genero una marca temporal UTC para auditar cuándo se construyó la demo pública.
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_yaml(path: Path = CONFIG_PATH) -> dict[str, Any]:
    """
    Yo cargo ejemplos públicos de inmobiliarias peruanas desde configuración, no desde CRM privado.
    """
    if not path.exists():
        return {"companies": []}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {"companies": []}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """
    Yo escribo un JSON público auditable con solo referencias agregadas y fuentes públicas.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _money(value: Any) -> str:
    """
    Yo formateo montos agregados para demo ejecutiva sin tocar filas privadas.
    """
    try:
        return f"S/ {float(value):,.0f}"
    except Exception:
        return "S/ N/D"


def load_safe_public_payload() -> dict[str, Any]:
    """
    Yo leo el payload público agregado y devuelvo valores mínimos si aún no existe.
    """
    payload = read_json(PUBLIC_PAYLOAD)
    if not payload:
        return {
            "total_operaciones": "N/D",
            "valor_total_en_riesgo": "N/D",
            "riesgo_promedio": "N/D",
            "p0_p1": "N/D",
            "fecha_generacion": now_iso(),
            "data_mode": "public_market_examples",
        }
    return payload


def public_examples_metadata() -> dict[str, Any]:
    """
    Yo expongo metadata de los ejemplos públicos sin convertirlos en clientes reales.
    """
    cfg = load_yaml()
    payload = {
        "version": cfg.get("version", "2.6.0"),
        "release_name": cfg.get("release_name", "v2.6_public_peru_demo_and_dashboard_route_fix"),
        "mode": cfg.get("mode", "public_market_examples"),
        "disclaimer": cfg.get("disclaimer"),
        "company_count": len(cfg.get("companies", [])),
        "companies": cfg.get("companies", []),
        "allowed_public_fields": cfg.get("allowed_public_fields", []),
        "generated_at": now_iso(),
    }
    write_json(PUBLIC_EXAMPLES_JSON, payload)
    return payload


def validate_public_examples(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Yo valido que la demo pública no incluya campos obvios de PII o credenciales.
    """
    payload = payload or public_examples_metadata()
    text = json.dumps(payload, ensure_ascii=False).lower()
    hits = sorted(term for term in FORBIDDEN_PUBLIC_TERMS if term in text)
    # Yo permito source_urls porque son referencias públicas; bloqueo el resto de términos sensibles.
    hits = [hit for hit in hits if hit not in {"email", "correo"}]
    return {
        "status": "ok" if not hits else "fail",
        "forbidden_hits": hits,
        "company_count": payload.get("company_count", 0),
        "expected_company_count": 3,
    }


def _list_html(items: list[Any]) -> str:
    """
    Yo renderizo listas públicas de forma simple para la landing.
    """
    if not items:
        return "<li>Sin señales públicas configuradas.</li>"
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in items)


def _company_card(company: dict[str, Any]) -> str:
    """
    Yo convierto una inmobiliaria pública de ejemplo en una tarjeta comercial segura.
    """
    footprint = company.get("public_footprint", {})
    sources = company.get("source_urls", [])
    source_links = "".join(
        f"<a class='mini-link' href='{html.escape(str(url))}' target='_blank' rel='noopener'>fuente</a>"
        for url in sources[:2]
    )
    focus = company.get("example_dashboard_focus", [])
    return f"""
    <article class='company-card'>
      <div class='company-topline'>{html.escape(str(company.get('public_segment', 'Inmobiliaria')))}</div>
      <h3>{html.escape(str(company.get('company_name', 'Ejemplo público')))}</h3>
      <p>{html.escape(str(company.get('public_positioning', 'Referencia pública de mercado.')))}</p>
      <div class='mini-grid'>
        <div><strong>{html.escape(str(footprint.get('public_years_reference', 'N/D')))}</strong><span>Trayectoria pública</span></div>
        <div><strong>{html.escape(str(footprint.get('public_units_reference', 'N/D')))}</strong><span>Escala pública</span></div>
        <div><strong>{html.escape(str(footprint.get('public_projects_reference', 'N/D')))}</strong><span>Portafolio público</span></div>
      </div>
      <p class='location'>{html.escape(str(footprint.get('public_locations_reference', 'Ubicaciones públicas configuradas.')))}</p>
      <h4>Qué analizaría el sistema</h4>
      <ul>{_list_html(company.get('use_case_fit', []))}</ul>
      <h4>Dashboards ejemplo</h4>
      <div class='chips'>{''.join(f"<span>{html.escape(str(x))}</span>" for x in focus)}</div>
      <div class='sources'>{source_links}</div>
    </article>
    """


def build_public_peru_demo_html() -> Path:
    """
    Yo construyo una landing de cliente usando ejemplos públicos peruanos y payload CRM agregado.
    """
    cfg = load_yaml()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    metadata = public_examples_metadata()
    validation = validate_public_examples(metadata)
    if validation["status"] != "ok":
        raise RuntimeError(f"Demo pública contiene términos prohibidos: {validation['forbidden_hits']}")

    public_payload = load_safe_public_payload()
    css = build_brand_css({
        "brand": {
            "palette": {
                "background": "#070A12",
                "surface": "#10182A",
                "surface_2": "#151F35",
                "gold": "#D6A84F",
                "blue": "#6EA8FE",
                "text": "#F5F7FB",
                "muted": "#AAB4C8",
                "success": "#38D39F",
                "warning": "#FFC857",
                "danger": "#FF5C7A",
            },
            "typography": {"body": "Inter, Segoe UI, Arial, sans-serif"},
        }
    })
    extra_css = """
.company-section{max-width:1180px;margin:20px auto 70px;padding:0 24px}.section-head{margin:16px 0 22px}.section-head h2{font-size:34px;margin:0 0 8px}.company-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px}.company-card{background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.025));border:1px solid rgba(214,168,79,.25);border-radius:22px;padding:22px}.company-topline{color:var(--gold);font-size:11px;letter-spacing:.12em;text-transform:uppercase;font-weight:800}.company-card h3{font-size:28px;margin:8px 0}.company-card h4{margin:20px 0 8px;color:#f3d48a}.mini-grid{display:grid;grid-template-columns:1fr;gap:8px;margin:16px 0}.mini-grid div{background:rgba(0,0,0,.18);border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:10px}.mini-grid strong{display:block;color:var(--gold)}.mini-grid span{font-size:12px;color:var(--muted)}.location{font-size:14px}.chips{display:flex;gap:8px;flex-wrap:wrap}.chips span{border:1px solid rgba(110,168,254,.30);background:rgba(110,168,254,.10);border-radius:999px;padding:7px 10px;font-size:12px}.sources{margin-top:14px}.mini-link{display:inline-block;margin-right:8px;color:#0b1220;background:var(--gold);padding:7px 10px;border-radius:999px;font-weight:800}.disclaimer{max-width:1180px;margin:0 auto 28px;padding:0 24px;color:var(--muted);font-size:14px}.route-card a{display:block;margin:8px 0}.metric-label{color:var(--muted);font-size:13px}.payload-card .metric{letter-spacing:-.02em}
"""
    cards = "".join(_company_card(c) for c in cfg.get("companies", []))
    routes = [
        ("Dashboard Público Seguro", "/public/decision-dashboard"),
        ("Catálogo de Dashboards", "/dashboard/catalog"),
        ("Action Feedback", "/dashboard/action-feedback"),
        ("Experiment Policy", "/dashboard/experiment-power-policy"),
        ("Demo Package", "/product/demo/package"),
        ("Swagger API Docs", "/docs"),
    ]
    route_links = "".join(f"<a class='btn secondary' href='{url}'>{html.escape(label)}</a>" for label, url in routes)
    html_text = f"""<!doctype html>
<html lang='es'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Commercial Intelligence OS · Demo Perú</title>
<style>{css}\n{extra_css}</style>
</head>
<body>
  <main class='hero'>
    <div class='eyebrow'>EconoAgents Intelligence Factory · Demo pública Perú</div>
    <h1>Inteligencia comercial inmobiliaria con ejemplos públicos peruanos.</h1>
    <p>Yo muestro cómo el sistema analizaría perfiles inmobiliarios peruanos usando señales públicas y payloads agregados. Cuando conectes una base histórica real, reemplazas estos ejemplos por métricas CRM agregadas por cliente.</p>
    <div class='cta-row'>
      <a class='btn' href='/public/decision-dashboard'>Ver dashboard seguro</a>
      <a class='btn secondary' href='/dashboard/catalog'>Explorar catálogo</a>
    </div>
  </main>

  <section class='grid'>
    <div class='card payload-card'><h3>Operaciones evaluadas</h3><div class='metric'>{html.escape(str(public_payload.get('total_operaciones', 'N/D')))}</div><p class='metric-label'>Payload CRM agregado si existe; sin filas operativas.</p></div>
    <div class='card payload-card'><h3>Valor en riesgo</h3><div class='metric'>{html.escape(_money(public_payload.get('valor_total_en_riesgo')))}</div><p class='metric-label'>Lectura ejecutiva agregada.</p></div>
    <div class='card payload-card'><h3>Riesgo promedio</h3><div class='metric'>{html.escape(str(public_payload.get('riesgo_promedio', 'N/D')))}</div><p class='metric-label'>Modo: <code>{html.escape(str(public_payload.get('data_mode', 'public_market_examples')))}</code></p></div>
    <div class='card payload-card'><h3>P0 + P1</h3><div class='metric'>{html.escape(str(public_payload.get('p0_p1', 'N/D')))}</div><p class='metric-label'>Operaciones agregadas que requieren SLA.</p></div>
  </section>

  <section class='company-section'>
    <div class='section-head'>
      <div class='eyebrow'>Análisis público publicado en docs y Railway</div>
      <h2>{html.escape(str(cfg.get('cards', {}).get('headline', 'Ejemplos públicos')))}</h2>
      <p>{html.escape(str(cfg.get('cards', {}).get('subheadline', 'Referencias públicas de mercado.')))}</p>
    </div>
    <div class='company-grid'>{cards}</div>
  </section>

  <section class='grid'>
    <div class='card route-card' style='grid-column:1/-1'>
      <h3>Rutas priorizadas</h3>
      <p>Yo mantengo Railway como demo viva y GitHub Pages como hub público de links.</p>
      <div class='cta-row'>{route_links}</div>
    </div>
  </section>

  <div class='disclaimer'><strong>Gobierno:</strong> {html.escape(str(cfg.get('disclaimer', 'Solo ejemplos públicos.')))} Generado: {now_iso()}.</div>
</body>
</html>"""
    LANDING_HTML.write_text(html_text, encoding="utf-8")
    return LANDING_HTML


def run_public_peru_demo_build() -> dict[str, Any]:
    """
    Yo ejecuto la generación completa de la landing pública Perú y devuelvo un manifiesto mínimo.
    """
    path = build_public_peru_demo_html()
    meta = public_examples_metadata()
    validation = validate_public_examples(meta)
    return {
        "status": validation["status"],
        "landing_html": str(path.relative_to(PROJECT_ROOT)),
        "examples_json": str(PUBLIC_EXAMPLES_JSON.relative_to(PROJECT_ROOT)),
        "company_count": meta.get("company_count", 0),
        "validation": validation,
        "generated_at": now_iso(),
    }
