from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.dashboard_metrics_engine import validate_dashboard_metrics

if __name__ == "__main__":
    validation = validate_dashboard_metrics()
    print(validation)
    if validation["status"] != "ok":
        raise SystemExit(1)
