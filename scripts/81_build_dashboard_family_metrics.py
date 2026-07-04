from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.dashboard_metrics_engine import build_family_metrics, validate_dashboard_metrics

if __name__ == "__main__":
    bundle = build_family_metrics()
    validation = validate_dashboard_metrics()
    print(f"Familias con métricas: {len(bundle['families'])}")
    print(f"Validación métricas: {validation['status']}")
    if validation["status"] != "ok":
        raise SystemExit(1)
