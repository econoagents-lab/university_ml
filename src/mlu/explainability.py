from __future__ import annotations

import pandas as pd


def get_feature_importance(model) -> pd.DataFrame:
    """Extrae importancia de variables para modelos con feature_importances_.

    En producción se puede reemplazar por SHAP. Aquí se mantiene simple y legible.
    """
    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["model"]

    try:
        feature_names = preprocessor.get_feature_names_out()
    except Exception:
        feature_names = [f"feature_{i}" for i in range(len(classifier.feature_importances_))]

    return (
        pd.DataFrame({"feature": feature_names, "importance": classifier.feature_importances_})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )
