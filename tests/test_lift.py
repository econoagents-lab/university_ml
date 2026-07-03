import pandas as pd

from src.mlu.lift import compute_lift_deciles, precision_at_k, summarize_lift


def test_compute_lift_deciles_orders_top_risk():
    df = pd.DataFrame({
        "riesgo_caida": [0.9, 0.8, 0.7, 0.2, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01],
        "caida_30d": [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        "precio_departamento": [100] * 10,
    })
    lift = compute_lift_deciles(df, n_deciles=5)
    summary = summarize_lift(lift)
    assert lift.loc[lift["decile"] == 1, "event_rate"].iloc[0] >= df["caida_30d"].mean()
    assert summary.top_decile_lift >= 1


def test_precision_at_k_basic():
    df = pd.DataFrame({"score": [0.9, 0.8, 0.1], "target": [1, 0, 1]})
    out = precision_at_k(df, "score", "target", [1, 2])
    assert out.loc[out["k"] == 1, "precision_at_k"].iloc[0] == 1
