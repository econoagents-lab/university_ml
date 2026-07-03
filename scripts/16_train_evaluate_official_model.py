from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.mlu.official_rules import FEATURE_COLUMNS, TARGET
from src.mlu.leakage import assert_no_forbidden_columns

MODEL_READY_PATH = Path("data/processed/gold/riesgo_caida_training_model_ready.parquet")
MODEL_PATH = Path("models/riesgo_caida_model.joblib")
MANIFEST_PATH = Path("models/model_manifest.json")
FEATURES_PATH = Path("models/feature_columns.json")
NUMERIC_FEATURES = ["dormitorios", "precio_departamento", "dias_en_tuberia", "cambios_unidad", "interacciones_ult_7d", "descuento_pct"]
CATEGORICAL_FEATURES = ["proyecto", "asesor", "medio_captacion", "canal_agrupado"]
BOOLEAN_FEATURES = ["tiene_cuota_inicial"]


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer([
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), NUMERIC_FEATURES),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), CATEGORICAL_FEATURES),
        ("bool", Pipeline([("imputer", SimpleImputer(strategy="most_frequent"))]), BOOLEAN_FEATURES),
    ])
    classifier = RandomForestClassifier(n_estimators=300, max_depth=8, min_samples_leaf=20, class_weight="balanced", random_state=42, n_jobs=-1)
    return Pipeline([("preprocessor", preprocessor), ("model", classifier)])


def main() -> None:
    df = pd.read_parquet(MODEL_READY_PATH).sort_values("fecha_snapshot").reset_index(drop=True)
    assert_no_forbidden_columns(df, context="official_training_input")
    split_idx = int(len(df) * 0.75)
    train, test = df.iloc[:split_idx].copy(), df.iloc[split_idx:].copy()
    X_train, y_train = train[FEATURE_COLUMNS].copy(), train[TARGET].astype(int)
    X_test, y_test = test[FEATURE_COLUMNS].copy(), test[TARGET].astype(int)
    X_train["tiene_cuota_inicial"] = X_train["tiene_cuota_inicial"].astype(bool).astype(int)
    X_test["tiene_cuota_inicial"] = X_test["tiene_cuota_inicial"].astype(bool).astype(int)
    model = build_pipeline()
    model.fit(X_train, y_train)
    proba = model.predict_proba(X_test)[:, 1]
    rows = []
    for th in np.arange(0.10, 0.81, 0.05):
        pred = (proba >= th).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_test, pred, labels=[0, 1]).ravel()
        precision, recall, f1 = precision_score(y_test, pred, zero_division=0), recall_score(y_test, pred, zero_division=0), f1_score(y_test, pred, zero_division=0)
        beta = 2
        f2 = (1 + beta**2) * precision * recall / (beta**2 * precision + recall) if (precision + recall) > 0 else 0
        rows.append({"threshold": round(float(th), 2), "precision": precision, "recall": recall, "f1": f1, "f2": f2, "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn)})
    thresholds = pd.DataFrame(rows)
    threshold = float(thresholds.sort_values(["f2", "recall", "precision"], ascending=[False, False, False]).iloc[0]["threshold"])
    pred = (proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, pred, labels=[0, 1]).ravel()
    metrics = {
        "model_version": "0.5.0-official_rules",
        "total_rows": int(len(df)),
        "training_rows": int(len(train)),
        "test_rows": int(len(test)),
        "target_rate": float(df[TARGET].mean()),
        "roc_auc": float(roc_auc_score(y_test, proba)),
        "average_precision": float(average_precision_score(y_test, proba)),
        "recommended_threshold": threshold,
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "f1": float(f1_score(y_test, pred, zero_division=0)),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "feature_columns": FEATURE_COLUMNS,
    }
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    FEATURES_PATH.write_text(json.dumps(FEATURE_COLUMNS, indent=2, ensure_ascii=False), encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    Path("reports/modeling").mkdir(parents=True, exist_ok=True)
    thresholds.to_csv("reports/modeling/threshold_table.csv", index=False)

    cm = metrics["confusion_matrix"]
    eval_md = f"""# Evaluation Report - Riesgo de Caída v0.5 Official Rules

## Lectura ejecutiva

Modelo gobernado de riesgo de caída entrenado sobre dataset model-ready sin columnas prohibidas.

## Dataset

| Métrica | Valor |
|---|---:|
| Filas totales | {metrics['total_rows']:,} |
| Filas entrenamiento | {metrics['training_rows']:,} |
| Filas prueba | {metrics['test_rows']:,} |
| Tasa histórica de caída 30d | {metrics['target_rate']:.2%} |

## Métricas

| Métrica | Valor |
|---|---:|
| ROC AUC | {metrics['roc_auc']:.3f} |
| Average Precision | {metrics['average_precision']:.3f} |
| Threshold recomendado | {metrics['recommended_threshold']:.2f} |
| Precision | {metrics['precision']:.3f} |
| Recall | {metrics['recall']:.3f} |
| F1 | {metrics['f1']:.3f} |

## Confusion Matrix

| Real / Predicho | Predice No Caída | Predice Caída |
|---|---:|---:|
| Real No Caída | {cm['tn']} | {cm['fp']} |
| Real Caída | {cm['fn']} | {cm['tp']} |

## Lectura económica

- El evento es minoritario; no usar accuracy como métrica principal.
- El falso negativo es el error más caro: una caída no priorizada.
- El ranking operativo debe ordenar por valor esperado en riesgo.

## Anti-leakage

Si `fecha_caida` o cualquier columna prohibida entra a X, el entrenamiento falla.
"""
    Path("reports/modeling/evaluation_report.md").write_text(eval_md, encoding="utf-8")

    model_card = f"""# Model Card - Riesgo de Caída v0.5

- Modelo: riesgo_caida_model
- Versión: 0.5.0-official_rules
- Target: caida_30d
- Uso: priorizar separaciones activas con riesgo de caída en 30 días.

## Métricas

| Métrica | Valor |
|---|---:|
| ROC AUC | {metrics['roc_auc']:.3f} |
| Average Precision | {metrics['average_precision']:.3f} |
| Precision | {metrics['precision']:.3f} |
| Recall | {metrics['recall']:.3f} |
| F1 | {metrics['f1']:.3f} |

## Features

```json
{json.dumps(FEATURE_COLUMNS, indent=2, ensure_ascii=False)}
```

## Limitaciones

No usar para decisiones automáticas de anulación ni evaluación punitiva de asesores.
"""
    Path("models/model_card.md").write_text(model_card, encoding="utf-8")

    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
