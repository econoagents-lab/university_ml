from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import sys
from src.mlu.productized_commercial_intelligence_os import validate_productized_os

if __name__ == "__main__":
    result = validate_productized_os()
    print(result)
    sys.exit(1 if result.get("status") == "fail" else 0)
