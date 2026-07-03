from __future__ import annotations

from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pathlib import Path

from src.mlu.config import SPERANT_TRAINING_PATH, MODELS_DIR
from src.mlu.data_loader import load_operations
from src.mlu.model import train_riesgo_caida_model
from src.mlu.reporting import write_markdown_report


if __name__ == "__main__":
    if not SPERANT_TRAINING_PATH.exists():
        raise SystemExit(
            "No existe data/processed/gold/riesgo_caida_training.parquet. "
            "Ejecuta primero scripts/10_build_sperant_training_dataset.py"
        )
    df = load_operations(SPERANT_TRAINING_PATH)
    result = train_riesgo_caida_model(df)
    metrics = result["metrics"]
    write_markdown_report(
        MODELS_DIR / "model_card.md",
        "Model Card · Riesgo de Caída v0.2 · Sperant/Redshift",
        {
            "Objetivo": "Priorizar operaciones inmobiliarias con riesgo de caída usando historia operacional de Sperant.",
            "Datos": "Gold table generada desde procesos/unidades/proformas exportadas desde Redshift.",
            "Grano": "Operación inmobiliaria observada en snapshots de 7, 14 y 30 días posteriores a separación.",
            "Target": "caida_30d = caída dentro de los 30 días posteriores al snapshot.",
            "Métrica principal": f"ROC AUC: {metrics['roc_auc']:.3f}",
            "Tamaño entrenamiento": metrics["n_train"],
            "Tamaño prueba": metrics["n_test"],
            "Tasa histórica de caída": f"{metrics['target_rate']:.1%}",
            "Decisión económica": "Escalar seguimiento comercial antes de que el valor de venta se pierda.",
            "Limitaciones": "Validar contratos, leakage temporal, sesgo por asesor/proyecto y calidad de fechas antes de usar en comité.",
        },
    )
    print("OK: modelo entrenado con gold table Sperant/Redshift")
    print(f"ROC AUC: {metrics['roc_auc']:.3f}")
