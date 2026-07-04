from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.dashboard_generator import generate_dashboards_from_catalog

if __name__ == "__main__":
    manifest = generate_dashboards_from_catalog()
    print(f"Dashboards generados: {manifest['total_generated']}")
    print("Índice: reports/generated_dashboards/index.html")
