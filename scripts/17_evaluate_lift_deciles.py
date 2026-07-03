from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import joblib
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.metrics import average_precision_score, roc_auc_score

from src.mlu.lift import compute_lift_deciles, precision_at_k, summarize_lift
from src.mlu.official_rules import FEATURE_COLUMNS, TARGET
from src.mlu.leakage import assert_no_forbidden_columns

MODEL_READY_PATH = Path("data/processed/gold/riesgo_caida_training_model_ready.parquet")
MODEL_PATH = Path("models/riesgo_caida_model.joblib")
OUT_DIR = Path("reports/modeling")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(MODEL_READY_PATH).sort_values("fecha_snapshot").reset_index(drop=True)
    assert_no_forbidden_columns(df, context="lift_model_ready_input")
    split_idx = int(len(df) * 0.75)
    test = df.iloc[split_idx:].copy()
    X_test = test[FEATURE_COLUMNS].copy()
    y_test = test[TARGET].astype(int)
    if "tiene_cuota_inicial" in X_test.columns:
        X_test["tiene_cuota_inicial"] = X_test["tiene_cuota_inicial"].astype(bool).astype(int)
    model = joblib.load(MODEL_PATH)
    test["riesgo_caida"] = model.predict_proba(X_test)[:, 1]

    lift_df = compute_lift_deciles(test, score_col="riesgo_caida", target_col=TARGET, value_col="precio_departamento")
    p_at_k = precision_at_k(test, score_col="riesgo_caida", target_col=TARGET, k_values=[10, 20, 50, 100, 200, len(test)])
    summary = summarize_lift(lift_df)

    lift_df.to_csv(OUT_DIR / "lift_deciles.csv", index=False, encoding="utf-8-sig")
    lift_df.to_parquet(OUT_DIR / "lift_deciles.parquet", index=False)
    p_at_k.to_csv(OUT_DIR / "precision_at_k.csv", index=False, encoding="utf-8-sig")

    metrics = {
        "model_version": "0.6.0-feedback_and_lift",
        "test_rows": int(len(test)),
        "target_rate_test": float(y_test.mean()),
        "roc_auc_test": float(roc_auc_score(y_test, test["riesgo_caida"])),
        "average_precision_test": float(average_precision_score(y_test, test["riesgo_caida"])),
        "top_decile_rate": summary.top_decile_rate,
        "top_decile_lift": summary.top_decile_lift,
        "top_20_capture_rate": summary.top_20_capture_rate,
        "total_positives_test": summary.total_positives,
    }
    (OUT_DIR / "lift_metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    # Visualización simple y portable
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(lift_df["decile"].astype(str), lift_df["lift"])
    ax.axhline(1.0, linestyle="--", linewidth=1)
    ax.set_title("Lift por decil - Riesgo de Caída")
    ax.set_xlabel("Decil de riesgo (1 = mayor riesgo)")
    ax.set_ylabel("Lift vs tasa promedio")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "lift_deciles.png", dpi=160)
    plt.close(fig)

    report = f"""# Lift Report - Riesgo de Caída v0.6

## Lectura ejecutiva

El objetivo de este reporte no es volver a preguntar si el modelo es perfecto. La pregunta correcta es si el ranking concentra más caídas reales en los primeros deciles que una selección aleatoria.

## Métricas clave

| Métrica | Valor |
|---|---:|
| Filas test | {metrics['test_rows']:,} |
| Tasa caída test | {metrics['target_rate_test']:.2%} |
| ROC AUC test | {metrics['roc_auc_test']:.3f} |
| Average Precision test | {metrics['average_precision_test']:.3f} |
| Tasa caída top decil | {metrics['top_decile_rate']:.2%} |
| Lift top decil | {metrics['top_decile_lift']:.2f}x |
| Captura top 20% | {metrics['top_20_capture_rate']:.2%} |

## Interpretación

- Si el lift del primer decil es mayor a 1.0x, el modelo ordena mejor que una lista aleatoria.
- Si el top 20% captura una proporción relevante de caídas, el ranking sirve para priorización comercial.
- Si el lift es débil, el siguiente trabajo no es cambiar de algoritmo primero, sino mejorar features de comportamiento, contacto, banco y cuota inicial.

## Decisión comercial recomendada

1. Revisar diariamente el decil 1.
2. Asignar SLA de 24 horas al decil 1 y 48 horas a deciles 2-3.
3. Registrar feedback por acción tomada.
4. Medir resultados a 7 y 30 días.
"""
    (OUT_DIR / "lift_report.md").write_text(report, encoding="utf-8")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
