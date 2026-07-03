import pandas as pd

from src.mlu.calibration import calibration_table, calibration_summary


def test_calibration_table_has_expected_columns():
    y = [0, 0, 1, 1, 0, 1]
    s = [0.1, 0.2, 0.7, 0.8, 0.3, 0.9]
    table = calibration_table(y, s, n_bins=3)
    assert {"rows", "avg_score", "event_rate", "calibration_gap"}.issubset(table.columns)
    assert table["rows"].sum() == 6


def test_calibration_summary_brier_score():
    y = [0, 1, 0, 1]
    s = [0.1, 0.9, 0.2, 0.8]
    summary = calibration_summary(y, s, n_bins=2)
    assert summary["brier_score"] < 0.1
