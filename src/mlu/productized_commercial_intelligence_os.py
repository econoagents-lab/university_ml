from __future__ import annotations

import html
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.mlu.config import PROJECT_ROOT

CONFIG_PATH = PROJECT_ROOT / "config" / "productized_os.yml"
REPORT_DIR = PROJECT_ROOT / "reports" / "productized_os"
MANIFEST_JSON = REPORT_DIR / "productized_os_manifest.json"
VALIDATION_JSON = REPORT_DIR / "productized_os_validation.json"
OVERVIEW_MD = REPORT_DIR / "PRODUCTIZED_COMMERCIAL_INTELLIGENCE_OS.md"
ONE_PAGER_MD = REPORT_DIR / "CLIENT_DEMO_ONE_PAGER.md"
SALES_SCRIPT_MD = REPORT_DIR / "EXECUTIVE_SALES_SCRIPT.md"
MODULE_CATALOG_MD = REPORT_DIR / "PRODUCT_MODULE_CATALOG.md"
DEPLOYMENT_CHECKLIST_MD = REPORT_DIR / "RAILWAY_PUBLIC_DEMO_CHECKLIST.md"
INDEX_HTML = REPORT_DIR / "productized_os_index.html"
DEMO_PACKAGE_JSON = REPORT_DIR / "sales_demo_package.json"

PUBLIC_PAYLOAD_PATH = PROJECT_ROOT / "reports" / "public" / "decision_dashboard_payload_public.json"


def now_iso() -> str:
    """
    Yo genero una marca temporal UTC para dejar trazabilidad de cada release del producto.
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_yaml(path: Path) -> dict[str, Any]:
    """
    Yo leo configuración YAML y devuelvo un diccionario vacío si el archivo no existe.
    """
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def read_json(path: Path) -> dict[str, Any]:
    """
    Yo leo JSON de forma segura para alimentar manifiestos del producto.
    """
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """
    Yo escribo JSON con indentación para que el equipo pueda auditarlo sin herramientas especiales.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def rel(path: Path) -> str:
    """
    Yo convierto rutas absolutas en rutas relativas al proyecto para que los reportes sean portables.
    """
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def artifact_status(required_artifacts: list[str]) -> dict[str, Any]:
    """
    Yo verifico si los artefactos mínimos de cada módulo existen antes de venderlo como producto activo.
    """
    items = []
    for item in required_artifacts:
        path = PROJECT_ROOT / item
        items.append({"path": item, "exists": path.exists(), "size_bytes": path.stat().st_size if path.exists() else 0})
    existing = sum(1 for item in items if item["exists"])
    total = len(items)
    status = "ok" if total > 0 and existing == total else "warning" if existing > 0 else "missing"
    return {"status": status, "existing": existing, "total": total, "items": items}


def validate_public_payload_privacy(config: dict[str, Any]) -> dict[str, Any]:
    """
    Yo inspecciono el payload público de Railway para confirmar que solo expone agregados seguros.
    """
    forbidden = [str(x).lower() for x in config.get("privacy", {}).get("forbidden_public_fields", [])]
    result: dict[str, Any] = {
        "path": rel(PUBLIC_PAYLOAD_PATH),
        "exists": PUBLIC_PAYLOAD_PATH.exists(),
        "status": "missing",
        "forbidden_hits": [],
        "allowed_top_level_fields": [],
    }
    if not PUBLIC_PAYLOAD_PATH.exists():
        return result

    text = PUBLIC_PAYLOAD_PATH.read_text(encoding="utf-8", errors="ignore")
    payload = read_json(PUBLIC_PAYLOAD_PATH)
    result["allowed_top_level_fields"] = list(payload.keys()) if isinstance(payload, dict) else []

    lowered = text.lower()
    hits = []
    for token in forbidden:
        # Yo busco tokens prohibidos como claves o texto para evitar exponer PII por accidente.
        if re.search(rf'"?{re.escape(token)}"?\s*:', lowered) or token in [str(k).lower() for k in result["allowed_top_level_fields"]]:
            hits.append(token)
    result["forbidden_hits"] = sorted(set(hits))
    result["status"] = "ok" if not hits else "fail"
    return result


def build_module_manifest(config: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Yo convierto la configuración del producto en un manifiesto de módulos vendibles.
    """
    modules = []
    for module in config.get("modules", []):
        artifacts = artifact_status(module.get("required_artifacts", []))
        modules.append({
            "id": module.get("id"),
            "name": module.get("name"),
            "owner": module.get("owner"),
            "commercial_question": module.get("commercial_question"),
            "demo_endpoint": module.get("demo_endpoint"),
            "value_claim": module.get("value_claim"),
            "artifact_status": artifacts,
            "module_status": artifacts["status"],
        })
    return modules


def build_productized_os_manifest() -> dict[str, Any]:
    """
    Yo construyo el manifiesto central de v2.0 para probar que el sistema ya funciona como producto.
    """
    config = read_yaml(CONFIG_PATH)
    modules = build_module_manifest(config)
    privacy = validate_public_payload_privacy(config)
    ok_modules = sum(1 for m in modules if m.get("module_status") == "ok")
    warning_modules = sum(1 for m in modules if m.get("module_status") == "warning")
    missing_modules = sum(1 for m in modules if m.get("module_status") == "missing")
    required_ok = int(config.get("quality_gates", {}).get("min_required_modules_ok", 5))

    release_status = "ok" if ok_modules >= required_ok and privacy.get("status") in {"ok", "missing"} else "warning"
    if privacy.get("status") == "fail":
        release_status = "fail"

    manifest = {
        "version": config.get("version", "2.0.0"),
        "product_name": config.get("product_name", "Productized Commercial Intelligence OS"),
        "positioning": config.get("positioning"),
        "release_mode": config.get("release_mode", "demo_safe"),
        "generated_at": now_iso(),
        "release_status": release_status,
        "module_summary": {
            "total_modules": len(modules),
            "ok_modules": ok_modules,
            "warning_modules": warning_modules,
            "missing_modules": missing_modules,
            "min_required_modules_ok": required_ok,
        },
        "privacy_validation": privacy,
        "modules": modules,
        "recommended_demo_flow": [
            "/production/health",
            "/metadata/productized-os",
            "/public/decision-dashboard",
            "/dashboard/catalog",
            "/dashboard/action-feedback",
            "/dashboard/experiment-power-policy",
            "/product/demo/package",
        ],
    }
    write_json(MANIFEST_JSON, manifest)
    return manifest


def validate_productized_os() -> dict[str, Any]:
    """
    Yo valido que v2.0 tenga mínimos de producto: módulos, privacidad, docs, endpoints y paquete comercial.
    """
    manifest = build_productized_os_manifest()
    required_docs = [
        PROJECT_ROOT / "docs" / "PRODUCTIZED_COMMERCIAL_INTELLIGENCE_OS.md",
        PROJECT_ROOT / "docs" / "SALES_DEMO_PLAYBOOK.md",
        PROJECT_ROOT / "docs" / "DEPLOYMENT_RUNBOOK_V2_0.md",
        PROJECT_ROOT / "docs" / "V2_0_EXECUTIVE_SUMMARY.md",
    ]
    doc_checks = [{"path": rel(p), "exists": p.exists()} for p in required_docs]
    endpoint_checks = [
        {"endpoint": item, "declared": True}
        for item in manifest.get("recommended_demo_flow", [])
    ]
    errors = []
    warnings = []
    if manifest["privacy_validation"].get("status") == "fail":
        errors.append("El payload público contiene campos prohibidos.")
    if manifest["module_summary"].get("ok_modules", 0) < manifest["module_summary"].get("min_required_modules_ok", 5):
        warnings.append("Hay menos módulos OK que el mínimo recomendado para demo comercial fuerte.")
    missing_docs = [x["path"] for x in doc_checks if not x["exists"]]
    if missing_docs:
        warnings.append("Faltan documentos de producto: " + ", ".join(missing_docs))

    validation = {
        "status": "fail" if errors else "warning" if warnings else "ok",
        "generated_at": now_iso(),
        "errors": errors,
        "warnings": warnings,
        "doc_checks": doc_checks,
        "endpoint_checks": endpoint_checks,
        "manifest_path": rel(MANIFEST_JSON),
    }
    write_json(VALIDATION_JSON, validation)
    return validation


def build_markdown_reports(manifest: dict[str, Any], validation: dict[str, Any]) -> None:
    """
    Yo genero reportes ejecutivos y comerciales para que v2.0 pueda presentarse como producto.
    """
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    summary = manifest.get("module_summary", {})

    overview_lines = [
        "# Productized Commercial Intelligence OS v2.0",
        "",
        "## Promesa",
        "Yo convierto CRM, modelos, RAG, dashboards, alertas, feedback y experimentos en un sistema comercial productizado.",
        "",
        "## Estado del release",
        f"- Estado: **{manifest.get('release_status')}**",
        f"- Módulos OK: **{summary.get('ok_modules')} / {summary.get('total_modules')}**",
        f"- Módulos warning: **{summary.get('warning_modules')}**",
        f"- Módulos missing: **{summary.get('missing_modules')}**",
        f"- Privacidad pública: **{manifest.get('privacy_validation', {}).get('status')}**",
        "",
        "## Flujo demo recomendado",
    ]
    overview_lines += [f"1. `{endpoint}`" for endpoint in manifest.get("recommended_demo_flow", [])]
    overview_lines += ["", "## Módulos"]
    for module in manifest.get("modules", []):
        overview_lines += [
            f"### {module.get('name')}",
            f"- Owner: {module.get('owner')}",
            f"- Pregunta: {module.get('commercial_question')}",
            f"- Endpoint demo: `{module.get('demo_endpoint')}`",
            f"- Estado: **{module.get('module_status')}**",
            f"- Valor: {module.get('value_claim')}",
            "",
        ]
    OVERVIEW_MD.write_text("\n".join(overview_lines), encoding="utf-8")

    one_pager = f"""
# One-Pager Comercial · Intelligence OS v2.0

## Qué vendemos
Un sistema operativo de inteligencia comercial inmobiliaria que transforma datos operativos en decisiones: riesgo, stock, pricing, cobranza, RAG, alertas, feedback y experimentación.

## Dolor que resuelve
- Reportes manuales sin trazabilidad.
- Scores que no terminan en acción.
- Dashboards sin responsable ni SLA.
- Datos sensibles que no pueden exponerse en demo.
- Decisiones comerciales sin medición de impacto.

## Demo segura
- Railway muestra solo agregados.
- Lenovo/self-hosted runner procesa CRM privado.
- GitHub Actions genera alertas, artifacts y quality gates.
- API expone endpoints de producto sin PII.

## Estado actual
- Release: **{manifest.get('release_status')}**
- Módulos OK: **{summary.get('ok_modules')} / {summary.get('total_modules')}**
- Privacidad pública: **{manifest.get('privacy_validation', {}).get('status')}**

## Oferta comercial
Diagnóstico + implementación MVP de fábrica comercial: tableros, payload público, API, alertas, RAG y ciclo de feedback.
""".strip()
    ONE_PAGER_MD.write_text(one_pager, encoding="utf-8")

    sales_script = """
# Executive Sales Script · v2.0

## Apertura
No estoy mostrando un dashboard más. Estoy mostrando una fábrica comercial donde cada métrica termina en una decisión, un responsable y una medición del resultado.

## Narrativa de demo
1. Salud del sistema: `/production/health`.
2. Payload público seguro: `/public/decision-dashboard`.
3. Catálogo de dashboards: `/dashboard/catalog`.
4. Cola de acciones: `/dashboard/action-feedback`.
5. Política experimental: `/dashboard/experiment-power-policy`.
6. Paquete comercial: `/product/demo/package`.

## Cierre
El valor no está en predecir. El valor está en priorizar acciones, capturar feedback y demostrar si la intervención salvó ventas, caja o stock.
""".strip()
    SALES_SCRIPT_MD.write_text(sales_script, encoding="utf-8")

    catalog_lines = ["# Product Module Catalog", ""]
    for module in manifest.get("modules", []):
        catalog_lines += [
            f"## {module.get('name')}",
            f"- ID: `{module.get('id')}`",
            f"- Estado: **{module.get('module_status')}**",
            f"- Endpoint: `{module.get('demo_endpoint')}`",
            f"- Pregunta económica: {module.get('commercial_question')}",
            f"- Value claim: {module.get('value_claim')}",
            "",
        ]
    MODULE_CATALOG_MD.write_text("\n".join(catalog_lines), encoding="utf-8")

    checklist = """
# Railway Public Demo Checklist

- [ ] `MLU_ENV=production`.
- [ ] `MLU_DISABLE_SAMPLE_FALLBACK=true`.
- [ ] Existe `reports/public/decision_dashboard_payload_public.json`.
- [ ] El payload público tiene `data_mode=crm`.
- [ ] No contiene clientes, DNI, teléfonos, emails, direcciones ni credenciales.
- [ ] `/public/decision-dashboard` responde sin filas individuales.
- [ ] `/metadata/productized-os` responde con estado del release.
- [ ] GitHub Actions sube artifacts agregados, no CRM crudo.
""".strip()
    DEPLOYMENT_CHECKLIST_MD.write_text(checklist, encoding="utf-8")

    demo_package = {
        "one_pager": rel(ONE_PAGER_MD),
        "sales_script": rel(SALES_SCRIPT_MD),
        "module_catalog": rel(MODULE_CATALOG_MD),
        "deployment_checklist": rel(DEPLOYMENT_CHECKLIST_MD),
        "manifest": rel(MANIFEST_JSON),
        "validation": rel(VALIDATION_JSON),
        "recommended_demo_flow": manifest.get("recommended_demo_flow", []),
    }
    write_json(DEMO_PACKAGE_JSON, demo_package)

    cards = []
    for module in manifest.get("modules", []):
        cards.append(f"""
<div class='card'>
  <h3>{html.escape(str(module.get('name')))}</h3>
  <p><b>Estado:</b> {html.escape(str(module.get('module_status')))}</p>
  <p><b>Pregunta:</b> {html.escape(str(module.get('commercial_question')))}</p>
  <p><b>Endpoint:</b> <code>{html.escape(str(module.get('demo_endpoint')))}</code></p>
  <p>{html.escape(str(module.get('value_claim')))}</p>
</div>
""")
    index = f"""
<!doctype html>
<html lang='es'>
<head>
<meta charset='utf-8'>
<title>Productized Commercial Intelligence OS v2.0</title>
<style>
body {{ font-family: Arial, sans-serif; background:#0b1020; color:#f4f6fb; margin:0; padding:32px; }}
.header {{ max-width:1100px; margin:auto; }}
.grid {{ max-width:1100px; margin:24px auto; display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:16px; }}
.card {{ background:#151d33; border:1px solid #2d3a63; border-radius:14px; padding:18px; box-shadow:0 10px 30px rgba(0,0,0,.25); }}
code {{ background:#050816; padding:2px 6px; border-radius:6px; color:#c8d6ff; }}
.badge {{ display:inline-block; padding:6px 10px; background:#25345f; border-radius:999px; }}
a {{ color:#9cc2ff; }}
</style>
</head>
<body>
<div class='header'>
<h1>Productized Commercial Intelligence OS v2.0</h1>
<p class='badge'>Release status: {html.escape(str(manifest.get('release_status')))}</p>
<p>API + dashboards + RAG + Railway public payload + GitHub alerts + feedback + experiment policy.</p>
<p><b>Módulos OK:</b> {summary.get('ok_modules')} / {summary.get('total_modules')} · <b>Privacidad:</b> {manifest.get('privacy_validation', {}).get('status')}</p>
</div>
<div class='grid'>
{''.join(cards)}
</div>
</body>
</html>
""".strip()
    INDEX_HTML.write_text(index, encoding="utf-8")


def run_productized_os_release() -> dict[str, Any]:
    """
    Yo ejecuto la consolidación v2.0: manifiesto, validación, docs comerciales e índice HTML.
    """
    manifest = build_productized_os_manifest()
    validation = validate_productized_os()
    build_markdown_reports(manifest, validation)
    # Yo reconstruyo el manifiesto al final para que incluya archivos generados por este run.
    manifest = build_productized_os_manifest()
    return {"manifest": manifest, "validation": validation, "report": rel(OVERVIEW_MD), "index_html": rel(INDEX_HTML)}


def productized_os_metadata() -> dict[str, Any]:
    """
    Yo devuelvo metadata del producto; si no existe, genero el release localmente.
    """
    if not MANIFEST_JSON.exists() or not VALIDATION_JSON.exists():
        run_productized_os_release()
    return {"manifest": read_json(MANIFEST_JSON), "validation": read_json(VALIDATION_JSON)}
