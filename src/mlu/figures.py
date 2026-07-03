from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, PrecisionRecallDisplay, RocCurveDisplay, confusion_matrix, precision_recall_curve, roc_curve

from .config import PROJECT_ROOT
from .official_rules import FEATURE_COLUMNS, TARGET
from .comparison import compare_registered_models, temporal_train_test_split

FIG_DIR = PROJECT_ROOT / "reports" / "figures" / "congress"
EXEC_FIG_DIR = PROJECT_ROOT / "reports" / "figures" / "executive"
MODEL_READY_PATH = PROJECT_ROOT / "data" / "processed" / "gold" / "riesgo_caida_training_model_ready.parquet"
MODEL_PATH = PROJECT_ROOT / "models" / "riesgo_caida_model.joblib"


def _save(fig, filename: str) -> str:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    EXEC_FIG_DIR.mkdir(parents=True, exist_ok=True)
    png_path = FIG_DIR / filename
    svg_path = png_path.with_suffix(".svg")
    fig.tight_layout()
    fig.savefig(png_path, dpi=160, bbox_inches="tight")
    fig.savefig(svg_path, bbox_inches="tight")
    # Copy a smaller executive version as PNG only.
    fig.savefig(EXEC_FIG_DIR / filename, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return str(png_path.relative_to(PROJECT_ROOT))


def _load_model_ready() -> pd.DataFrame:
    if MODEL_READY_PATH.exists():
        return pd.read_parquet(MODEL_READY_PATH)
    fallback = PROJECT_ROOT / "data" / "processed" / "gold" / "riesgo_caida_training.parquet"
    if fallback.exists():
        df = pd.read_parquet(fallback)
        cols = [c for c in df.columns if c in FEATURE_COLUMNS + [TARGET, "fecha_snapshot", "codigo_proforma", "codigo_unidad"]]
        return df[cols].copy()
    raise FileNotFoundError("No existe dataset model-ready ni fallback gold.")


def _score_test(df: pd.DataFrame):
    train, test = temporal_train_test_split(df)
    if MODEL_PATH.exists():
        model = joblib.load(MODEL_PATH)
        X_test = test[FEATURE_COLUMNS].copy()
        if "tiene_cuota_inicial" in X_test.columns:
            X_test["tiene_cuota_inicial"] = X_test["tiene_cuota_inicial"].astype(bool).astype(int)
        proba = model.predict_proba(X_test)[:, 1]
    else:
        proba = np.full(len(test), float(train[TARGET].mean()))
    return test[TARGET].astype(int).to_numpy(), np.asarray(proba), train, test


def generate_problem_funnel(df: pd.DataFrame) -> str:
    total = len(df)
    caidas = int(df[TARGET].sum())
    no_caidas = total - caidas
    stages = ["Separaciones\nhistóricas", "No caída\n30d", "Caída\n30d"]
    values = [total, no_caidas, caidas]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(stages, values)
    ax.set_title("Funnel del problema: riesgo de caída comercial")
    ax.set_ylabel("Operaciones")
    for i, v in enumerate(values):
        ax.text(i, v, f"{v:,}", ha="center", va="bottom")
    ax.text(0.5, -0.18, "Pregunta: ¿qué operaciones activas deben priorizar seguimiento antes de caer?", transform=ax.transAxes, ha="center")
    return _save(fig, "01_problem_funnel.png")


def generate_target_distribution(df: pd.DataFrame) -> str:
    counts = df[TARGET].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(["No cae", "Cae 30d"], [counts.get(0, 0), counts.get(1, 0)])
    ax.set_title("Distribución del target: evento minoritario")
    ax.set_ylabel("Operaciones")
    rate = df[TARGET].mean()
    ax.text(0.5, -0.18, f"Tasa histórica de caída: {rate:.2%}. Accuracy no debe ser la métrica reina.", transform=ax.transAxes, ha="center")
    return _save(fig, "02_target_distribution.png")


def generate_temporal_split(df: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if "fecha_snapshot" in df.columns:
        tmp = df.copy()
        tmp["fecha_snapshot"] = pd.to_datetime(tmp["fecha_snapshot"], errors="coerce")
        by_month = tmp.dropna(subset=["fecha_snapshot"]).groupby(tmp["fecha_snapshot"].dt.to_period("M")).size()
        if not by_month.empty:
            x = by_month.index.astype(str)
            y = by_month.values
            split = int(len(x) * 0.75)
            ax.plot(x, y, marker="o")
            ax.axvline(max(split - 0.5, 0), linestyle="--")
            ax.set_xticklabels(x, rotation=45, ha="right")
            ax.set_title("Split temporal: entrenamiento antes, prueba después")
            ax.set_ylabel("Operaciones por mes")
        else:
            ax.text(0.5, 0.5, "fecha_snapshot sin valores válidos", ha="center", va="center")
    else:
        ax.text(0.5, 0.5, "Dataset sin fecha_snapshot; usar split temporal en producción", ha="center", va="center")
    ax.text(0.5, -0.25, "Mensaje: el modelo no debe aprender del futuro.", transform=ax.transAxes, ha="center")
    return _save(fig, "03_temporal_split.png")


def generate_anti_leakage_architecture() -> str:
    steps = ["Raw CRM", "Gold audit", "Target build", "Model-ready", "Feature table", "X / API"]
    notes = ["puede traer fecha_caida", "auditable", "caida_30d", "sin columnas futuras", "solo features permitidas", "modelo/scoring"]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.axis("off")
    xs = np.linspace(0.08, 0.92, len(steps))
    for i, (x, step, note) in enumerate(zip(xs, steps, notes)):
        ax.text(x, 0.62, step, ha="center", va="center", bbox=dict(boxstyle="round,pad=0.35", fill=False))
        ax.text(x, 0.42, note, ha="center", va="center", fontsize=9)
        if i < len(steps) - 1:
            ax.annotate("", xy=(xs[i+1]-0.055, 0.62), xytext=(x+0.055, 0.62), arrowprops=dict(arrowstyle="->"))
    ax.set_title("Arquitectura anti-leakage: el futuro no entra al modelo")
    ax.text(0.5, 0.12, "fecha_caida puede existir para auditoría/target; nunca en X, model_matrix ni scoring.", ha="center")
    return _save(fig, "04_anti_leakage_architecture.png")


def generate_roc_curve(y_true, proba) -> str:
    fig, ax = plt.subplots(figsize=(6.8, 5))
    RocCurveDisplay.from_predictions(y_true, proba, ax=ax)
    ax.set_title("ROC Curve - Riesgo de caída")
    return _save(fig, "05_roc_curve.png")


def generate_pr_curve(y_true, proba) -> str:
    fig, ax = plt.subplots(figsize=(6.8, 5))
    PrecisionRecallDisplay.from_predictions(y_true, proba, ax=ax)
    ax.set_title("Precision-Recall Curve - evento minoritario")
    return _save(fig, "06_pr_curve.png")


def generate_confusion_matrix(y_true, proba, threshold: float = 0.40) -> str:
    pred = (proba >= threshold).astype(int)
    cm = confusion_matrix(y_true, pred, labels=[0, 1])
    fig, ax = plt.subplots(figsize=(6.2, 5))
    ConfusionMatrixDisplay(cm, display_labels=["No cae", "Cae"]).plot(ax=ax, values_format="d")
    ax.set_title(f"Confusion Matrix - threshold negocio {threshold:.2f}")
    return _save(fig, "07_confusion_matrix.png")


def generate_lift_deciles(y_true, proba) -> str:
    tmp = pd.DataFrame({"y": y_true, "score": proba}).sort_values("score", ascending=False).reset_index(drop=True)
    tmp["decile"] = pd.qcut(tmp.index + 1, 10, labels=False, duplicates="drop") + 1
    lift = tmp.groupby("decile")["y"].mean().reset_index(name="event_rate")
    base = tmp["y"].mean()
    lift["lift"] = lift["event_rate"] / base if base else 0
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(lift["decile"].astype(str), lift["lift"])
    ax.axhline(1.0, linestyle="--")
    ax.set_title("Lift por deciles: capacidad de priorización")
    ax.set_xlabel("Decil de score: 1 = mayor riesgo")
    ax.set_ylabel("Lift vs tasa base")
    return _save(fig, "08_lift_deciles.png")


def generate_calibration_curve() -> str:
    table_path = PROJECT_ROOT / "reports" / "monitoring" / "calibration_table.csv"
    fig, ax = plt.subplots(figsize=(6.8, 5))
    if table_path.exists():
        cal = pd.read_csv(table_path)
        xcol = "mean_score" if "mean_score" in cal.columns else cal.columns[0]
        ycol = "event_rate" if "event_rate" in cal.columns else cal.columns[-1]
        ax.plot(cal[xcol], cal[ycol], marker="o")
    else:
        ax.text(0.5, 0.5, "Ejecutar 24_evaluate_calibration.py para curva real", ha="center", va="center")
    ax.plot([0, 1], [0, 1], linestyle="--")
    ax.set_title("Calibration Curve")
    ax.set_xlabel("Probabilidad predicha")
    ax.set_ylabel("Frecuencia real")
    return _save(fig, "09_calibration_curve.png")


def generate_drift_heatmap() -> str:
    drift_path = PROJECT_ROOT / "reports" / "monitoring" / "feature_drift.csv"
    fig, ax = plt.subplots(figsize=(8, 4.8))
    if drift_path.exists():
        drift = pd.read_csv(drift_path)
        metric_col = "drift_metric" if "drift_metric" in drift.columns else drift.select_dtypes("number").columns[0]
        top = drift.sort_values(metric_col, ascending=False).head(10)
        ax.barh(top["feature"].astype(str), top[metric_col])
        ax.invert_yaxis()
        ax.set_xlabel("Drift metric")
    else:
        ax.text(0.5, 0.5, "Ejecutar 22_monitor_feature_drift.py", ha="center", va="center")
    ax.set_title("Top variables con drift")
    return _save(fig, "10_drift_heatmap.png")


def generate_champion_vs_challenger() -> str:
    comp = compare_registered_models()
    fig, ax = plt.subplots(figsize=(9, 5))
    if not comp.empty:
        metric = "promotion_score" if "promotion_score" in comp.columns else "roc_auc"
        top = comp.head(8).copy()
        ax.barh(top["model_id"].astype(str), top[metric].fillna(0))
        ax.invert_yaxis()
        ax.set_xlabel(metric)
    else:
        ax.text(0.5, 0.5, "Aún no hay challengers registrados", ha="center", va="center")
    ax.set_title("Champion vs Challengers")
    return _save(fig, "11_champion_vs_challenger.png")


def generate_feature_importance() -> str:
    fi_path = PROJECT_ROOT / "reports" / "modeling" / "feature_importance.csv"
    fig, ax = plt.subplots(figsize=(8, 5))
    if fi_path.exists():
        fi = pd.read_csv(fi_path)
        if "feature" in fi.columns:
            val_col = "importance" if "importance" in fi.columns else fi.select_dtypes("number").columns[-1]
            top = fi.sort_values(val_col, ascending=False).head(10)
            ax.barh(top["feature"].astype(str), top[val_col])
            ax.invert_yaxis()
        else:
            ax.text(0.5, 0.5, "feature_importance.csv sin columna feature", ha="center", va="center")
    else:
        ax.barh(FEATURE_COLUMNS[:10], np.linspace(1, 0.2, min(10, len(FEATURE_COLUMNS))))
        ax.invert_yaxis()
        ax.text(0.5, -0.22, "Placeholder pedagógico: reemplazar por permutation/SHAP en congreso final.", transform=ax.transAxes, ha="center")
    ax.set_title("Importancia de variables")
    return _save(fig, "12_feature_importance.png")


def generate_intervention_effect() -> str:
    effect_path = PROJECT_ROOT / "reports" / "experiments" / "intervention_effect_report.json"
    fig, ax = plt.subplots(figsize=(7, 4.8))
    if effect_path.exists():
        data = json.loads(effect_path.read_text(encoding="utf-8"))
        labels = ["Control", "Intervenido"]
        values = [data.get("control_event_rate", 0), data.get("intervention_event_rate", 0)]
        ax.bar(labels, values)
        ax.set_ylabel("Tasa de caída")
    else:
        ax.bar(["Control", "Intervenido"], [0, 0])
        ax.text(0.5, 0.5, "Aún falta feedback real de intervenciones", ha="center", va="center")
    ax.set_title("Efecto de intervención comercial")
    return _save(fig, "13_intervention_effect.png")


def build_congress_figure_pack() -> dict:
    df = _load_model_ready()
    y_true, proba, train, test = _score_test(df)
    outputs = [
        generate_problem_funnel(df),
        generate_target_distribution(df),
        generate_temporal_split(df),
        generate_anti_leakage_architecture(),
        generate_roc_curve(y_true, proba),
        generate_pr_curve(y_true, proba),
        generate_confusion_matrix(y_true, proba),
        generate_lift_deciles(y_true, proba),
        generate_calibration_curve(),
        generate_drift_heatmap(),
        generate_champion_vs_challenger(),
        generate_feature_importance(),
        generate_intervention_effect(),
    ]
    manifest = {
        "version": "0.8.0-retraining_registry_crm_first_congress_pack",
        "figures": outputs,
        "n_figures": len(outputs),
        "message": "CRM-first congress pack generado desde artifacts model-ready/monitoring/registry.",
    }
    (PROJECT_ROOT / "reports" / "figures" / "congress_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest
