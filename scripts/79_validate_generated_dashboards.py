from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.dashboard_generator import validate_generated_dashboards

if __name__ == "__main__":
    report = validate_generated_dashboards()
    print(report)
    if report["status"] != "ok":
        raise SystemExit(1)
