from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.dashboard_metrics_engine import build_family_metrics, validate_dashboard_metrics
from src.mlu.dashboard_generator import generate_dashboards_from_catalog, validate_generated_dashboards

if __name__ == "__main__":
    metrics = build_family_metrics()
    metrics_validation = validate_dashboard_metrics()
    manifest = generate_dashboards_from_catalog()
    dashboard_validation = validate_generated_dashboards()
    print(f"Familias métricas: {len(metrics['families'])}")
    print(f"Validación métricas: {metrics_validation['status']}")
    print(f"Dashboards generados/enriquecidos: {manifest['total_generated']}")
    print(f"Validación dashboards: {dashboard_validation['status']}")
    if metrics_validation["status"] != "ok" or dashboard_validation["status"] != "ok":
        raise SystemExit(1)
