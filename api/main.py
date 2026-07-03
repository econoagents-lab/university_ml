from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Query
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
    version="0.9.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "machine-learning-university", "version": "0.9.0"}


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
