from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.real_marts import validate_no_pii_in_marts

if __name__ == "__main__":
    report = validate_no_pii_in_marts()
    print(f"Validación marts reales: {report['status']}")
    for error in report.get("errors", []):
        print(f"ERROR: {error}")
    for warning in report.get("warnings", [])[:10]:
        print(f"WARN: {warning}")
    if report["status"] != "ok":
        raise SystemExit(1)
