from __future__ import annotations

import html

import json
from pathlib import Path

from fastapi import FastAPI, Query, Header, HTTPException, Depends
from fastapi.responses import FileResponse, HTMLResponse

from api.schemas import (
    RiesgoCaidaBatchInput,
    RiesgoCaidaBatchOutput,
    RiesgoCaidaInput,
    RiesgoCaidaOutput,
    FeedbackRiesgoCaidaInput,
    FeedbackRiesgoCaidaOutput,
)
from api.services import predict_riesgo_caida, append_feedback
from src.mlu.config import FEATURE_COLUMNS_PATH, MODEL_MANIFEST_PATH, PROJECT_ROOT

app = FastAPI(
    title="Machine Learning University API",
    description="API educativa-productiva para servir modelos de ML inmobiliario con datos sintéticos o Sperant/Redshift.",
    version="1.0.0",
)


def optional_api_key_guard(x_api_key: str | None = Header(default=None)) -> bool:
    from src.mlu.security import require_api_key
    if not require_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")
    return True


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "machine-learning-university", "version": "1.0.0"}


@app.get("/metadata/model")
def model_metadata():
    if MODEL_MANIFEST_PATH.exists():
        return json.loads(MODEL_MANIFEST_PATH.read_text(encoding="utf-8"))
    return {"status": "model_manifest_not_found", "path": str(MODEL_MANIFEST_PATH)}


@app.get("/metadata/features")
def feature_metadata():
    if FEATURE_COLUMNS_PATH.exists():
        return {"features": json.loads(FEATURE_COLUMNS_PATH.read_text(encoding="utf-8"))}
    return {"status": "feature_columns_not_found", "path": str(FEATURE_COLUMNS_PATH)}


@app.get("/contracts/riesgo-caida")
def riesgo_caida_contract():
    path = PROJECT_ROOT / "contracts" / "official_business_rules_cygnus_sperant.yml"
    if path.exists():
        return {"contract_path": str(path), "contract_text": path.read_text(encoding="utf-8")}
    return {"status": "contract_not_found", "path": str(path)}


@app.post("/predict/riesgo-caida", response_model=RiesgoCaidaOutput)
def predict(payload: RiesgoCaidaInput):
    return predict_riesgo_caida(payload.model_dump())


@app.post("/predict/riesgo-caida/batch", response_model=RiesgoCaidaBatchOutput)
def predict_batch(payload: RiesgoCaidaBatchInput):
    resultados = [predict_riesgo_caida(row.model_dump()) for row in payload.operaciones]
    return {"total_operaciones": len(resultados), "resultados": resultados}



@app.get("/feedback/riesgo-caida/schema")
def feedback_schema():
    path = PROJECT_ROOT / "contracts" / "feedback_contract_riesgo_caida.yml"
    return {"contract_path": str(path), "contract_text": path.read_text(encoding="utf-8") if path.exists() else "not_found"}


@app.post("/feedback/riesgo-caida", response_model=FeedbackRiesgoCaidaOutput)
def register_feedback(payload: FeedbackRiesgoCaidaInput):
    return append_feedback(payload.model_dump())


@app.get("/monitoring/riesgo-caida/latest")
def latest_monitoring_report():
    path = PROJECT_ROOT / "reports" / "monitoring" / "weekly_monitoring_manifest.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"status": "monitoring_manifest_not_found", "path": str(path)}


@app.get("/experiments/riesgo-caida/schema")
def experiment_schema():
    path = PROJECT_ROOT / "contracts" / "experiment_contract_riesgo_caida.yml"
    return {"contract_path": str(path), "contract_text": path.read_text(encoding="utf-8") if path.exists() else "not_found"}


@app.get("/metadata/model-registry")
def model_registry_metadata():
    from src.mlu.registry import registry_metadata
    return registry_metadata()



@app.get("/decision/riesgo-caida/kpis")
def decision_kpis():
    from src.mlu.decision_dashboard import load_dashboard_payload
    return load_dashboard_payload()["kpis"]


@app.get("/decision/riesgo-caida/queue")
def decision_queue(limit: int = Query(50, ge=1, le=500), prioridad: str | None = None):
    from src.mlu.decision_dashboard import load_decision_queue
    df = load_decision_queue(limit=limit, prioridad=prioridad)
    return {"total": int(len(df)), "items": df.to_dict(orient="records")}


@app.get("/decision/riesgo-caida/by-proyecto")
def decision_by_project():
    from src.mlu.decision_dashboard import aggregate_by, load_decision_queue
    df = load_decision_queue()
    return {"items": aggregate_by(df, "proyecto", top_n=50).to_dict(orient="records")}


@app.get("/decision/riesgo-caida/by-asesor")
def decision_by_advisor():
    from src.mlu.decision_dashboard import aggregate_by, load_decision_queue
    df = load_decision_queue()
    return {"items": aggregate_by(df, "asesor", top_n=50).to_dict(orient="records")}


@app.get("/decision/riesgo-caida/action-plan")
def decision_action_plan(limit: int = Query(25, ge=1, le=200)):
    from src.mlu.decision_dashboard import load_decision_queue
    df = load_decision_queue(limit=limit)
    cols = ["ranking_decision", "codigo_proforma", "codigo_unidad", "proyecto", "asesor", "riesgo_caida", "prioridad_operativa", "sla_horas", "fecha_limite_accion", "valor_esperado_en_riesgo", "accion_operativa"]
    return {"total": int(len(df)), "items": df[[c for c in cols if c in df.columns]].to_dict(orient="records")}


@app.get("/decision/riesgo-caida/brief")
def decision_brief():
    from src.mlu.decision_dashboard import EXECUTIVE_BRIEF_PATH, generate_executive_brief, load_dashboard_payload
    if not EXECUTIVE_BRIEF_PATH.exists():
        generate_executive_brief(load_dashboard_payload())
    return {"brief_path": str(EXECUTIVE_BRIEF_PATH), "brief_text": EXECUTIVE_BRIEF_PATH.read_text(encoding="utf-8")}


@app.get("/decision/riesgo-caida/export/csv")
def decision_export_csv():
    from src.mlu.decision_dashboard import DECISION_QUEUE_CSV_PATH, load_decision_queue, save_decision_artifacts, build_dashboard_payload
    if not DECISION_QUEUE_CSV_PATH.exists():
        df = load_decision_queue()
        save_decision_artifacts(df, build_dashboard_payload(df))
    return FileResponse(str(DECISION_QUEUE_CSV_PATH), media_type="text/csv", filename="decision_queue_riesgo_caida.csv")


@app.get("/dashboard/riesgo-caida", response_class=HTMLResponse)
def dashboard_riesgo_caida():
    from src.mlu.decision_dashboard import DASHBOARD_HTML_PATH, generate_dashboard_html, load_dashboard_payload
    if not DASHBOARD_HTML_PATH.exists():
        generate_dashboard_html(load_dashboard_payload())
    return HTMLResponse(DASHBOARD_HTML_PATH.read_text(encoding="utf-8"))


@app.get("/production/health")
def production_health():
    from src.mlu.production import load_readiness_metadata
    readiness = load_readiness_metadata()
    return {
        "status": "ok",
        "service": "machine-learning-university",
        "version": "1.0.0",
        "release": "v1.0_production_release",
        "readiness_status": readiness.get("status"),
        "checks_ok": readiness.get("checks_ok"),
        "checks_total": readiness.get("checks_total"),
    }


@app.get("/metadata/release")
def release_metadata():
    from src.mlu.production import load_release_metadata
    return load_release_metadata()


@app.get("/metadata/production-readiness")
def production_readiness_metadata():
    from src.mlu.production import load_readiness_metadata
    return load_readiness_metadata()


@app.get("/feedback/store/schema")
def feedback_store_schema_endpoint():
    from src.mlu.feedback_store import feedback_store_schema
    return feedback_store_schema()


@app.get("/auth/whoami")
def auth_whoami(role: str = Query("public"), _auth: bool = Depends(optional_api_key_guard)):
    from src.mlu.security import get_security_settings, role_capabilities
    settings = get_security_settings()
    return {"security": settings.__dict__, "access": role_capabilities(role)}


@app.get("/production/release/checklist")
def production_release_checklist():
    path = PROJECT_ROOT / "docs" / "PRODUCTION_RELEASE_CHECKLIST.md"
    return {"path": str(path), "text": path.read_text(encoding="utf-8") if path.exists() else "not_found"}


@app.get("/metadata/uni-final-rag")
def get_uni_final_rag_metadata():
    """
    Yo expongo metadata del entregable UNI para demostrar trazabilidad del sistema RAG.
    """
    return {
        "version": "v1.1_uni_final_rag_economic_hypothesis_pack",
        "domain": "inteligencia comercial inmobiliaria",
        "techniques": ["citations", "guardrails", "multi_query_expansion", "reranking", "text_to_sql", "ragas_like_evaluation"],
        "notebook": "notebooks/UNI_Final_RAG_Asistente_Economico_Inmobiliario.ipynb",
        "safe_mode": True,
    }


@app.get("/public/decision-dashboard/payload")
def public_decision_dashboard_payload():
    """
    Yo sirvo a Railway solo un payload agregado y público, nunca filas con clientes.
    """
    from src.mlu.decision_dashboard import load_public_dashboard_payload
    try:
        return load_public_dashboard_payload()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/public/decision-dashboard", response_class=HTMLResponse)
def public_decision_dashboard_html():
    """
    Yo sirvo un dashboard público agregado para demo comercial en Railway.
    """
    from src.mlu.decision_dashboard import generate_public_dashboard_html, load_public_dashboard_payload
    try:
        payload = load_public_dashboard_payload()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    path = generate_public_dashboard_html(payload)
    return HTMLResponse(path.read_text(encoding="utf-8"))

@app.get("/metadata/dashboard-catalog")
def dashboard_catalog_metadata():
    """
    Yo expongo el catálogo de dashboards para auditar qué productos de decisión existen.
    """
    from src.mlu.dashboard_control import dashboard_control_metadata, load_dashboard_catalog
    meta = dashboard_control_metadata()
    catalog = load_dashboard_catalog()
    return {**meta, "dashboards": catalog.get("dashboards", [])}


@app.get("/metadata/dashboard-params")
def dashboard_params_metadata():
    """
    Yo expongo decisiones y parámetros de alto nivel sin revelar datos CRM.
    """
    from src.mlu.dashboard_control import load_dashboard_params, load_privacy_policy
    params = load_dashboard_params()
    privacy = load_privacy_policy()
    return {
        "version": params.get("version"),
        "validated_decisions": params.get("validated_decisions", {}),
        "public_dashboard": params.get("public_dashboard", {}),
        "privacy_public_dashboard": privacy.get("public_dashboard", {}),
    }


@app.get("/metadata/generated-dashboards")
def generated_dashboards_metadata():
    """
    Yo expongo metadata de los dashboards generados desde catálogo para auditoría y demo.
    """
    from src.mlu.dashboard_generator import dashboard_generator_metadata
    return dashboard_generator_metadata()


@app.get("/dashboard/catalog", response_class=HTMLResponse)
def dashboard_catalog_generated_index():
    """
    Yo sirvo el índice HTML de dashboards generados desde catálogo.
    """
    from src.mlu.dashboard_generator import INDEX_HTML_PATH, generate_dashboards_from_catalog
    if not INDEX_HTML_PATH.exists():
        generate_dashboards_from_catalog()
    return HTMLResponse(INDEX_HTML_PATH.read_text(encoding="utf-8"))


@app.get("/metadata/dashboard-metrics")
def dashboard_metrics_metadata_endpoint():
    """
    Yo expongo métricas específicas por familia para auditar la inteligencia de cada dashboard.
    """
    from src.mlu.dashboard_metrics_engine import dashboard_metrics_metadata
    return dashboard_metrics_metadata()


@app.get("/dashboard/metrics", response_class=HTMLResponse)
def dashboard_metrics_report():
    """
    Yo sirvo el reporte maestro de métricas específicas por familia.
    """
    from src.mlu.dashboard_metrics_engine import ENGINE_REPORT_MD, build_family_metrics
    if not ENGINE_REPORT_MD.exists():
        build_family_metrics()
    text = ENGINE_REPORT_MD.read_text(encoding="utf-8")
    html_text = "<html><body><pre style='white-space:pre-wrap;font-family:Arial'>" + html.escape(text) + "</pre></body></html>"
    return HTMLResponse(html_text)


@app.get("/metadata/real-marts")
def real_marts_metadata_endpoint():
    """
    Yo expongo metadata de marts reales para distinguir evidencia oficial de proxy.
    """
    from src.mlu.real_marts import real_mart_metadata
    return real_mart_metadata()


@app.get("/dashboard/real-marts", response_class=HTMLResponse)
def real_marts_report_endpoint():
    """
    Yo sirvo el reporte maestro de expansión de marts reales.
    """
    from src.mlu.real_marts import REAL_MART_REPORT_MD, build_all_real_marts
    if not REAL_MART_REPORT_MD.exists():
        build_all_real_marts()
    text = REAL_MART_REPORT_MD.read_text(encoding="utf-8")
    html_text = "<html><body><pre style='white-space:pre-wrap;font-family:Arial'>" + html.escape(text) + "</pre></body></html>"
    return HTMLResponse(html_text)

@app.get("/metadata/action-feedback")
def action_feedback_metadata_endpoint():
    """
    Yo expongo metadata del ciclo alerta -> acción -> feedback -> aprendizaje sin revelar datos personales.
    """
    from src.mlu.decision_action_feedback_lab import action_feedback_metadata
    return action_feedback_metadata()


@app.get("/dashboard/action-feedback", response_class=HTMLResponse)
def action_feedback_report_endpoint():
    """
    Yo sirvo el reporte ejecutivo del laboratorio de acciones y feedback.
    """
    from src.mlu.decision_action_feedback_lab import REPORT_MD, run_decision_action_feedback_lab
    if not REPORT_MD.exists():
        run_decision_action_feedback_lab()
    text = REPORT_MD.read_text(encoding="utf-8")
    html_text = "<html><body><pre style='white-space:pre-wrap;font-family:Arial'>" + html.escape(text) + "</pre></body></html>"
    return HTMLResponse(html_text)


@app.get("/decision/action-feedback/queue")
def action_feedback_queue(limit: int = Query(50, ge=1, le=500), prioridad: str | None = None):
    """
    Yo devuelvo la cola segura de acciones para operación comercial, sin clientes ni códigos crudos.
    """
    import pandas as pd
    from src.mlu.decision_action_feedback_lab import QUEUE_CSV, run_decision_action_feedback_lab
    if not QUEUE_CSV.exists():
        run_decision_action_feedback_lab()
    df = pd.read_csv(QUEUE_CSV)
    if prioridad:
        df = df[df["prioridad"].astype(str).str.upper() == prioridad.upper()]
    return {"total": int(len(df)), "items": df.head(limit).to_dict(orient="records")}


@app.get("/metadata/experimentation-causal-impact")
def experimentation_causal_impact_metadata_endpoint():
    """
    Yo expongo metadata segura del laboratorio causal.
    """
    from src.mlu.experimentation_causal_impact_lab import experimentation_metadata
    return experimentation_metadata()


@app.get("/dashboard/experimentation-causal-impact", response_class=HTMLResponse)
def experimentation_causal_impact_report_endpoint():
    """
    Yo sirvo el reporte ejecutivo del laboratorio de impacto causal.
    """
    from src.mlu.experimentation_causal_impact_lab import REPORT_MD, run_experimentation_causal_impact_lab
    if not REPORT_MD.exists():
        run_experimentation_causal_impact_lab()
    text = REPORT_MD.read_text(encoding="utf-8")
    html_text = "<html><body><pre style='white-space:pre-wrap;font-family:Arial'>" + html.escape(text) + "</pre></body></html>"
    return HTMLResponse(html_text)


@app.get("/experiments/causal-impact/assignment")
def causal_impact_assignment(limit: int = Query(50, ge=1, le=500), arm: str | None = None):
    """
    Yo devuelvo asignaciones experimentales seguras, sin datos personales.
    """
    import pandas as pd
    from src.mlu.experimentation_causal_impact_lab import ASSIGNMENT_CSV, run_experimentation_causal_impact_lab
    if not ASSIGNMENT_CSV.exists():
        run_experimentation_causal_impact_lab()
    df = pd.read_csv(ASSIGNMENT_CSV)
    if arm:
        df = df[df["experiment_arm"].astype(str).str.lower() == arm.lower()]
    return {"total": int(len(df)), "items": df.head(limit).to_dict(orient="records")}


@app.get("/experiments/causal-impact/summary")
def causal_impact_summary_endpoint():
    """
    Yo devuelvo el resumen de impacto tratamiento vs control.
    """
    from src.mlu.experimentation_causal_impact_lab import IMPACT_SUMMARY_JSON, evaluate_causal_impact, read_json
    if not IMPACT_SUMMARY_JSON.exists():
        evaluate_causal_impact()
    return read_json(IMPACT_SUMMARY_JSON)


@app.get("/metadata/experiment-power-policy")
def experiment_power_policy_metadata_endpoint():
    """
    Yo expongo metadata segura del motor de poder experimental y política comercial.
    """
    from src.mlu.experiment_power_policy_engine import experiment_power_policy_metadata
    return experiment_power_policy_metadata()


@app.get("/dashboard/experiment-power-policy", response_class=HTMLResponse)
def experiment_power_policy_report_endpoint():
    """
    Yo sirvo el reporte ejecutivo del motor de política experimental.
    """
    from src.mlu.experiment_power_policy_engine import REPORT_MD, run_experiment_power_policy_engine
    if not REPORT_MD.exists():
        run_experiment_power_policy_engine()
    text = REPORT_MD.read_text(encoding="utf-8")
    html_text = "<html><body><pre style='white-space:pre-wrap;font-family:Arial'>" + html.escape(text) + "</pre></body></html>"
    return HTMLResponse(html_text)


@app.get("/experiments/policy/segments")
def experiment_policy_segments(limit: int = Query(50, ge=1, le=500), dimension: str | None = None):
    """
    Yo devuelvo impacto por segmento sin datos personales.
    """
    import pandas as pd
    from src.mlu.experiment_power_policy_engine import SEGMENT_IMPACT_CSV, run_experiment_power_policy_engine
    if not SEGMENT_IMPACT_CSV.exists():
        run_experiment_power_policy_engine()
    df = pd.read_csv(SEGMENT_IMPACT_CSV)
    if dimension and "dimension" in df.columns:
        df = df[df["dimension"].astype(str).str.lower() == dimension.lower()]
    return {"total": int(len(df)), "items": df.head(limit).to_dict(orient="records")}


@app.get("/experiments/policy/recommendations")
def experiment_policy_recommendations():
    """
    Yo devuelvo SLA, capacidad y política de escalamiento para operación comercial.
    """
    from src.mlu.experiment_power_policy_engine import (
        ESCALATION_POLICY_JSON,
        SLA_RECOMMENDATIONS_JSON,
        read_json,
        run_experiment_power_policy_engine,
    )
    if not SLA_RECOMMENDATIONS_JSON.exists() or not ESCALATION_POLICY_JSON.exists():
        run_experiment_power_policy_engine()
    return {
        "sla_capacity": read_json(SLA_RECOMMENDATIONS_JSON),
        "escalation_policy": read_json(ESCALATION_POLICY_JSON),
    }

@app.get("/metadata/productized-os")
def productized_os_metadata_endpoint():
    """
    Yo expongo el estado de producto v2.0 para demo, auditoría y venta consultiva.
    """
    from src.mlu.productized_commercial_intelligence_os import productized_os_metadata
    return productized_os_metadata()


@app.get("/dashboard/productized-os", response_class=HTMLResponse)
def productized_os_dashboard_endpoint():
    """
    Yo sirvo el índice HTML del producto comercial v2.0.
    """
    from src.mlu.productized_commercial_intelligence_os import INDEX_HTML, run_productized_os_release
    if not INDEX_HTML.exists():
        run_productized_os_release()
    return HTMLResponse(INDEX_HTML.read_text(encoding="utf-8"))


@app.get("/product/demo/package")
def productized_os_demo_package_endpoint():
    """
    Yo devuelvo el paquete de demo comercial con one-pager, guion y flujo recomendado.
    """
    from src.mlu.productized_commercial_intelligence_os import DEMO_PACKAGE_JSON, read_json, run_productized_os_release
    if not DEMO_PACKAGE_JSON.exists():
        run_productized_os_release()
    return read_json(DEMO_PACKAGE_JSON)



@app.get("/metadata/client-ready")
def client_ready_metadata_endpoint():
    """
    Yo expongo metadata de la demo cliente v2.1: marca, landing, Railway y privacidad.
    """
    from src.mlu.client_ready_branding_and_deployment import client_ready_metadata
    return client_ready_metadata()


@app.get("/demo/client-ready", response_class=HTMLResponse)
def client_ready_demo_endpoint(demo_token: str | None = Query(default=None), x_demo_token: str | None = Header(default=None)):
    """
    Yo sirvo la landing cliente con token simple opcional para demos externas.
    """
    from src.mlu.client_ready_branding_and_deployment import (
        LANDING_HTML,
        run_client_ready_branding_and_deployment,
        validate_demo_token,
    )
    token = x_demo_token or demo_token
    if not validate_demo_token(token):
        raise HTTPException(status_code=401, detail="Demo token inválido o ausente")
    if not LANDING_HTML.exists():
        run_client_ready_branding_and_deployment()
    return HTMLResponse(LANDING_HTML.read_text(encoding="utf-8"))


@app.get("/demo/landing", response_class=HTMLResponse)
def client_ready_landing_alias(demo_token: str | None = Query(default=None), x_demo_token: str | None = Header(default=None)):
    """
    Yo expongo un alias corto de la landing comercial para compartirla en demo.
    """
    return client_ready_demo_endpoint(demo_token=demo_token, x_demo_token=x_demo_token)


@app.get("/metadata/client-tenants")
def client_tenants_metadata_endpoint():
    """
    Yo expongo metadata de paquetes multi-tenant para saber qué demos cliente existen y si son seguras.
    """
    from src.mlu.multi_tenant_client_packaging import client_tenant_metadata
    return client_tenant_metadata()


@app.get("/demo/tenants", response_class=HTMLResponse)
def client_tenants_index_endpoint():
    """
    Yo sirvo el índice HTML de demos por cliente.
    """
    from src.mlu.multi_tenant_client_packaging import TENANT_INDEX_HTML, run_multi_tenant_client_packaging
    if not TENANT_INDEX_HTML.exists():
        run_multi_tenant_client_packaging()
    return HTMLResponse(TENANT_INDEX_HTML.read_text(encoding="utf-8"))


@app.get("/demo/client/{tenant_id}", response_class=HTMLResponse)
def client_tenant_landing_endpoint(tenant_id: str, demo_token: str | None = Query(default=None), x_demo_token: str | None = Header(default=None)):
    """
    Yo sirvo una landing específica por tenant con token por cliente en producción.
    """
    from src.mlu.multi_tenant_client_packaging import tenant_dir, normalize_tenant_id, run_multi_tenant_client_packaging, validate_tenant_token
    token = x_demo_token or demo_token
    if not validate_tenant_token(tenant_id, token):
        raise HTTPException(status_code=401, detail="Token de tenant inválido o ausente")
    landing = tenant_dir(normalize_tenant_id(tenant_id)) / "landing.html"
    if not landing.exists():
        run_multi_tenant_client_packaging()
    if not landing.exists():
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    return HTMLResponse(landing.read_text(encoding="utf-8"))


@app.get("/product/client/{tenant_id}/package")
def client_tenant_package_endpoint(tenant_id: str):
    """
    Yo devuelvo el paquete comercial de un tenant: módulos, rutas, artifacts y estado de privacidad.
    """
    from src.mlu.multi_tenant_client_packaging import get_tenant_package
    try:
        return get_tenant_package(tenant_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")


@app.get("/metadata/client-proposals")
def client_proposals_metadata_endpoint():
    """
    Yo expongo metadata del motor de propuestas comerciales por cliente.
    """
    from src.mlu.client_proposal_and_contract_automation import client_proposal_metadata
    return client_proposal_metadata()


@app.get("/proposals/clients", response_class=HTMLResponse)
def client_proposals_index_endpoint():
    """
    Yo sirvo el índice HTML de propuestas comerciales por cliente.
    """
    from src.mlu.client_proposal_and_contract_automation import INDEX_HTML, run_client_proposal_and_contract_automation
    if not INDEX_HTML.exists():
        run_client_proposal_and_contract_automation()
    return HTMLResponse(INDEX_HTML.read_text(encoding="utf-8"))


@app.get("/proposal/client/{tenant_id}", response_class=HTMLResponse)
def client_proposal_html_endpoint(tenant_id: str):
    """
    Yo sirvo la propuesta HTML de un tenant específico.
    """
    from src.mlu.client_proposal_and_contract_automation import normalize_tenant_id, run_client_proposal_and_contract_automation, tenant_output_dir
    tenant_id = normalize_tenant_id(tenant_id)
    proposal = tenant_output_dir(tenant_id) / "proposal.html"
    if not proposal.exists():
        run_client_proposal_and_contract_automation()
    if not proposal.exists():
        raise HTTPException(status_code=404, detail="Propuesta de tenant no encontrada")
    return HTMLResponse(proposal.read_text(encoding="utf-8"))


@app.get("/proposal/client/{tenant_id}/package")
def client_proposal_package_endpoint(tenant_id: str):
    """
    Yo devuelvo el paquete de propuesta, precio, scope y contrato de métricas por tenant.
    """
    from src.mlu.client_proposal_and_contract_automation import get_client_proposal_package
    try:
        return get_client_proposal_package(tenant_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Propuesta de tenant no encontrada")

@app.get("/metadata/contract-ops")
def contract_ops_metadata_endpoint():
    """
    Yo expongo metadata del motor propuesta → firma → invoice.
    """
    from src.mlu.contract_to_signature_and_invoice_ops import contract_ops_metadata
    return contract_ops_metadata()


@app.get("/contracts/ops/clients", response_class=HTMLResponse)
def contract_ops_clients_index_endpoint():
    """
    Yo sirvo el índice HTML de expedientes contractuales por cliente.
    """
    from src.mlu.contract_to_signature_and_invoice_ops import INDEX_HTML, run_contract_to_signature_and_invoice_ops
    if not INDEX_HTML.exists():
        run_contract_to_signature_and_invoice_ops()
    return HTMLResponse(INDEX_HTML.read_text(encoding="utf-8"))


@app.get("/contract/client/{tenant_id}/work-order", response_class=HTMLResponse)
def contract_client_work_order_endpoint(tenant_id: str):
    """
    Yo sirvo la orden de trabajo HTML de un tenant.
    """
    from src.mlu.contract_to_signature_and_invoice_ops import normalize_tenant_id, run_contract_to_signature_and_invoice_ops, tenant_output_dir
    tenant_id = normalize_tenant_id(tenant_id)
    path = tenant_output_dir(tenant_id) / "work_order.html"
    if not path.exists():
        run_contract_to_signature_and_invoice_ops()
    if not path.exists():
        raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada")
    return HTMLResponse(path.read_text(encoding="utf-8"))


@app.get("/contract/client/{tenant_id}/invoice", response_class=HTMLResponse)
def contract_client_invoice_endpoint(tenant_id: str):
    """
    Yo sirvo la proforma HTML de un tenant.
    """
    from src.mlu.contract_to_signature_and_invoice_ops import normalize_tenant_id, run_contract_to_signature_and_invoice_ops, tenant_output_dir
    tenant_id = normalize_tenant_id(tenant_id)
    path = tenant_output_dir(tenant_id) / "invoice_proforma.html"
    if not path.exists():
        run_contract_to_signature_and_invoice_ops()
    if not path.exists():
        raise HTTPException(status_code=404, detail="Proforma no encontrada")
    return HTMLResponse(path.read_text(encoding="utf-8"))


@app.get("/contract/client/{tenant_id}/ops-package")
def contract_client_ops_package_endpoint(tenant_id: str):
    """
    Yo devuelvo el paquete contractual de un tenant.
    """
    from src.mlu.contract_to_signature_and_invoice_ops import get_contract_ops_package
    try:
        return get_contract_ops_package(tenant_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Paquete contractual no encontrado")

@app.get("/metadata/client-success")
def client_success_metadata_endpoint():
    """
    Yo expongo metadata del motor de client success, adopción, churn y renovación.
    """
    from src.mlu.client_success_and_renewal_intelligence import client_success_metadata
    return client_success_metadata()


@app.get("/success/clients", response_class=HTMLResponse)
def client_success_clients_index_endpoint():
    """
    Yo sirvo el índice HTML de salud y renovación por tenant.
    """
    from src.mlu.client_success_and_renewal_intelligence import INDEX_HTML, run_client_success_and_renewal_intelligence
    if not INDEX_HTML.exists():
        run_client_success_and_renewal_intelligence()
    return HTMLResponse(INDEX_HTML.read_text(encoding="utf-8"))


@app.get("/success/client/{tenant_id}/health", response_class=HTMLResponse)
def client_success_health_endpoint(tenant_id: str):
    """
    Yo sirvo el reporte de salud de un tenant específico.
    """
    from src.mlu.client_success_and_renewal_intelligence import normalize_tenant_id, run_client_success_and_renewal_intelligence, tenant_dir
    tenant_id = normalize_tenant_id(tenant_id)
    path = tenant_dir(tenant_id) / "success_health.html"
    if not path.exists():
        run_client_success_and_renewal_intelligence()
    if not path.exists():
        raise HTTPException(status_code=404, detail="Success health no encontrado")
    return HTMLResponse(path.read_text(encoding="utf-8"))


@app.get("/success/client/{tenant_id}/renewal-plan", response_class=HTMLResponse)
def client_success_renewal_plan_endpoint(tenant_id: str):
    """
    Yo sirvo el plan de renovación de un tenant específico.
    """
    from src.mlu.client_success_and_renewal_intelligence import normalize_tenant_id, run_client_success_and_renewal_intelligence, tenant_dir
    tenant_id = normalize_tenant_id(tenant_id)
    path = tenant_dir(tenant_id) / "renewal_plan.html"
    if not path.exists():
        run_client_success_and_renewal_intelligence()
    if not path.exists():
        raise HTTPException(status_code=404, detail="Renewal plan no encontrado")
    return HTMLResponse(path.read_text(encoding="utf-8"))


@app.get("/success/client/{tenant_id}/package")
def client_success_package_endpoint(tenant_id: str):
    """
    Yo devuelvo el paquete JSON de health, adopción, upsell y renovación por tenant.
    """
    from src.mlu.client_success_and_renewal_intelligence import get_client_success_package
    try:
        return get_client_success_package(tenant_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Client success package no encontrado")

