from __future__ import annotations

import html
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.mlu.config import PROJECT_ROOT
from src.mlu.dashboard_control import load_dashboard_catalog, load_dashboard_params, parse_param_ref, load_yaml

GENERATED_DIR = PROJECT_ROOT / "reports" / "generated_dashboards"
MANIFEST_PATH = GENERATED_DIR / "dashboard_generation_manifest.json"
INDEX_MD_PATH = GENERATED_DIR / "DASHBOARD_INDEX.md"
INDEX_HTML_PATH = GENERATED_DIR / "index.html"
GENERATION_CONFIG_PATH = PROJECT_ROOT / "config" / "dashboard_generation.yml"
PUBLIC_PAYLOAD_PATH = PROJECT_ROOT / "reports" / "public" / "decision_dashboard_payload_public.json"
DASHBOARD_PAYLOAD_PATH = PROJECT_ROOT / "reports" / "dashboard" / "decision_dashboard_payload.json"
RANKING_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "scoring" / "ranking_operaciones_riesgo_caida.csv"
RAGAS_SUMMARY_PATH = PROJECT_ROOT / "reports" / "uni_final" / "RAGAS_LIKE_SUMMARY.md"
FINAL_TECHNICAL_REPORT_PATH = PROJECT_ROOT / "reports" / "uni_final" / "FINAL_TECHNICAL_REPORT.md"

SENSITIVE_TERMS = {
    "cliente",
    "documento",
    "dni",
    "email",
    "correo",
    "telefono",
    "teléfono",
    "nombre completo",
    "direccion",
    "dirección",
    "credencial",
    "password",
    "secret",
    "token",
}


@dataclass(frozen=True)
class GeneratedDashboard:
    id: str
    name: str
    family: str
    priority: str
    markdown_path: str
    html_path: str
    json_path: str
    params_ref: str
    status: str


def load_generation_config(path: Path = GENERATION_CONFIG_PATH) -> dict[str, Any]:
    """
    Yo cargo las reglas de generación automática para que el catálogo produzca tableros sin tocar código.
    """
    if path.exists():
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {
        "project": "machine_learning_university",
        "version": "v1.4_dashboard_generator_from_catalog",
        "generate_markdown": True,
        "generate_html": True,
        "generate_json": True,
        "safe_aggregate_only": True,
        "max_top_items": 5,
    }


def family_from_output_path(output_path: str) -> str:
    """
    Yo infiero la familia del dashboard desde su ruta de salida para agrupar el catálogo automáticamente.
    """
    parts = Path(output_path).parts
    if "dashboard" in parts:
        idx = parts.index("dashboard")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    if len(parts) >= 2:
        return parts[-2]
    return "general"


def read_json_if_exists(path: Path) -> dict[str, Any]:
    """
    Yo leo JSON si existe; si no existe devuelvo un diccionario vacío para mantener el generador tolerante.
    """
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """
    Yo busco columnas por nombres alternativos porque mis outputs evolucionan por versiones.
    """
    normalized = {str(col).lower().strip(): col for col in df.columns}
    for candidate in candidates:
        key = candidate.lower().strip()
        if key in normalized:
            return normalized[key]
    return None


def load_ranking_dataframe() -> pd.DataFrame:
    """
    Yo cargo la cola de riesgo solo para agregados; nunca exporto filas individuales al dashboard generado.
    """
    if not RANKING_CSV_PATH.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(RANKING_CSV_PATH)
    except Exception:
        return pd.DataFrame()


def safe_number(value: Any, default: float = 0.0) -> float:
    """
    Yo convierto valores de KPIs a número para evitar que un tipo inesperado rompa el reporte.
    """
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def aggregate_dimension(df: pd.DataFrame, dimension_candidates: list[str], value_candidates: list[str], top_n: int) -> list[dict[str, Any]]:
    """
    Yo calculo rankings agregados por proyecto, asesor o canal sin exponer operaciones individuales.
    """
    if df.empty:
        return []
    dim = find_column(df, dimension_candidates)
    if not dim:
        return []
    value = find_column(df, value_candidates)
    work = df.copy()
    if value:
        work[value] = pd.to_numeric(work[value], errors="coerce").fillna(0)
        agg = work.groupby(dim, dropna=False).agg(operaciones=(dim, "size"), valor_en_riesgo=(value, "sum")).reset_index()
        agg = agg.sort_values(["valor_en_riesgo", "operaciones"], ascending=False)
    else:
        agg = work.groupby(dim, dropna=False).size().reset_index(name="operaciones")
        agg["valor_en_riesgo"] = 0.0
        agg = agg.sort_values("operaciones", ascending=False)
    agg = agg.head(top_n).rename(columns={dim: "dimension"})
    return agg.to_dict(orient="records")


def build_global_kpis(df: pd.DataFrame, public_payload: dict[str, Any], top_n: int) -> dict[str, Any]:
    """
    Yo construyo KPIs globales agregados para que todos los dashboards tengan una base común de lectura.
    """
    if public_payload:
        return {
            "total_operaciones": public_payload.get("total_operaciones", 0),
            "valor_total_en_riesgo": public_payload.get("valor_total_en_riesgo", 0),
            "riesgo_promedio": public_payload.get("riesgo_promedio", 0),
            "p0_p1": public_payload.get("p0_p1", 0),
            "top_proyectos": public_payload.get("top_proyectos", []),
            "top_asesores": public_payload.get("top_asesores", []),
            "top_canales": public_payload.get("top_canales", []),
            "data_mode": public_payload.get("data_mode", "crm"),
            "fecha_generacion": public_payload.get("fecha_generacion"),
        }

    if df.empty:
        return {
            "total_operaciones": 0,
            "valor_total_en_riesgo": 0,
            "riesgo_promedio": 0,
            "p0_p1": 0,
            "top_proyectos": [],
            "top_asesores": [],
            "top_canales": [],
            "data_mode": "unknown",
            "fecha_generacion": datetime.now().isoformat(timespec="seconds"),
        }

    risk_col = find_column(df, ["riesgo_caida", "riesgo", "risk_score", "probabilidad_caida", "score_riesgo"])
    value_col = find_column(df, ["valor_esperado_en_riesgo", "expected_value_at_risk", "valor_riesgo"])
    priority_col = find_column(df, ["prioridad_operativa", "prioridad", "priority", "nivel_prioridad"])

    riesgo_promedio = safe_number(pd.to_numeric(df[risk_col], errors="coerce").mean() if risk_col else 0)
    valor_total = safe_number(pd.to_numeric(df[value_col], errors="coerce").sum() if value_col else 0)
    p0_p1 = 0
    if priority_col:
        normalized_priority = df[priority_col].fillna("").astype(str).str.upper()
        p0_p1 = int(normalized_priority.str.contains("P0|P1", regex=True).sum())

    return {
        "total_operaciones": int(len(df)),
        "valor_total_en_riesgo": valor_total,
        "riesgo_promedio": riesgo_promedio,
        "p0_p1": p0_p1,
        "top_proyectos": aggregate_dimension(df, ["proyecto", "project"], ["valor_esperado_en_riesgo", "expected_value_at_risk", "valor_riesgo"], top_n),
        "top_asesores": aggregate_dimension(df, ["asesor", "advisor"], ["valor_esperado_en_riesgo", "expected_value_at_risk", "valor_riesgo"], top_n),
        "top_canales": aggregate_dimension(df, ["canal_agrupado", "canal", "medio_captacion", "channel"], ["valor_esperado_en_riesgo", "expected_value_at_risk", "valor_riesgo"], top_n),
        "data_mode": "crm",
        "fecha_generacion": datetime.now().isoformat(timespec="seconds"),
    }


def load_param_snapshot(params_ref: str) -> dict[str, Any]:
    """
    Yo extraigo el bloque de parámetros asociado a un dashboard para mostrar dónde cambiar su comportamiento.
    """
    path, section = parse_param_ref(params_ref)
    if path is None or not path.exists():
        return {"status": "params_ref_not_found", "params_ref": params_ref}
    if path.suffix in {".yml", ".yaml"}:
        data = load_yaml(path)
    elif path.suffix == ".json":
        data = read_json_if_exists(path)
    else:
        return {"status": "unsupported_param_file", "params_ref": params_ref}
    if section:
        return data.get(section, {"status": "section_not_found", "section": section})
    return data


def action_recommendation(dashboard: dict[str, Any], family: str) -> str:
    """
    Yo traduzco cada dashboard en una acción ejecutiva inicial para que el tablero no sea decorativo.
    """
    text = " ".join([str(dashboard.get("id", "")), str(dashboard.get("name", "")), family]).lower()
    if "riesgo" in text or "caida" in text or "caída" in text or "tuberia" in text or "tubería" in text:
        return "Revisar operaciones P0/P1, asignar responsable y registrar feedback de intervención."
    if "funnel" in text or "conversion" in text or "conversión" in text or "lead" in text:
        return "Comparar conversión por etapa, canal y asesor; priorizar los cuellos de botella con mayor valor comercial."
    if "stock" in text or "pricing" in text or "precio" in text or "absorcion" in text or "absorción" in text:
        return "Cruzar inventario, precio m² y velocidad de venta para ajustar campaña, descuento o mix de producto."
    if "cobranza" in text or "caja" in text or "pago" in text:
        return "Priorizar saldos pendientes y pagos no asignados para proteger caja y trazabilidad financiera."
    if "rag" in text or "uni" in text or "congreso" in text:
        return "Validar citas, guardrails y métricas de evaluación antes de presentar o publicar el asistente."
    if "railway" in text or "privacy" in text or "pii" in text:
        return "Servir solo agregados públicos; bloquear sample fallback y cualquier campo sensible."
    if "mlops" in text or "drift" in text or "registry" in text or "lift" in text:
        return "Revisar estado del champion, drift, lift y política de retraining antes de confiar en el ranking."
    return "Usar el tablero para convertir datos en decisión, responsable, plazo y métrica de resultado."


def dashboard_payload(dashboard: dict[str, Any], global_kpis: dict[str, Any], params_snapshot: dict[str, Any]) -> dict[str, Any]:
    """
    Yo construyo el payload semántico del dashboard desde catálogo, KPIs y parámetros.
    """
    family = family_from_output_path(str(dashboard.get("output_path", "")))
    return {
        "id": dashboard.get("id"),
        "number": dashboard.get("number"),
        "name": dashboard.get("name"),
        "family": family,
        "owner": dashboard.get("owner"),
        "audience": dashboard.get("audience"),
        "economic_question": dashboard.get("economic_question"),
        "priority": dashboard.get("priority", "cataloged"),
        "status": dashboard.get("status", "cataloged"),
        "output_path_declared": dashboard.get("output_path"),
        "params_ref": dashboard.get("params_ref"),
        "where_to_change": dashboard.get("params_ref"),
        "params_snapshot": params_snapshot,
        "global_kpis": global_kpis,
        "recommended_action": action_recommendation(dashboard, family),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


def markdown_table(rows: list[dict[str, Any]], max_rows: int = 5) -> str:
    """
    Yo convierto rankings agregados en tablas Markdown sin exponer filas individuales.
    """
    if not rows:
        return "_Sin datos agregados disponibles._"
    normalized = rows[:max_rows]
    headers = list(normalized[0].keys())
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in normalized:
        lines.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
    return "\n".join(lines)


def render_markdown(payload: dict[str, Any]) -> str:
    """
    Yo renderizo un dashboard Markdown que combina pregunta económica, KPIs, parámetros y acción.
    """
    kpis = payload["global_kpis"]
    params_text = yaml.safe_dump(payload.get("params_snapshot", {}), allow_unicode=True, sort_keys=False)[:3000]
    return f"""# {payload['name']}

**Familia:** `{payload['family']}`  
**Owner:** {payload['owner']}  
**Audiencia:** {payload['audience']}  
**Prioridad:** {payload['priority']}  
**Estado:** {payload['status']}

## Pregunta económica

{payload['economic_question']}

## KPIs agregados disponibles

- Total operaciones: **{kpis.get('total_operaciones', 0):,}**
- Valor total en riesgo: **S/ {safe_number(kpis.get('valor_total_en_riesgo')):,.2f}**
- Riesgo promedio: **{safe_number(kpis.get('riesgo_promedio')):.3f}**
- Operaciones P0/P1: **{kpis.get('p0_p1', 0)}**
- Data mode: **{kpis.get('data_mode', 'unknown')}**
- Fecha generación KPI: **{kpis.get('fecha_generacion', 'n/d')}**

## Top proyectos agregados

{markdown_table(kpis.get('top_proyectos', []))}

## Top asesores agregados

{markdown_table(kpis.get('top_asesores', []))}

## Top canales agregados

{markdown_table(kpis.get('top_canales', []))}

## Acción recomendada

{payload['recommended_action']}

## Donde cambiar

`{payload['where_to_change']}`

## Parámetros actuales usados como contexto

```yaml
{params_text}
```

## Regla de gobierno

Yo genero este dashboard desde `config/dashboard_catalog.yml` y sus parámetros asociados. Si cambia la decisión económica, cambio configuración; no reescribo el tablero a mano.
"""


def html_table(rows: list[dict[str, Any]], max_rows: int = 5) -> str:
    """
    Yo construyo tablas HTML desde agregados seguros.
    """
    if not rows:
        return "<p><em>Sin datos agregados disponibles.</em></p>"
    rows = rows[:max_rows]
    headers = list(rows[0].keys())
    head = "".join(f"<th>{html.escape(str(h))}</th>" for h in headers)
    body = []
    for row in rows:
        body.append("<tr>" + "".join(f"<td>{html.escape(str(row.get(h, '')))}</td>" for h in headers) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def render_html(payload: dict[str, Any]) -> str:
    """
    Yo renderizo un dashboard HTML simple y portable para abrirlo localmente o publicarlo como artifact.
    """
    kpis = payload["global_kpis"]
    params_text = html.escape(yaml.safe_dump(payload.get("params_snapshot", {}), allow_unicode=True, sort_keys=False)[:3000])
    return f"""<!doctype html>
<html lang=\"es\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{html.escape(str(payload['name']))}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; background: #f7f8fb; color: #0b2538; }}
    .card {{ background: white; border: 1px solid #d9e0e8; border-radius: 14px; padding: 20px; margin: 16px 0; box-shadow: 0 2px 8px rgba(0,0,0,.04); }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }}
    .kpi {{ background: #0b2538; color: white; border-radius: 12px; padding: 16px; }}
    .kpi small {{ color: #bed2df; }}
    table {{ border-collapse: collapse; width: 100%; background: white; }}
    th, td {{ border: 1px solid #d9e0e8; padding: 8px; text-align: left; }}
    th {{ background: #123f63; color: white; }}
    code, pre {{ background: #eef3f7; padding: 8px; border-radius: 8px; overflow:auto; }}
    a {{ color: #0a66c2; }}
  </style>
</head>
<body>
  <h1>{html.escape(str(payload['name']))}</h1>
  <p><strong>Familia:</strong> {html.escape(str(payload['family']))} · <strong>Owner:</strong> {html.escape(str(payload['owner']))} · <strong>Prioridad:</strong> {html.escape(str(payload['priority']))}</p>
  <div class=\"card\"><h2>Pregunta económica</h2><p>{html.escape(str(payload['economic_question']))}</p></div>
  <div class=\"grid\">
    <div class=\"kpi\"><small>Total operaciones</small><h2>{int(kpis.get('total_operaciones', 0)):,}</h2></div>
    <div class=\"kpi\"><small>Valor total en riesgo</small><h2>S/ {safe_number(kpis.get('valor_total_en_riesgo')):,.2f}</h2></div>
    <div class=\"kpi\"><small>Riesgo promedio</small><h2>{safe_number(kpis.get('riesgo_promedio')):.3f}</h2></div>
    <div class=\"kpi\"><small>P0/P1</small><h2>{kpis.get('p0_p1', 0)}</h2></div>
  </div>
  <div class=\"card\"><h2>Acción recomendada</h2><p>{html.escape(str(payload['recommended_action']))}</p></div>
  <div class=\"card\"><h2>Top proyectos agregados</h2>{html_table(kpis.get('top_proyectos', []))}</div>
  <div class=\"card\"><h2>Top asesores agregados</h2>{html_table(kpis.get('top_asesores', []))}</div>
  <div class=\"card\"><h2>Top canales agregados</h2>{html_table(kpis.get('top_canales', []))}</div>
  <div class=\"card\"><h2>Donde cambiar</h2><p><code>{html.escape(str(payload['where_to_change']))}</code></p></div>
  <div class=\"card\"><h2>Parámetros actuales</h2><pre>{params_text}</pre></div>
  <p><a href=\"../index.html\">Volver al índice</a></p>
</body>
</html>"""


def write_dashboard_artifacts(payload: dict[str, Any]) -> GeneratedDashboard:
    """
    Yo escribo Markdown, HTML y JSON por dashboard para reutilizarlo en GitHub, Railway o demo local.
    """
    family = str(payload["family"])
    dashboard_id = str(payload["id"])
    out_dir = GENERATED_DIR / family
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / f"{dashboard_id}.md"
    html_path = out_dir / f"{dashboard_id}.html"
    json_path = out_dir / f"{dashboard_id}.json"
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    html_path.write_text(render_html(payload), encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return GeneratedDashboard(
        id=dashboard_id,
        name=str(payload["name"]),
        family=family,
        priority=str(payload["priority"]),
        markdown_path=str(md_path.relative_to(PROJECT_ROOT)),
        html_path=str(html_path.relative_to(PROJECT_ROOT)),
        json_path=str(json_path.relative_to(PROJECT_ROOT)),
        params_ref=str(payload["params_ref"]),
        status="generated",
    )


def generate_dashboards_from_catalog() -> dict[str, Any]:
    """
    Yo convierto el catálogo de dashboards en artefactos reales Markdown/HTML/JSON.
    """
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    config = load_generation_config()
    catalog = load_dashboard_catalog()
    public_payload = read_json_if_exists(PUBLIC_PAYLOAD_PATH)
    df = load_ranking_dataframe()
    top_n = int(config.get("max_top_items", 5))
    global_kpis = build_global_kpis(df, public_payload, top_n=top_n)

    generated: list[GeneratedDashboard] = []
    for dashboard in catalog.get("dashboards", []):
        params_snapshot = load_param_snapshot(str(dashboard.get("params_ref", "")))
        payload = dashboard_payload(dashboard, global_kpis=global_kpis, params_snapshot=params_snapshot)
        generated.append(write_dashboard_artifacts(payload))

    manifest = {
        "project": catalog.get("project"),
        "version": "v1.4_dashboard_generator_from_catalog",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_generated": len(generated),
        "families": sorted({item.family for item in generated}),
        "safe_aggregate_only": True,
        "source_paths": {
            "catalog": str((PROJECT_ROOT / "config" / "dashboard_catalog.yml").relative_to(PROJECT_ROOT)),
            "params": str((PROJECT_ROOT / "config" / "dashboard_params.yml").relative_to(PROJECT_ROOT)),
            "public_payload": str(PUBLIC_PAYLOAD_PATH.relative_to(PROJECT_ROOT)),
            "ranking_csv": str(RANKING_CSV_PATH.relative_to(PROJECT_ROOT)),
        },
        "dashboards": [item.__dict__ for item in generated],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    generate_dashboard_index(manifest)
    generate_family_indexes(manifest)
    return manifest


def generate_dashboard_index(manifest: dict[str, Any] | None = None) -> tuple[Path, Path]:
    """
    Yo genero el índice maestro para navegar todos los dashboards creados desde el catálogo.
    """
    if manifest is None:
        manifest = read_json_if_exists(MANIFEST_PATH)
    dashboards = manifest.get("dashboards", [])
    by_family: dict[str, list[dict[str, Any]]] = {}
    for item in dashboards:
        by_family.setdefault(item["family"], []).append(item)

    lines = [
        "# Dashboard Generator From Catalog",
        "",
        f"**Versión:** {manifest.get('version')}  ",
        f"**Generados:** {manifest.get('total_generated', 0)}  ",
        f"**Fecha:** {manifest.get('generated_at', '')}",
        "",
        "Yo genero estos dashboards desde `config/dashboard_catalog.yml`. Si cambia una pregunta económica, owner o parámetro, cambio configuración y regenero.",
        "",
    ]
    for family, items in sorted(by_family.items()):
        lines.append(f"## {family}")
        lines.append("| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |")
        lines.append("|---|---|---|---|---|")
        for item in sorted(items, key=lambda x: x["id"]):
            html_rel = Path(item["html_path"]).relative_to(GENERATED_DIR.relative_to(PROJECT_ROOT)) if item["html_path"].startswith("reports/generated_dashboards/") else item["html_path"]
            md_rel = Path(item["markdown_path"]).relative_to(GENERATED_DIR.relative_to(PROJECT_ROOT)) if item["markdown_path"].startswith("reports/generated_dashboards/") else item["markdown_path"]
            lines.append(f"| {item['name']} | {item['priority']} | `{item['params_ref']}` | [{item['id']}]({html_rel}) | [{item['id']}]({md_rel}) |")
        lines.append("")
    INDEX_MD_PATH.write_text("\n".join(lines), encoding="utf-8")

    cards = []
    for item in dashboards:
        rel = Path(item["html_path"]).relative_to(GENERATED_DIR.relative_to(PROJECT_ROOT)) if item["html_path"].startswith("reports/generated_dashboards/") else item["html_path"]
        cards.append(f"<div class='card'><h3>{html.escape(item['name'])}</h3><p>{html.escape(item['family'])} · {html.escape(item['priority'])}</p><p><code>{html.escape(item['params_ref'])}</code></p><a href='{html.escape(str(rel))}'>Abrir dashboard</a></div>")
    INDEX_HTML_PATH.write_text(f"""<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>Dashboard Generator</title><style>body{{font-family:Arial,sans-serif;margin:32px;background:#f7f8fb;color:#0b2538}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}}.card{{background:white;border:1px solid #d9e0e8;border-radius:14px;padding:18px;box-shadow:0 2px 8px rgba(0,0,0,.04)}}a{{color:#0a66c2}}code{{background:#eef3f7;padding:3px 6px;border-radius:5px}}</style></head><body><h1>Dashboard Generator From Catalog</h1><p>Generados: {len(dashboards)} · {html.escape(str(manifest.get('generated_at','')))}</p><div class='grid'>{''.join(cards)}</div></body></html>""", encoding="utf-8")
    return INDEX_MD_PATH, INDEX_HTML_PATH


def generate_family_indexes(manifest: dict[str, Any] | None = None) -> dict[str, str]:
    """
    Yo genero un índice por familia para que el dashboard catalogado se pueda navegar por producto de decisión.
    """
    if manifest is None:
        manifest = read_json_if_exists(MANIFEST_PATH)
    dashboards = manifest.get("dashboards", [])
    by_family: dict[str, list[dict[str, Any]]] = {}
    for item in dashboards:
        by_family.setdefault(item["family"], []).append(item)

    family_outputs: dict[str, str] = {}
    for family, items in by_family.items():
        family_dir = GENERATED_DIR / family
        family_dir.mkdir(parents=True, exist_ok=True)
        lines = [f"# Familia dashboard: {family}", "", "| Dashboard | Prioridad | Donde cambiar |", "|---|---|---|"]
        html_cards = []
        for item in sorted(items, key=lambda x: x["id"]):
            lines.append(f"| [{item['name']}]({Path(item['html_path']).name}) | {item['priority']} | `{item['params_ref']}` |")
            html_cards.append(f"<li><a href='{Path(item['html_path']).name}'>{html.escape(item['name'])}</a> · {html.escape(item['priority'])}</li>")
        md_path = family_dir / "index.md"
        html_path = family_dir / "index.html"
        md_path.write_text("\n".join(lines), encoding="utf-8")
        html_path.write_text(f"<!doctype html><html lang='es'><head><meta charset='utf-8'><title>{html.escape(family)}</title></head><body><h1>{html.escape(family)}</h1><ul>{''.join(html_cards)}</ul><p><a href='../index.html'>Volver</a></p></body></html>", encoding="utf-8")
        family_outputs[family] = str(md_path.relative_to(PROJECT_ROOT))
    return family_outputs


def validate_generated_dashboards() -> dict[str, Any]:
    """
    Yo valido que el generador haya creado artefactos suficientes y que no filtre términos sensibles obvios.
    """
    manifest = read_json_if_exists(MANIFEST_PATH)
    dashboards = manifest.get("dashboards", [])
    errors: list[str] = []
    warnings: list[str] = []
    if len(dashboards) < 60:
        errors.append(f"Se esperaban al menos 60 dashboards generados y encontré {len(dashboards)}")
    for item in dashboards:
        for key in ["markdown_path", "html_path", "json_path"]:
            path = PROJECT_ROOT / item[key]
            if not path.exists():
                errors.append(f"No existe artefacto generado: {path}")
        # Yo reviso que los dashboards públicos no expongan nombres de campos sensibles como contenido operativo.
        text = (PROJECT_ROOT / item["markdown_path"]).read_text(encoding="utf-8").lower()
        if item.get("family") == "public" and any(term in text for term in ["documento", "dni", "email", "telefono", "teléfono"]):
            errors.append(f"Dashboard público menciona campo sensible: {item['id']}")
    if not INDEX_MD_PATH.exists() or not INDEX_HTML_PATH.exists():
        errors.append("No existe índice maestro de dashboards generados")
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_dashboards": len(dashboards),
        "errors": errors,
        "warnings": warnings,
        "status": "ok" if not errors else "fail",
    }
    (GENERATED_DIR / "dashboard_generation_validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def dashboard_generator_metadata() -> dict[str, Any]:
    """
    Yo expongo metadata resumida del generador para API y auditoría.
    """
    manifest = read_json_if_exists(MANIFEST_PATH)
    return {
        "version": manifest.get("version", "v1.4_dashboard_generator_from_catalog"),
        "total_generated": manifest.get("total_generated", 0),
        "families": manifest.get("families", []),
        "index_html": str(INDEX_HTML_PATH.relative_to(PROJECT_ROOT)),
        "index_md": str(INDEX_MD_PATH.relative_to(PROJECT_ROOT)),
        "safe_aggregate_only": manifest.get("safe_aggregate_only", True),
    }
