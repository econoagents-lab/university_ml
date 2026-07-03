from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pathlib import Path
import json
from src.mlu.config import MODEL_MANIFEST_PATH, MODELS_DIR
from src.mlu.reporting import write_markdown_report

if __name__ == "__main__":
    metrics = json.loads(MODEL_MANIFEST_PATH.read_text(encoding="utf-8"))
    write_markdown_report(
        MODELS_DIR / "model_card.md",
        "Model Card · Riesgo de Caída v0.1",
        {
            "Objetivo": "Predecir probabilidad de caída a 30 días.",
            "Métrica principal": f"ROC AUC: {metrics['roc_auc']:.3f}",
            "Tamaño entrenamiento": metrics["n_train"],
            "Tamaño prueba": metrics["n_test"],
            "Tasa histórica de caída": f"{metrics['target_rate']:.1%}",
        },
    )
    print("OK: model card regenerada")
