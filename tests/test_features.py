import pandas as pd
import pytest

from src.mlu.data_loader import load_operations
from src.mlu.features import build_feature_table, build_target, FEATURE_COLUMNS
from src.mlu.leakage import assert_no_forbidden_columns


def test_feature_table_has_expected_columns():
    df = load_operations()
    X = build_feature_table(df)
    assert list(X.columns) == FEATURE_COLUMNS


def test_feature_table_strips_audit_columns_before_model_matrix():
    df = load_operations().copy()
    df["fecha_caida"] = pd.Timestamp("2026-01-15")
    df["fecha_firma"] = pd.Timestamp("2026-01-10")

    X = build_feature_table(df)

    assert "fecha_caida" not in X.columns
    assert "fecha_firma" not in X.columns
    assert list(X.columns) == FEATURE_COLUMNS


def test_model_matrix_fails_if_forbidden_column_enters_x():
    X = pd.DataFrame({
        "proyecto": ["Proyecto Demo"],
        "fecha_caida": [pd.Timestamp("2026-01-15")],
    })

    with pytest.raises(ValueError, match="Anti-leakage fail"):
        assert_no_forbidden_columns(X, context="model_matrix_X")


def test_target_is_binary():
    df = load_operations()
    y = build_target(df)
    assert set(y.unique()).issubset({0, 1})
