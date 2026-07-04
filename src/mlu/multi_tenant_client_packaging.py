from __future__ import annotations

import hashlib
import html
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from src.mlu.config import PROJECT_ROOT

CONFIG_PATH = PROJECT_ROOT / "config" / "client_tenants.yml"
REPORT_DIR = PROJECT_ROOT / "reports" / "client_tenants"
MANIFEST_JSON = REPORT_DIR / "multi_tenant_manifest.json"
VALIDATION_JSON = REPORT_DIR / "multi_tenant_validation.json"
TENANT_INDEX_HTML = REPORT_DIR / "tenant_index.html"
TENANT_INDEX_MD = REPORT_DIR / "TENANT_INDEX.md"
PUBLIC_PAYLOAD_PATH = PROJECT_ROOT / "reports" / "public" / "decision_dashboard_payload_public.json"
PRODUCTIZED_PACKAGE_PATH = PROJECT_ROOT / "reports" / "productized_os" / "sales_demo_package.json"
CLIENT_READY_LANDING = PROJECT_ROOT / "reports" / "client_ready_branding" / "LANDING_PAGE_CLIENT_DEMO.html"


def now_iso() -> str:
    """
    Yo genero una marca temporal UTC para auditar cuándo empaqueté demos por cliente.
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_yaml(path: Path) -> dict[str, Any]:
    """
    Yo leo la configuración multi-tenant sin romper la ejecución cuando aún no existe.
    """
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def read_json(path: Path) -> dict[str, Any]:
    """
    Yo leo un JSON de soporte para empaquetar payloads y manifests comerciales.
    """
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """
    Yo escribo JSON legible para que cada paquete cliente sea auditable.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def rel(path: Path) -> str:
    """
    Yo convierto rutas absolutas a rutas relativas para que el paquete pueda moverse entre laptops y Railway.
    """
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def normalize_tenant_id(tenant_id: str) -> str:
    """
    Yo normalizo el tenant_id para evitar rutas peligrosas o nombres ambiguos.
    """
    clean = re.sub(r"[^a-zA-Z0-9_-]+", "_", str(tenant_id).strip().lower()).strip("_")
    if not clean:
        raise ValueError("tenant_id vacío o inválido")
    return clean


def tenant_dir(tenant_id: str) -> Path:
    """
    Yo centralizo la carpeta de salida de cada cliente.
    """
    return REPORT_DIR / normalize_tenant_id(tenant_id)


def _hash_label(prefix: str, value: Any) -> str:
    """
    Yo anonimizo etiquetas comerciales sensibles con hashes estables y cortos.
    """
    text = str(value or "unknown")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:8].upper()
    return f"{prefix}_{digest}"


def _safe_number(value: Any) -> Any:
    """
    Yo redondeo números para que los payloads públicos sean legibles y consistentes.
    """
    if isinstance(value, float):
        return round(value, 4)
    return value


def load_public_payload() -> dict[str, Any]:
    """
    Yo cargo el payload público agregado de Railway; si no existe, construyo un fallback vacío seguro.
    """
    payload = read_json(PUBLIC_PAYLOAD_PATH)
    if payload:
        return payload
    return {
        "total_operaciones": 0,
        "valor_total_en_riesgo": 0,
        "riesgo_promedio": 0,
        "p0_p1": 0,
        "top_proyectos": [],
        "top_asesores": [],
        "top_canales": [],
        "fecha_generacion": now_iso(),
        "data_mode": "missing_public_payload",
    }


def filter_public_payload_for_tenant(payload: dict[str, Any], tenant: dict[str, Any], defaults: dict[str, Any]) -> dict[str, Any]:
    """
    Yo creo un payload por cliente usando solo campos agregados permitidos.
    """
    allowed = set(defaults.get("allowed_public_payload_fields", []))
    tenant_payload = {key: payload.get(key) for key in allowed if key in payload}
    tenant_payload.setdefault("fecha_generacion", now_iso())
    tenant_payload["data_mode"] = payload.get("data_mode", defaults.get("data_mode", "crm_aggregated"))
    tenant_payload["tenant_id"] = normalize_tenant_id(tenant.get("tenant_id", "tenant"))
    tenant_payload["tenant_segment"] = tenant.get("segment")
    tenant_payload["enabled_modules"] = tenant.get("enabled_modules", [])

    top_n = int(tenant.get("payload_overrides", {}).get("top_n", defaults.get("max_public_top_n", 5)))
    for field in ["top_proyectos", "top_canales"]:
        if isinstance(tenant_payload.get(field), list):
            tenant_payload[field] = tenant_payload[field][:top_n]
    if isinstance(tenant_payload.get("top_asesores"), list):
        tenant_payload["top_asesores"] = [
            {**item, "asesor": _hash_label("Asesor", item.get("asesor", item.get("advisor", idx)))} if isinstance(item, dict) else _hash_label("Asesor", item)
            for idx, item in enumerate(tenant_payload["top_asesores"][:top_n])
        ]
    for key, value in list(tenant_payload.items()):
        tenant_payload[key] = _safe_number(value)
    return tenant_payload


def contains_forbidden_data(payload: Any, forbidden: list[str]) -> list[str]:
    """
    Yo inspecciono un payload serializado para evitar PII, credenciales y columnas crudas.
    """
    text = json.dumps(payload, ensure_ascii=False).lower()
    hits: list[str] = []
    for token in forbidden:
        token_l = str(token).lower()
        if re.search(rf'"{re.escape(token_l)}"\s*:', text):
            hits.append(token_l)
    return sorted(set(hits))


def _theme_palette(theme: str) -> dict[str, str]:
    """
    Yo devuelvo una paleta simple por cliente para diferenciar demos sin reescribir HTML.
    """
    palettes = {
        "dark_gold": {"accent": "#D6A84F", "blue": "#6EA8FE", "bg": "#070A12", "surface": "#10182A"},
        "dark_blue": {"accent": "#6EA8FE", "blue": "#8FD3FF", "bg": "#06101F", "surface": "#0F1E33"},
        "black_platinum": {"accent": "#D8DDE8", "blue": "#A3BFFA", "bg": "#050608", "surface": "#101319"},
    }
    return palettes.get(theme, palettes["dark_gold"])


def build_tenant_landing_html(tenant: dict[str, Any], tenant_payload: dict[str, Any]) -> str:
    """
    Yo genero una landing específica por cliente con narrativa, módulos y rutas habilitadas.
    """
    palette = _theme_palette(str(tenant.get("brand_theme", "dark_gold")))
    modules = tenant.get("enabled_modules", [])
    routes = tenant.get("public_routes", [])
    cards = "".join(
        f"<section class='card'><span>Módulo</span><h3>{html.escape(str(module))}</h3><p>Producto habilitado para esta demo.</p></section>"
        for module in modules
    )
    route_links = "".join(
        f"<a class='btn secondary' href='{html.escape(str(route))}'>{html.escape(str(route))}</a>"
        for route in routes
    )
    kpis = tenant_payload
    return f"""
<!doctype html>
<html lang='es'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>{html.escape(str(tenant.get('display_name')))} · Demo</title>
<style>
:root {{ --bg:{palette['bg']}; --surface:{palette['surface']}; --accent:{palette['accent']}; --blue:{palette['blue']}; --text:#F7F8FC; --muted:#AAB4C8; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:Inter, Segoe UI, Arial, sans-serif; color:var(--text); background:radial-gradient(circle at top left, #1b2540 0, var(--bg) 45%); }}
.hero {{ max-width:1180px; margin:0 auto; padding:72px 24px 32px; }}
.eyebrow {{ color:var(--accent); letter-spacing:.14em; text-transform:uppercase; font-size:12px; font-weight:800; }}
h1 {{ font-size:clamp(36px,6vw,70px); line-height:.95; margin:14px 0; letter-spacing:-.045em; }}
p {{ color:var(--muted); font-size:18px; line-height:1.62; }}
.grid {{ max-width:1180px; margin:20px auto; padding:0 24px 46px; display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:16px; }}
.card {{ background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.025)); border:1px solid rgba(255,255,255,.10); border-radius:22px; padding:22px; box-shadow:0 18px 50px rgba(0,0,0,.30); }}
.card span {{ color:var(--accent); font-size:12px; text-transform:uppercase; letter-spacing:.12em; font-weight:800; }}
.metric {{ font-size:30px; color:var(--accent); font-weight:900; }}
.btn {{ display:inline-block; margin:6px 8px 6px 0; padding:12px 15px; border-radius:14px; color:var(--text); border:1px solid rgba(255,255,255,.18); text-decoration:none; background:rgba(255,255,255,.06); }}
.secondary {{ border-color:rgba(110,168,254,.32); }}
code {{ background:#050816; color:#DFE8FF; border-radius:7px; padding:2px 6px; }}
.footer {{ max-width:1180px; margin:0 auto; padding:26px 24px; border-top:1px solid rgba(255,255,255,.08); color:var(--muted); }}
</style>
</head>
<body>
  <main class='hero'>
    <div class='eyebrow'>{html.escape(str(tenant.get('display_name')))}</div>
    <h1>{html.escape(str(tenant.get('landing_title')))}</h1>
    <p>{html.escape(str(tenant.get('landing_subtitle')))}</p>
    <p><strong>Foco comercial:</strong> {html.escape(str(tenant.get('commercial_focus')))}</p>
    <a class='btn' href='/product/client/{html.escape(str(tenant.get('tenant_id')))}/package'>{html.escape(str(tenant.get('primary_cta', 'Ver paquete')))}</a>
  </main>
  <section class='grid'>
    <div class='card'><span>KPI</span><h3>Operaciones</h3><div class='metric'>{html.escape(str(kpis.get('total_operaciones', 0)))}</div><p>Agregado seguro por cliente.</p></div>
    <div class='card'><span>KPI</span><h3>Valor en riesgo</h3><div class='metric'>S/ {html.escape(str(kpis.get('valor_total_en_riesgo', 0)))}</div><p>Sin operaciones individuales ni clientes.</p></div>
    <div class='card'><span>KPI</span><h3>Riesgo promedio</h3><div class='metric'>{html.escape(str(kpis.get('riesgo_promedio', 0)))}</div><p>Payload modo <code>{html.escape(str(kpis.get('data_mode')))}</code>.</p></div>
    <div class='card'><span>KPI</span><h3>P0 + P1</h3><div class='metric'>{html.escape(str(kpis.get('p0_p1', 0)))}</div><p>Cola ejecutiva agregada.</p></div>
  </section>
  <section class='grid'>{cards}</section>
  <section class='grid'><div class='card' style='grid-column:1/-1'><span>Rutas</span><h3>Demo habilitada</h3><p>Yo expongo solo rutas seguras para este cliente.</p>{route_links}</div></section>
  <footer class='footer'>Commercial Intelligence OS · Tenant <code>{html.escape(str(tenant.get('tenant_id')))}</code> · generado {now_iso()}</footer>
</body>
</html>
""".strip()


def build_tenant_package(tenant: dict[str, Any], defaults: dict[str, Any], source_payload: dict[str, Any]) -> dict[str, Any]:
    """
    Yo genero landing, one-pager, payload y manifiesto para un cliente específico.
    """
    tenant_id = normalize_tenant_id(tenant.get("tenant_id", "tenant"))
    out_dir = tenant_dir(tenant_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = filter_public_payload_for_tenant(source_payload, tenant, defaults)
    forbidden = defaults.get("forbidden_public_fields", [])
    forbidden_hits = contains_forbidden_data(payload, forbidden)

    payload_path = out_dir / "public_payload.json"
    landing_path = out_dir / "landing.html"
    one_pager_path = out_dir / "one_pager.md"
    package_path = out_dir / "client_demo_package.json"

    write_json(payload_path, payload)
    landing_path.write_text(build_tenant_landing_html(tenant, payload), encoding="utf-8")
    one_pager = [
        f"# {tenant.get('display_name')}",
        "",
        f"**Segmento:** {tenant.get('segment')}",
        f"**Foco comercial:** {tenant.get('commercial_focus')}",
        f"**Token env var:** `{tenant.get('token_env_var')}`",
        "",
        "## Módulos habilitados",
        *[f"- `{module}`" for module in tenant.get("enabled_modules", [])],
        "",
        "## Rutas de demo",
        *[f"- `{route}`" for route in tenant.get("public_routes", [])],
        "",
        "## Política de datos",
        "Solo payload agregado CRM. No clientes, DNI, teléfonos, emails, direcciones, códigos crudos ni credenciales.",
    ]
    one_pager_path.write_text("\n".join(one_pager), encoding="utf-8")

    package = {
        "tenant_id": tenant_id,
        "display_name": tenant.get("display_name"),
        "segment": tenant.get("segment"),
        "generated_at": now_iso(),
        "token_env_var": tenant.get("token_env_var"),
        "enabled_modules": tenant.get("enabled_modules", []),
        "public_routes": tenant.get("public_routes", []),
        "artifact_paths": {
            "payload": rel(payload_path),
            "landing": rel(landing_path),
            "one_pager": rel(one_pager_path),
        },
        "privacy_status": "ok" if not forbidden_hits else "fail",
        "forbidden_hits": forbidden_hits,
        "data_mode": payload.get("data_mode"),
    }
    write_json(package_path, package)
    return package


def build_all_tenant_packages() -> dict[str, Any]:
    """
    Yo construyo todos los paquetes cliente desde una configuración multi-tenant.
    """
    config = read_yaml(CONFIG_PATH)
    defaults = config.get("defaults", {})
    tenants = config.get("tenants", [])
    source_payload = load_public_payload()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    packages = [build_tenant_package(tenant, defaults, source_payload) for tenant in tenants]
    ok_count = sum(1 for p in packages if p.get("privacy_status") == "ok")
    manifest = {
        "version": config.get("version", "2.2.0"),
        "product_name": config.get("product_name", "Commercial Intelligence OS"),
        "packaging_mode": config.get("packaging_mode", "multi_tenant_demo_safe"),
        "generated_at": now_iso(),
        "tenant_count": len(packages),
        "privacy_ok_count": ok_count,
        "status": "ok" if packages and ok_count == len(packages) else "fail",
        "tenants": packages,
    }
    write_json(MANIFEST_JSON, manifest)
    build_tenant_index(manifest)
    validate_multi_tenant_packaging()
    return manifest


def build_tenant_index(manifest: dict[str, Any] | None = None) -> Path:
    """
    Yo genero un índice maestro para abrir todas las demos cliente desde una sola puerta.
    """
    manifest = manifest or read_json(MANIFEST_JSON)
    rows = []
    md = ["# Multi-Tenant Client Packaging", "", "| Tenant | Segmento | Estado | Landing | One-pager |", "|---|---|---|---|---|"]
    for tenant in manifest.get("tenants", []):
        artifacts = tenant.get("artifact_paths", {})
        rows.append(f"""
        <tr>
          <td><strong>{html.escape(str(tenant.get('display_name')))}</strong><br><code>{html.escape(str(tenant.get('tenant_id')))}</code></td>
          <td>{html.escape(str(tenant.get('segment')))}</td>
          <td>{html.escape(str(tenant.get('privacy_status')))}</td>
          <td><a href='/{html.escape(str(artifacts.get('landing', '')))}'>landing</a></td>
          <td><code>{html.escape(str(artifacts.get('one_pager', '')))}</code></td>
        </tr>
        """)
        md.append(f"| {tenant.get('tenant_id')} | {tenant.get('segment')} | {tenant.get('privacy_status')} | `{artifacts.get('landing')}` | `{artifacts.get('one_pager')}` |")
    html_text = f"""
<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Multi-Tenant Client Packaging</title>
<style>body{{font-family:Inter,Segoe UI,Arial,sans-serif;background:#070A12;color:#F6F7FB;margin:0;padding:36px}} table{{width:100%;border-collapse:collapse;background:#10182A;border-radius:18px;overflow:hidden}} td,th{{padding:14px;border-bottom:1px solid rgba(255,255,255,.08);text-align:left}} a{{color:#6EA8FE}} code{{color:#D6A84F}}</style>
</head><body><h1>Commercial Intelligence OS · Client Packages</h1><p>Yo empaqueto demos separadas por cliente con payloads agregados y política anti-PII.</p><table><thead><tr><th>Tenant</th><th>Segmento</th><th>Privacidad</th><th>Landing</th><th>One-pager</th></tr></thead><tbody>{''.join(rows)}</tbody></table></body></html>
""".strip()
    TENANT_INDEX_HTML.write_text(html_text, encoding="utf-8")
    TENANT_INDEX_MD.write_text("\n".join(md), encoding="utf-8")
    return TENANT_INDEX_HTML


def validate_multi_tenant_packaging() -> dict[str, Any]:
    """
    Yo valido que cada tenant tenga landing, payload, one-pager, token env var y cero PII.
    """
    config = read_yaml(CONFIG_PATH)
    manifest = read_json(MANIFEST_JSON)
    errors: list[str] = []
    warnings: list[str] = []
    if not manifest.get("tenants"):
        errors.append("No hay tenants empaquetados.")
    for tenant in manifest.get("tenants", []):
        artifacts = tenant.get("artifact_paths", {})
        for label, rel_path in artifacts.items():
            if not rel_path or not (PROJECT_ROOT / rel_path).exists():
                errors.append(f"Falta artifact {label} para tenant {tenant.get('tenant_id')}: {rel_path}")
        if tenant.get("privacy_status") != "ok":
            errors.append(f"Tenant {tenant.get('tenant_id')} tiene hits prohibidos: {tenant.get('forbidden_hits')}")
        if not tenant.get("token_env_var"):
            warnings.append(f"Tenant {tenant.get('tenant_id')} no declara token_env_var.")
    required = [TENANT_INDEX_HTML, TENANT_INDEX_MD, MANIFEST_JSON]
    for path in required:
        if not path.exists():
            errors.append(f"Falta archivo requerido: {rel(path)}")
    validation = {
        "status": "fail" if errors else "warning" if warnings else "ok",
        "generated_at": now_iso(),
        "errors": errors,
        "warnings": warnings,
        "tenant_count": manifest.get("tenant_count", 0),
        "privacy_ok_count": manifest.get("privacy_ok_count", 0),
        "config_path": rel(CONFIG_PATH),
        "manifest_path": rel(MANIFEST_JSON),
    }
    write_json(VALIDATION_JSON, validation)
    return validation


def client_tenant_metadata() -> dict[str, Any]:
    """
    Yo expongo metadata segura de paquetes cliente para API y demo externa.
    """
    if not MANIFEST_JSON.exists():
        build_all_tenant_packages()
    manifest = read_json(MANIFEST_JSON)
    validation = read_json(VALIDATION_JSON)
    return {
        "version": manifest.get("version"),
        "status": manifest.get("status"),
        "tenant_count": manifest.get("tenant_count"),
        "privacy_ok_count": manifest.get("privacy_ok_count"),
        "validation_status": validation.get("status"),
        "tenant_ids": [t.get("tenant_id") for t in manifest.get("tenants", [])],
        "manifest_path": rel(MANIFEST_JSON),
        "index_html": rel(TENANT_INDEX_HTML),
    }


def get_tenant_package(tenant_id: str) -> dict[str, Any]:
    """
    Yo recupero el paquete de un cliente específico por tenant_id.
    """
    if not MANIFEST_JSON.exists():
        build_all_tenant_packages()
    tenant_id = normalize_tenant_id(tenant_id)
    package_path = tenant_dir(tenant_id) / "client_demo_package.json"
    if not package_path.exists():
        raise FileNotFoundError(f"No existe paquete para tenant: {tenant_id}")
    return read_json(package_path)


def validate_tenant_token(tenant_id: str, token: str | None) -> bool:
    """
    Yo valido un token por cliente usando la variable de entorno declarada para ese tenant.
    """
    config = read_yaml(CONFIG_PATH)
    tenant_id = normalize_tenant_id(tenant_id)
    tenant = next((t for t in config.get("tenants", []) if normalize_tenant_id(t.get("tenant_id", "")) == tenant_id), None)
    if tenant is None:
        return False
    require_token = bool(config.get("defaults", {}).get("require_token", True))
    if os.getenv("MLU_ENV", "local").lower() != "production" and os.getenv("MLU_FORCE_TENANT_TOKEN", "").lower() not in {"1", "true", "yes"}:
        return True
    if not require_token:
        return True
    expected = os.getenv(str(tenant.get("token_env_var", "")), "").strip()
    if not expected:
        return False
    return bool(token and token.strip() == expected)


def run_multi_tenant_client_packaging() -> dict[str, Any]:
    """
    Yo ejecuto toda la fábrica de empaquetado cliente: payload, landing, one-pager, manifest y validación.
    """
    return build_all_tenant_packages()


if __name__ == "__main__":
    run_multi_tenant_client_packaging()
