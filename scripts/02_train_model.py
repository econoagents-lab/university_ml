from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mlu.data_loader import load_operations
from src.mlu.model import train_riesgo_caida_model
from src.mlu.reporting import write_markdown_report
from src.mlu.config import MODELS_DIR

if __name__ == "__main__":
    df = load_operations()
    result = train_riesgo_caida_model(df)
    metrics = result["metrics"]
    write_markdown_report(
        MODELS_DIR / "model_card.md",
        "Model Card · Riesgo de Caída v0.1",
        {
            "Objetivo": "Predecir probabilidad de caída a 30 días en separaciones inmobiliarias.",
            "Decisión económica": "Priorizar seguimiento comercial para proteger ventas en riesgo.",
            "Datos": "Dataset sintético seguro con estructura comercial inmobiliaria.",
            "Features": "Proyecto, asesor, medio, canal, dormitorios, precio, días en tubería, cuota inicial, cambios, interacciones, descuento.",
            "Métrica principal": f"ROC AUC: {metrics['roc_auc']:.3f}",
            "Riesgos": "Dataset sintético. En datos reales validar drift, sesgo por asesor, leakage y consistencia de contratos.",
            "Uso recomendado": "No automatizar castigos comerciales. Usar como priorizador de seguimiento y aprendizaje operativo.",
        },
    )
    print("OK: modelo entrenado")
    print(f"ROC AUC: {metrics['roc_auc']:.3f}")
