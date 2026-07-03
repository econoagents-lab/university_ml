from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score, roc_auc_score, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import PROJECT_ROOT
from .official_rules import FEATURE_COLUMNS, TARGET
from .leakage import assert_no_forbidden_columns
from .registry import ARTIFACTS_DIR, CARDS_DIR, append_experiment_history, register_model, load_model_registry, get_model

NUMERIC_FEATURES = ["dormitorios", "precio_departamento", "dias_en_tuberia", "cambios_unidad", "interacciones_ult_7d", "descuento_pct"]
CATEGORICAL_FEATURES = ["proyecto", "asesor", "medio_captacion", "canal_agrupado"]
BOOLEAN_FEATURES = ["tiene_cuota_inicial"]


def temporal_train_test_split(df: pd.DataFrame, test_size: float = 0.25) -> tuple[pd.DataFrame, pd.DataFrame]:
    sort_col = "fecha_snapshot" if "fecha_snapshot" in df.columns else None
    if sort_col:
        df = df.sort_values(sort_col).reset_index(drop=True)
    split_idx = max(1, min(len(df) - 1, int(len(df) * (1 - test_size))))
    return df.iloc[:split_idx].copy(), df.iloc[split_idx:].copy()


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer([
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), NUMERIC_FEATURES),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), CATEGORICAL_FEATURES),
        ("bool", Pipeline([("imputer", SimpleImputer(strategy="most_frequent"))]), BOOLEAN_FEATURES),
    ])


def build_candidate_models(random_state: int = 42) -> dict[str, Pipeline]:
    return {
        "logistic_regression": Pipeline([
            ("preprocessor", build_preprocessor()),
            ("model", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=random_state)),
        ]),
        "random_forest": Pipeline([
            ("preprocessor", build_preprocessor()),
            ("model", RandomForestClassifier(n_estimators=260, max_depth=8, min_samples_leaf=18, class_weight="balanced", random_state=random_state, n_jobs=-1)),
        ]),
        "gradient_boosting": Pipeline([
            ("preprocessor", build_preprocessor()),
            ("model", GradientBoostingClassifier(n_estimators=120, learning_rate=0.05, max_depth=3, random_state=random_state)),
        ]),
    }


def evaluate_predictions(y_true, proba, threshold: float = 0.40) -> dict:
    pred = (np.asarray(proba) >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
    top_n = max(1, int(len(proba) * 0.10))
    order = np.argsort(-np.asarray(proba))
    top_rate = float(np.asarray(y_true)[order[:top_n]].mean()) if top_n else 0.0
    base_rate = float(np.asarray(y_true).mean()) if len(y_true) else 0.0
    return {
        "roc_auc": float(roc_auc_score(y_true, proba)) if len(set(y_true)) > 1 else None,
        "average_precision": float(average_precision_score(y_true, proba)) if len(set(y_true)) > 1 else None,
        "threshold": float(threshold),
        "precision": float(precision_score(y_true, pred, zero_division=0)),
        "recall": float(recall_score(y_true, pred, zero_division=0)),
        "f1": float(f1_score(y_true, pred, zero_division=0)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        "base_event_rate": base_rate,
        "top_decile_event_rate": top_rate,
        "top_decile_lift": float(top_rate / base_rate) if base_rate else 0.0,
    }


def write_model_card(path: Path, model_id: str, algorithm: str, dataset_version: str, metrics: dict) -> None:
    md = f"""# Model Card - {model_id}

## Identidad

- Proyecto: riesgo_caida
- Algoritmo: {algorithm}
- Dataset version: {dataset_version}
- Uso: priorizar operaciones inmobiliarias con mayor riesgo de caída.

## Métricas

| Métrica | Valor |
|---|---:|
| ROC AUC | {metrics.get('roc_auc') if metrics.get('roc_auc') is not None else 'NA'} |
| Average Precision | {metrics.get('average_precision') if metrics.get('average_precision') is not None else 'NA'} |
| Precision | {metrics.get('precision'):.3f} |
| Recall | {metrics.get('recall'):.3f} |
| F1 | {metrics.get('f1'):.3f} |
| Top decile lift | {metrics.get('top_decile_lift'):.3f} |

## Gobierno

Este modelo solo debe promoverse si supera al champion bajo política de retraining y mantiene anti-leakage.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(md, encoding="utf-8")


def train_challenger_models(dataset_path: str | Path, dataset_version: str = "dataset_unregistered", data_mode: str = "crm") -> list[dict]:
    dataset_path = Path(dataset_path)
    df = pd.read_parquet(dataset_path)
    assert_no_forbidden_columns(df, context="challenger_training_dataset")
    missing = [c for c in FEATURE_COLUMNS + [TARGET] if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas para entrenar challengers: {missing}")
    train, test = temporal_train_test_split(df)
    X_train, y_train = train[FEATURE_COLUMNS].copy(), train[TARGET].astype(int)
    X_test, y_test = test[FEATURE_COLUMNS].copy(), test[TARGET].astype(int)
    X_train["tiene_cuota_inicial"] = X_train["tiene_cuota_inicial"].astype(bool).astype(int)
    X_test["tiene_cuota_inicial"] = X_test["tiene_cuota_inicial"].astype(bool).astype(int)

    results: list[dict] = []
    for idx, (algorithm, model) in enumerate(build_candidate_models().items(), start=1):
        model_id = f"riesgo_caida_{algorithm}_{dataset_version}_c{idx:02d}".replace("-", "_")
        model.fit(X_train, y_train)
        proba = model.predict_proba(X_test)[:, 1]
        metrics = evaluate_predictions(y_test.to_numpy(), proba, threshold=0.40)
        metrics.update({
            "train_rows": int(len(train)),
            "test_rows": int(len(test)),
            "dataset_version": dataset_version,
            "data_mode": data_mode,
        })
        artifact_path = ARTIFACTS_DIR / f"{model_id}.joblib"
        card_path = CARDS_DIR / f"model_card_{model_id}.md"
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, artifact_path)
        write_model_card(card_path, model_id, algorithm, dataset_version, metrics)
        entry = register_model(
            model_id=model_id,
            algorithm=algorithm,
            artifact_path=artifact_path,
            dataset_version=dataset_version,
            metrics=metrics,
            status="challenger",
            model_card_path=card_path,
            notes=f"trained_from_{data_mode}_model_ready_dataset",
        )
        results.append(entry)

    append_experiment_history([{
        "model_id": r["model_id"],
        "algorithm": r["algorithm"],
        "dataset_version": r["dataset_version"],
        "status": r["status"],
        **{f"metric_{k}": v for k, v in r["metrics"].items() if isinstance(v, (int, float, str)) or v is None},
    } for r in results])
    return results


def compare_registered_models() -> pd.DataFrame:
    registry = load_model_registry()
    rows = []
    for m in registry.get("models", []):
        metrics = m.get("metrics", {})
        rows.append({
            "model_id": m.get("model_id"),
            "algorithm": m.get("algorithm"),
            "status": m.get("status"),
            "dataset_version": m.get("dataset_version"),
            "roc_auc": metrics.get("roc_auc"),
            "average_precision": metrics.get("average_precision"),
            "precision": metrics.get("precision"),
            "recall": metrics.get("recall"),
            "f1": metrics.get("f1"),
            "top_decile_lift": metrics.get("top_decile_lift"),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df["promotion_score"] = (
            df["roc_auc"].fillna(0) * 0.30
            + df["average_precision"].fillna(0) * 0.20
            + df["recall"].fillna(0) * 0.20
            + df["f1"].fillna(0) * 0.10
            + df["top_decile_lift"].fillna(0).clip(upper=3) / 3 * 0.20
        )
        df = df.sort_values("promotion_score", ascending=False).reset_index(drop=True)
    return df


def select_best_challenger(min_recall: float = 0.50) -> dict | None:
    df = compare_registered_models()
    if df.empty:
        return None
    candidates = df[(df["status"] != "champion") & (df["recall"].fillna(0) >= min_recall)]
    if candidates.empty:
        return None
    best_id = candidates.iloc[0]["model_id"]
    return get_model(best_id)
