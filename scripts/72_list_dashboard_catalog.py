from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.dashboard_control import load_dashboard_catalog


def main() -> None:
    """
    Yo listo los dashboards disponibles para revisar rápidamente la fábrica de decisión.
    """
    catalog = load_dashboard_catalog()
    for item in catalog.get("dashboards", []):
        print(f"{item['number']:02d} | {item['id']} | {item['name']} | {item['priority']} | {item['params_ref']}")


if __name__ == "__main__":
    main()
