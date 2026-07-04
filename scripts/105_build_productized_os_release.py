from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mlu.productized_commercial_intelligence_os import run_productized_os_release

if __name__ == "__main__":
    result = run_productized_os_release()
    print(result)
