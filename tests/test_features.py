from src.mlu.data_loader import load_operations
from src.mlu.features import build_feature_table, build_target, FEATURE_COLUMNS


def test_feature_table_has_expected_columns():
    df = load_operations()
    X = build_feature_table(df)
    assert list(X.columns) == FEATURE_COLUMNS


def test_target_is_binary():
    df = load_operations()
    y = build_target(df)
    assert set(y.unique()).issubset({0, 1})
