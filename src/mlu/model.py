from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .features import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    BOOLEAN_FEATURES,
    FEATURE_COLUMNS,
    build_feature_table,
    build_target,
)
from .config import MODEL_PATH, FEATURE_COLUMNS_PATH, MODEL_MANIFEST_PATH


def build_model_pipeline(random_state: int = 42) -> Pipeline:
    numeric_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    boolean_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, NUMERIC_FEATURES),
            ("cat", categorical_pipeline, CATEGORICAL_FEATURES),
            ("bool", boolean_pipeline, BOOLEAN_FEATURES),
        ]
    )

    classifier = RandomForestClassifier(
        n_estimators=250,
        max_depth=8,
        min_samples_leaf=20,
        class_weight="balanced",
        random_state=random_state,
    )

    return Pipeline(steps=[("preprocessor", preprocessor), ("model", classifier)])


def train_riesgo_caida_model(df: pd.DataFrame, random_state: int = 42) -> dict:
    X = build_feature_table(df)
    y = build_target(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=random_state,
        stratify=y,
    )

    model = build_model_pipeline(random_state=random_state)
    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.50).astype(int)

    metrics = {
        "roc_auc": float(roc_auc_score(y_test, proba)),
        "classification_report": classification_report(y_test, pred, output_dict=True),
        "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "target_rate": float(y.mean()),
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    FEATURE_COLUMNS_PATH.write_text(json.dumps(FEATURE_COLUMNS, indent=2, ensure_ascii=False), encoding="utf-8")
    MODEL_MANIFEST_PATH.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    return {"model": model, "metrics": metrics, "X_test": X_test, "y_test": y_test, "proba": proba}


def load_model(path: Path = MODEL_PATH) -> Pipeline:
    if not path.exists():
        raise FileNotFoundError(f"No existe modelo entrenado en {path}. Ejecuta scripts/02_train_model.py")
    return joblib.load(path)


def predict_riesgo(model: Pipeline, rows: pd.DataFrame) -> pd.DataFrame:
    X = build_feature_table(rows)
    proba = model.predict_proba(X)[:, 1]
    out = rows.copy()
    out["riesgo_caida"] = proba
    out["nivel_riesgo"] = pd.cut(
        out["riesgo_caida"],
        bins=[-0.01, 0.40, 0.70, 1.01],
        labels=["bajo", "medio", "alto"],
    ).astype(str)
    return out
