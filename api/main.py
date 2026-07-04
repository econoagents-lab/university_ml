from __future__ import annotations

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
