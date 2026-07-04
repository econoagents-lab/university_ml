from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.dashboard_metrics_engine import build_family_metrics
from src.mlu.dashboard_generator import generate_dashboards_from_catalog, validate_generated_dashboards

if __name__ == "__main__":
    build_family_metrics()
    manifest = generate_dashboards_from_catalog()
    validation = validate_generated_dashboards()
    print(f"Dashboards enriquecidos: {manifest['total_generated']}")
    print(f"Validación dashboards: {validation['status']}")
    if validation["status"] != "ok":
        raise SystemExit(1)
