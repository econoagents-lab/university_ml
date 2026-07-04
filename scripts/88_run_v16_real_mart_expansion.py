from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.real_marts import build_all_real_marts, validate_no_pii_in_marts
from src.mlu.dashboard_metrics_engine import build_family_metrics, validate_dashboard_metrics
from src.mlu.dashboard_generator import generate_dashboards_from_catalog, validate_generated_dashboards

if __name__ == "__main__":
    manifest = build_all_real_marts()
    real_validation = validate_no_pii_in_marts()
    metrics = build_family_metrics()
    metrics_validation = validate_dashboard_metrics()
    dashboard_manifest = generate_dashboards_from_catalog()
    dashboard_validation = validate_generated_dashboards()
    print(f"Marts reales: {len(manifest['marts'])}")
    print(f"Validación marts reales: {real_validation['status']}")
    print(f"Familias métricas: {len(metrics['families'])}")
    print(f"Validación métricas: {metrics_validation['status']}")
    print(f"Dashboards generados: {dashboard_manifest['total_generated']}")
    print(f"Validación dashboards: {dashboard_validation['status']}")
    if real_validation["status"] != "ok" or metrics_validation["status"] != "ok" or dashboard_validation["status"] != "ok":
        raise SystemExit(1)
