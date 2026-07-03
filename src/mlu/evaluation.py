from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix


def evaluate_classifier(y_true, proba, threshold: float = 0.5) -> dict:
    pred = (np.asarray(proba) >= threshold).astype(int)
    return {
        "threshold": threshold,
        "accuracy": float(accuracy_score(y_true, pred)),
        "precision": float(precision_score(y_true, pred, zero_division=0)),
        "recall": float(recall_score(y_true, pred, zero_division=0)),
        "f1": float(f1_score(y_true, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, proba)),
        "confusion_matrix": confusion_matrix(y_true, pred).tolist(),
    }


def threshold_table(y_true, proba, thresholds=None) -> pd.DataFrame:
    if thresholds is None:
        thresholds = [0.20, 0.30, 0.40, 0.50, 0.60, 0.70]
    return pd.DataFrame([evaluate_classifier(y_true, proba, t) for t in thresholds])
