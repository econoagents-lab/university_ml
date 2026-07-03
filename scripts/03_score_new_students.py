from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pathlib import Path
from src.mlu.data_loader import load_new_cases
from src.mlu.model import load_model, predict_riesgo

if __name__ == "__main__":
    model = load_model()
    df = load_new_cases()
    scored = predict_riesgo(model, df)
    out = Path("data/processed/scoring_output.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    scored.to_csv(out, index=False)
    print(f"OK: predicciones guardadas en {out}")
