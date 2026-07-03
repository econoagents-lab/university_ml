import pandas as pd
import pytest

from src.mlu.leakage import assert_no_forbidden_columns
from src.mlu.official_rules import build_model_ready_dataset


def test_model_ready_removes_forbidden_columns():
    df = pd.DataFrame({
        "codigo_proforma": ["P1"],
        "codigo_unidad": ["U1"],
        "fecha_snapshot": ["2026-01-01"],
        "proyecto": ["Proyecto Demo"],
        "asesor": ["Asesor Demo"],
        "medio_captacion": ["facebook"],
        "canal_agrupado": ["digital"],
        "dormitorios": [2],
        "precio_departamento": [300000.0],
        "dias_en_tuberia": [10],
        "tiene_cuota_inicial": [True],
        "cambios_unidad": [0],
        "interacciones_ult_7d": [1],
        "descuento_pct": [0.02],
        "fecha_caida": ["2026-01-20"],
        "caida_30d": [1],
    })
    out = build_model_ready_dataset(df)
    assert "fecha_caida" not in out.columns
    assert "caida_30d" in out.columns


def test_anti_leakage_fails_if_forbidden_column_in_x():
    df = pd.DataFrame({"proyecto": ["A"], "fecha_caida": ["2026-01-01"]})
    with pytest.raises(ValueError):
        assert_no_forbidden_columns(df, context="test")
