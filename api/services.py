from __future__ import annotations

import pandas as pd

from src.mlu.config import MODEL_PATH
from src.mlu.economics import recommend_decision, expected_value_at_risk


def infer_channel(medio: str) -> str:
    medio_norm = medio.strip().lower()
    if medio_norm in {"facebook", "web", "portal inmobiliario", "whatsapp"}:
        return "digital"
    if medio_norm in {"feria", "feria inmobiliaria"}:
        return "feria"
    return "tradicional"


def baseline_score(payload: dict) -> float:
    riesgo = 0.10
    if payload["dias_en_tuberia"] >= 30:
        riesgo += 0.25
    if not payload["tiene_cuota_inicial"]:
        riesgo += 0.30
    if payload["precio_departamento"] > 600_000:
        riesgo += 0.10
    if payload.get("cambios_unidad", 0) >= 1:
        riesgo += 0.10
    if payload.get("interacciones_ult_7d", 0) >= 2:
        riesgo -= 0.08
    return max(0.01, min(riesgo, 0.95))


def predict_riesgo_caida(payload: dict) -> dict:
    row = {
        "proyecto": payload["proyecto"],
        "asesor": payload["asesor"],
        "medio_captacion": payload["medio_captacion"],
        "canal_agrupado": infer_channel(payload["medio_captacion"]),
        "dormitorios": payload["dormitorios"],
        "precio_departamento": payload["precio_departamento"],
        "dias_en_tuberia": payload["dias_en_tuberia"],
        "tiene_cuota_inicial": int(bool(payload["tiene_cuota_inicial"])),
        "cambios_unidad": payload.get("cambios_unidad", 0),
        "interacciones_ult_7d": payload.get("interacciones_ult_7d", 0),
        "descuento_pct": payload.get("descuento_pct", 0.0),
    }

    modelo_usado = "baseline_rule"
    if MODEL_PATH.exists():
        try:
            # Yo importo el modelo de forma diferida para que endpoints de demo, metadata
            # y multi-tenant no dependan de joblib/scikit-learn durante tests livianos de CI.
            from src.mlu.model import load_model

            model = load_model(MODEL_PATH)
            riesgo = float(model.predict_proba(pd.DataFrame([row]))[:, 1][0])
            modelo_usado = "riesgo_caida_model.joblib"
        except Exception:
            # Yo protejo la API: si el artefacto del modelo o sus dependencias no están
            # disponibles, sirvo baseline en vez de romper rutas que no necesitan ML.
            riesgo = baseline_score(payload)
    else:
        riesgo = baseline_score(payload)

    decision = recommend_decision(riesgo, payload["asesor"])
    return {
        "riesgo_caida": round(riesgo, 4),
        "nivel_riesgo": decision["nivel_riesgo"],
        "decision_recomendada": decision["decision_recomendada"],
        "responsable": decision["responsable"],
        "valor_esperado_en_riesgo": round(expected_value_at_risk(riesgo, payload["precio_departamento"]), 2),
        "modelo_usado": modelo_usado,
    }



def append_feedback(payload: dict) -> dict:
    from src.mlu.feedback_store import append_feedback_record

    return append_feedback_record(payload)
