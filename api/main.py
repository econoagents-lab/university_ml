from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI

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
    version="0.6.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "machine-learning-university", "version": "0.6.0"}


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
