import pandas as pd

from src.mlu.foundations import (
    ALLOWED_FEATURES_RIESGO_CAIDA,
    FORBIDDEN_COLUMNS_RIESGO_CAIDA,
    audit_training_dataset,
    build_model_matrix,
    classify_risk_level,
    decision_from_score,
    expected_value_at_risk,
    validate_no_forbidden_columns,
)


def _valid_training_df():
    data = {
        "codigo_proforma": ["P-001"],
        "fecha_snapshot": ["2026-05-15"],
        "caida_30d": [1],
        "proyecto": ["Proyecto Demo"],
        "asesor": ["Asesor Demo"],
        "medio_captacion": ["facebook"],
        "canal_agrupado": ["digital"],
        "dormitorios": [2],
        "precio_departamento": [350000.0],
        "dias_en_tuberia": [14],
        "tiene_cuota_inicial": [True],
        "cambios_unidad": [0],
        "interacciones_ult_7d": [1],
        "descuento_pct": [0.05],
    }
    return pd.DataFrame(data)


def test_classify_risk_level():
    assert classify_risk_level(0.10) == "bajo"
    assert classify_risk_level(0.50) == "medio"
    assert classify_risk_level(0.80) == "alto"


def test_decision_from_score():
    decision = decision_from_score(0.80, owner="Jefe Comercial")
    assert decision["nivel_riesgo"] == "alto"
    assert decision["accion"] == "escalamiento_comercial"
    assert decision["responsable"] == "Jefe Comercial"


def test_expected_value_at_risk():
    assert expected_value_at_risk(0.25, 400000) == 100000.0


def test_build_model_matrix_uses_only_allowed_features():
    df = _valid_training_df()
    df["fecha_caida"] = "2026-05-20"
    x = build_model_matrix(df)
    assert list(x.columns) == ALLOWED_FEATURES_RIESGO_CAIDA
    assert "fecha_caida" not in x.columns


def test_validate_no_forbidden_columns():
    df = _valid_training_df()
    df["fecha_caida"] = "2026-05-20"
    present = validate_no_forbidden_columns(df, FORBIDDEN_COLUMNS_RIESGO_CAIDA)
    assert present == ["fecha_caida"]


def test_audit_training_dataset_ready():
    audit = audit_training_dataset(_valid_training_df())
    assert audit["ready_for_training"] is True
    assert audit["missing_required_columns"] == []
    assert audit["target_rate"] == 1.0
