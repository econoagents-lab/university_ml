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

CONFIG_PATH = PROJECT_ROOT / "config" / "client_ready_branding.yml"
REPORT_DIR = PROJECT_ROOT / "reports" / "client_ready_branding"
ASSETS_DIR = REPORT_DIR / "assets"
MANIFEST_JSON = REPORT_DIR / "client_ready_manifest.json"
VALIDATION_JSON = REPORT_DIR / "client_ready_validation.json"
DEMO_ASSETS_JSON = REPORT_DIR / "demo_assets.json"
LANDING_HTML = REPORT_DIR / "LANDING_PAGE_CLIENT_DEMO.html"
BRAND_SYSTEM_MD = REPORT_DIR / "BRAND_SYSTEM.md"
READINESS_MD = REPORT_DIR / "PUBLIC_DEMO_READINESS.md"
REPORT_MD = REPORT_DIR / "CLIENT_READY_BRANDING_AND_DEPLOYMENT.md"
SALES_SCRIPT_MD = REPORT_DIR / "EXTERNAL_CLIENT_DEMO_SCRIPT.md"
RAILWAY_CHECKLIST_MD = REPORT_DIR / "RAILWAY_DEPLOYMENT_ENV_CHECKLIST.md"

PRODUCTIZED_MANIFEST = PROJECT_ROOT / "reports" / "productized_os" / "productized_os_manifest.json"
PUBLIC_PAYLOAD = PROJECT_ROOT / "reports" / "public" / "decision_dashboard_payload_public.json"


def now_iso() -> str:
    """
    Yo genero una marca temporal UTC para saber cuándo fue construida la demo cliente.
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_yaml(path: Path) -> dict[str, Any]:
    """
    Yo leo configuración YAML de marca, deployment y demo externa.
    """
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def read_json(path: Path) -> dict[str, Any]:
    """
    Yo leo JSON de manifiestos sin romper el flujo cuando el archivo aún no existe.
    """
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """
    Yo escribo JSON auditable para que la demo tenga trazabilidad técnica.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def rel(path: Path) -> str:
    """
    Yo convierto rutas absolutas en rutas relativas para que el proyecto sea portable.
    """
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def demo_auth_enabled(config: dict[str, Any] | None = None) -> bool:
    """
    Yo determino si la demo externa debe pedir token simple.
    """
    config = config or read_yaml(CONFIG_PATH)
    auth = config.get("auth", {})
    env_flag = auth.get("env_enabled_flag", "MLU_DEMO_AUTH_ENABLED")
    if os.getenv(env_flag, "").strip().lower() in {"1", "true", "yes", "y"}:
        return True
    environment = os.getenv("MLU_ENV", "local").strip().lower()
    return bool(auth.get("require_token_in_production", False) and environment == "production")


def validate_demo_token(token: str | None, config: dict[str, Any] | None = None) -> bool:
    """
    Yo valido un token simple de demo cuando la demo externa está protegida.
    """
    config = config or read_yaml(CONFIG_PATH)
    auth = config.get("auth", {})
    if not demo_auth_enabled(config):
        return True
    env_token_name = auth.get("env_token_name", "MLU_DEMO_TOKEN")
    expected = os.getenv(env_token_name, "").strip()
    if not expected:
        return False
    return bool(token and token.strip() == expected)


def build_brand_css(config: dict[str, Any]) -> str:
    """
    Yo construyo CSS ejecutivo oscuro/dorado desde parámetros de marca.
    """
    palette = config.get("brand", {}).get("palette", {})
    bg = palette.get("background", "#070A12")
    surface = palette.get("surface", "#10182A")
    surface2 = palette.get("surface_2", "#151F35")
    gold = palette.get("gold", "#D6A84F")
    blue = palette.get("blue", "#6EA8FE")
    text = palette.get("text", "#F5F7FB")
    muted = palette.get("muted", "#AAB4C8")
    success = palette.get("success", "#38D39F")
    warning = palette.get("warning", "#FFC857")
    danger = palette.get("danger", "#FF5C7A")
    font = config.get("brand", {}).get("typography", {}).get("body", "Inter, Segoe UI, Arial, sans-serif")
    return f"""
:root {{
  --bg: {bg}; --surface: {surface}; --surface2: {surface2}; --gold: {gold}; --blue: {blue};
  --text: {text}; --muted: {muted}; --success: {success}; --warning: {warning}; --danger: {danger};
}}
* {{ box-sizing: border-box; }}
body {{ margin:0; font-family:{font}; background: radial-gradient(circle at top left, #1a2440 0%, var(--bg) 42%); color:var(--text); }}
a {{ color: var(--blue); text-decoration: none; }}
.hero {{ max-width:1180px; margin:0 auto; padding:72px 24px 36px; }}
.eyebrow {{ color:var(--gold); text-transform:uppercase; letter-spacing:.14em; font-size:12px; font-weight:700; }}
h1 {{ font-size: clamp(38px, 6vw, 74px); line-height:.94; margin:16px 0; letter-spacing:-.05em; }}
p {{ color:var(--muted); font-size:18px; line-height:1.65; }}
.cta-row {{ display:flex; gap:14px; flex-wrap:wrap; margin-top:26px; }}
.btn {{ border:1px solid rgba(214,168,79,.55); padding:13px 18px; border-radius:14px; color:var(--text); background:rgba(214,168,79,.12); font-weight:700; }}
.btn.secondary {{ border-color:rgba(110,168,254,.45); background:rgba(110,168,254,.10); }}
.grid {{ max-width:1180px; margin:24px auto; padding:0 24px 56px; display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:18px; }}
.card {{ background:linear-gradient(180deg, rgba(255,255,255,.055), rgba(255,255,255,.025)); border:1px solid rgba(255,255,255,.10); border-radius:22px; padding:22px; box-shadow: 0 22px 60px rgba(0,0,0,.30); }}
.card h3 {{ margin:0 0 8px; font-size:20px; }}
.metric {{ color:var(--gold); font-size:28px; font-weight:800; }}
.badge {{ display:inline-block; padding:7px 10px; border-radius:999px; background:rgba(56,211,159,.12); color:var(--success); border:1px solid rgba(56,211,159,.25); font-weight:700; font-size:12px; }}
.badge.warning {{ color:var(--warning); background:rgba(255,200,87,.10); border-color:rgba(255,200,87,.25); }}
.footer {{ max-width:1180px; margin:0 auto; padding:24px; color:var(--muted); border-top:1px solid rgba(255,255,255,.08); }}
code {{ background:#050816; padding:2px 6px; border-radius:6px; color:#dbe7ff; }}
""".strip()


def build_brand_assets(config: dict[str, Any]) -> dict[str, Any]:
    """
    Yo genero archivos de marca para que la demo tenga identidad visual consistente.
    """
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    css = build_brand_css(config)
    css_path = ASSETS_DIR / "client_demo_theme.css"
    css_path.write_text(css, encoding="utf-8")

    brand = config.get("brand", {})
    palette = brand.get("palette", {})
    brand_lines = [
        "# Brand System v2.1",
        "",
        f"## Marca",
        f"- Producto: **{config.get('product_name')}**",
        f"- Marca: **{config.get('brand_name')}**",
        f"- Tagline: {config.get('tagline')}",
        "",
        "## Paleta",
    ]
    brand_lines += [f"- `{key}`: `{value}`" for key, value in palette.items()]
    brand_lines += [
        "",
        "## Regla de tono",
        "Ejecutivo, sobrio, consultivo, trazable y comercial. La demo debe hablar de ventas, caja, stock, riesgo y decisión; no de scripts sueltos.",
    ]
    BRAND_SYSTEM_MD.write_text("\n".join(brand_lines), encoding="utf-8")
    return {"css": rel(css_path), "brand_system": rel(BRAND_SYSTEM_MD)}


def _count_payload_kpis() -> dict[str, Any]:
    """
    Yo leo el payload público agregado para mostrar métricas seguras en la landing.
    """
    payload = read_json(PUBLIC_PAYLOAD)
    if not payload:
        return {
            "total_operaciones": "N/D",
            "valor_total_en_riesgo": "N/D",
            "riesgo_promedio": "N/D",
            "p0_p1": "N/D",
            "data_mode": "missing",
        }
    return {
        "total_operaciones": payload.get("total_operaciones", "N/D"),
        "valor_total_en_riesgo": payload.get("valor_total_en_riesgo", "N/D"),
        "riesgo_promedio": payload.get("riesgo_promedio", "N/D"),
        "p0_p1": payload.get("p0_p1", "N/D"),
        "data_mode": payload.get("data_mode", "unknown"),
    }


def build_landing_html(config: dict[str, Any], manifest: dict[str, Any]) -> Path:
    """
    Yo genero una landing externa segura para convertir el producto técnico en demo comercial.
    """
    landing = config.get("landing", {})
    productized = read_json(PRODUCTIZED_MANIFEST)
    modules = productized.get("modules", []) or manifest.get("modules", [])
    selected = set(landing.get("show_modules", []))
    if selected:
        modules = [m for m in modules if m.get("id") in selected] or modules
    kpis = _count_payload_kpis()
    css = build_brand_css(config)
    cards = []
    for module in modules[:6]:
        cards.append(f"""
        <section class='card'>
          <span class='badge'>{html.escape(str(module.get('module_status', 'demo')))}</span>
          <h3>{html.escape(str(module.get('name', module.get('id'))))}</h3>
          <p>{html.escape(str(module.get('commercial_question', 'Producto de decisión comercial.')))}</p>
          <p><code>{html.escape(str(module.get('demo_endpoint', '/demo')))}</code></p>
        </section>
        """)
    routes = landing.get("public_routes", [])
    route_links = "".join([f"<a class='btn secondary' href='{html.escape(route)}'>{html.escape(route)}</a>" for route in routes])
    html_text = f"""
<!doctype html>
<html lang='es'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>{html.escape(str(config.get('product_name')))} · Demo Cliente</title>
<style>{css}</style>
</head>
<body>
  <main class='hero'>
    <div class='eyebrow'>{html.escape(str(config.get('brand_name')))}</div>
    <h1>{html.escape(str(landing.get('hero_title')))}</h1>
    <p>{html.escape(str(landing.get('hero_subtitle')))}</p>
    <div class='cta-row'>
      <a class='btn' href='/public/decision-dashboard'>{html.escape(str(landing.get('primary_cta', 'Ver demo')))}</a>
      <a class='btn secondary' href='/product/demo/package'>{html.escape(str(landing.get('secondary_cta', 'Paquete ejecutivo')))}</a>
    </div>
  </main>
  <section class='grid'>
    <div class='card'><h3>Operaciones evaluadas</h3><div class='metric'>{html.escape(str(kpis.get('total_operaciones')))}</div><p>Payload público agregado. Sin clientes ni documentos.</p></div>
    <div class='card'><h3>Valor en riesgo</h3><div class='metric'>S/ {html.escape(str(kpis.get('valor_total_en_riesgo')))}</div><p>Lectura comercial agregada para priorización ejecutiva.</p></div>
    <div class='card'><h3>Riesgo promedio</h3><div class='metric'>{html.escape(str(kpis.get('riesgo_promedio')))}</div><p>Modo de data: <code>{html.escape(str(kpis.get('data_mode')))}</code></p></div>
    <div class='card'><h3>P0 + P1</h3><div class='metric'>{html.escape(str(kpis.get('p0_p1')))}</div><p>Operaciones que requieren política comercial y SLA.</p></div>
  </section>
  <section class='grid'>
    {''.join(cards)}
  </section>
  <section class='grid'>
    <div class='card' style='grid-column:1/-1'>
      <h3>Rutas de demo</h3>
      <p>Yo muestro solo rutas seguras y agregadas para cliente externo.</p>
      <div class='cta-row'>{route_links}</div>
    </div>
  </section>
  <footer class='footer'>
    {html.escape(str(config.get('tagline')))} · generado {now_iso()}
  </footer>
</body>
</html>
""".strip()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    LANDING_HTML.write_text(html_text, encoding="utf-8")
    return LANDING_HTML


def validate_no_forbidden_public_tokens(paths: list[Path], config: dict[str, Any]) -> list[str]:
    """
    Yo escaneo archivos públicos de demo para impedir tokens sensibles evidentes.
    """
    tokens = [str(x).lower() for x in config.get("quality_gates", {}).get("forbidden_public_tokens", [])]
    hits = []
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for token in tokens:
            # Yo permito palabras en documentación de política solo si no son claves JSON ni parecen datos.
            if re.search(rf'"{re.escape(token)}"\s*:', text):
                hits.append(f"{rel(path)}::{token}")
    return sorted(set(hits))


def build_client_ready_manifest() -> dict[str, Any]:
    """
    Yo consolido la metadata de marca, landing, Railway y demo externa.
    """
    config = read_yaml(CONFIG_PATH)
    brand_assets = build_brand_assets(config)
    productized = read_json(PRODUCTIZED_MANIFEST)
    provisional = {
        "version": config.get("version", "2.1.0"),
        "release_name": config.get("release_name"),
        "product_name": config.get("product_name"),
        "brand_name": config.get("brand_name"),
        "generated_at": now_iso(),
        "productized_os_status": productized.get("release_status", productized.get("manifest", {}).get("release_status", "unknown")),
        "public_payload_exists": PUBLIC_PAYLOAD.exists(),
        "auth_enabled": demo_auth_enabled(config),
        "brand_assets": brand_assets,
        "landing_html": rel(LANDING_HTML),
        "railway_required_variables": config.get("railway", {}).get("required_variables", {}),
        "demo_flow": config.get("demo", {}).get("flow", []),
        "modules": productized.get("modules", []),
    }
    build_landing_html(config, provisional)
    write_json(MANIFEST_JSON, provisional)
    return provisional


def validate_client_ready_deployment() -> dict[str, Any]:
    """
    Yo valido que la demo cliente tenga landing, marca, payload público, política Railway y privacidad mínima.
    """
    config = read_yaml(CONFIG_PATH)
    manifest = build_client_ready_manifest()
    required_paths = [LANDING_HTML, BRAND_SYSTEM_MD, PUBLIC_PAYLOAD, PRODUCTIZED_MANIFEST]
    checks = [{"path": rel(p), "exists": p.exists(), "size_bytes": p.stat().st_size if p.exists() else 0} for p in required_paths]
    errors = []
    warnings = []
    missing = [c["path"] for c in checks if not c["exists"]]
    if missing:
        if config.get("quality_gates", {}).get("require_public_payload", True) and rel(PUBLIC_PAYLOAD) in missing:
            errors.append("Falta payload público CRM agregado para Railway.")
        else:
            warnings.append("Faltan artefactos de demo: " + ", ".join(missing))
    forbidden_hits = validate_no_forbidden_public_tokens([LANDING_HTML, DEMO_ASSETS_JSON], config)
    if forbidden_hits:
        errors.append("Se detectaron tokens prohibidos en assets públicos: " + ", ".join(forbidden_hits))
    auth = config.get("auth", {})
    if os.getenv("MLU_ENV", "local").lower() == "production" and auth.get("require_token_in_production") and not os.getenv(auth.get("env_token_name", "MLU_DEMO_TOKEN")):
        errors.append("Producción exige token de demo, pero no existe MLU_DEMO_TOKEN.")
    validation = {
        "status": "fail" if errors else "warning" if warnings else "ok",
        "generated_at": now_iso(),
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
        "forbidden_hits": forbidden_hits,
        "auth_enabled": demo_auth_enabled(config),
        "manifest_path": rel(MANIFEST_JSON),
    }
    write_json(VALIDATION_JSON, validation)
    return validation


def build_reports() -> dict[str, Any]:
    """
    Yo genero documentos de demo, deployment y guion comercial para cliente externo.
    """
    config = read_yaml(CONFIG_PATH)
    manifest = build_client_ready_manifest()
    validation = validate_client_ready_deployment()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    REPORT_MD.write_text(f"""
# Client Ready Branding & Deployment v2.1

## Promesa
Yo empaqueto el Intelligence OS como demo cliente: landing ejecutiva, marca oscuro/dorado, rutas seguras, token simple opcional y checklist Railway.

## Estado
- Validación: **{validation.get('status')}**
- Producto: **{manifest.get('product_name')}**
- Marca: **{manifest.get('brand_name')}**
- Payload público: **{manifest.get('public_payload_exists')}**
- Auth demo activo: **{manifest.get('auth_enabled')}**

## Rutas clave
- `/demo/client-ready`
- `/demo/landing`
- `/metadata/client-ready`
- `/public/decision-dashboard`
- `/dashboard/productized-os`
- `/product/demo/package`

## Decisión de arquitectura
Lenovo procesa CRM privado. Railway sirve demo pública agregada. GitHub Actions valida privacidad y genera artifacts. Nunca se publica CRM crudo.
""".strip(), encoding="utf-8")

    SALES_SCRIPT_MD.write_text(f"""
# External Client Demo Script v2.1

## Apertura
No voy a mostrarle un dashboard más. Voy a mostrarle una fábrica comercial donde cada señal termina en decisión, responsable y medición.

## Flujo de 12 minutos
1. Abrir `/demo/client-ready` y explicar la promesa.
2. Mostrar `/public/decision-dashboard`: CRM agregado, sin PII.
3. Mostrar `/dashboard/catalog`: productos de decisión.
4. Mostrar `/dashboard/action-feedback`: score → acción → responsable → resultado.
5. Mostrar `/dashboard/experiment-power-policy`: política comercial y capacidad.
6. Cerrar con `/product/demo/package`.

## Cierre comercial
El valor no es predecir. El valor es decidir mejor, actuar antes y medir si la intervención salvó venta, caja o stock.
""".strip(), encoding="utf-8")

    READINESS_MD.write_text(f"""
# Public Demo Readiness

- Estado: **{validation.get('status')}**
- Landing: `{rel(LANDING_HTML)}`
- Payload público: `{rel(PUBLIC_PAYLOAD)}`
- Manifiesto: `{rel(MANIFEST_JSON)}`
- Validación: `{rel(VALIDATION_JSON)}`

## Checks
""".strip() + "\n" + "\n".join([f"- {'✅' if c['exists'] else '❌'} `{c['path']}`" for c in validation.get('checks', [])]), encoding="utf-8")

    railway = config.get("railway", {})
    lines = ["# Railway Deployment Env Checklist", "", "## Variables requeridas"]
    for key, value in railway.get("required_variables", {}).items():
        lines.append(f"- `{key}` = `{value}`")
    lines += ["", "## Start command", f"`{railway.get('recommended_start_command')}`", "", "## Checklist"]
    lines += [f"- [ ] {item}" for item in railway.get("deployment_checklist", [])]
    RAILWAY_CHECKLIST_MD.write_text("\n".join(lines), encoding="utf-8")

    assets = {
        "landing_html": rel(LANDING_HTML),
        "brand_system": rel(BRAND_SYSTEM_MD),
        "client_ready_report": rel(REPORT_MD),
        "demo_script": rel(SALES_SCRIPT_MD),
        "public_demo_readiness": rel(READINESS_MD),
        "railway_checklist": rel(RAILWAY_CHECKLIST_MD),
        "manifest": rel(MANIFEST_JSON),
        "validation": rel(VALIDATION_JSON),
        "routes": ["/demo/client-ready", "/demo/landing", "/metadata/client-ready"],
    }
    write_json(DEMO_ASSETS_JSON, assets)
    # Yo reconstruyo la validación después de crear assets.
    validation = validate_client_ready_deployment()
    return {"manifest": read_json(MANIFEST_JSON), "validation": validation, "assets": read_json(DEMO_ASSETS_JSON)}


def run_client_ready_branding_and_deployment() -> dict[str, Any]:
    """
    Yo ejecuto v2.1 completo: marca, landing, validación Railway y paquete de demo externa.
    """
    return build_reports()


def client_ready_metadata() -> dict[str, Any]:
    """
    Yo devuelvo metadata de v2.1; si no existe, genero los artefactos.
    """
    if not MANIFEST_JSON.exists() or not VALIDATION_JSON.exists() or not LANDING_HTML.exists():
        run_client_ready_branding_and_deployment()
    return {"manifest": read_json(MANIFEST_JSON), "validation": read_json(VALIDATION_JSON), "assets": read_json(DEMO_ASSETS_JSON)}
