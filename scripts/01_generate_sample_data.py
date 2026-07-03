from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mlu.config import SAMPLE_DATA_PATH, NEW_CASES_PATH
from src.mlu.data_generator import save_sample_data

if __name__ == "__main__":
    save_sample_data(SAMPLE_DATA_PATH, NEW_CASES_PATH, n_rows=3000, seed=42)
    print(f"OK: data sintética generada en {SAMPLE_DATA_PATH}")
    print(f"OK: casos nuevos generados en {NEW_CASES_PATH}")
