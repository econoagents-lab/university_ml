from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.dashboard_control import generate_control_panel, validate_dashboard_catalog, validate_recommended_decisions


def main() -> None:
    """
    Yo ejecuto el paquete v1.3: valido parámetros y genero reportes de control.
    """
    validation = validate_dashboard_catalog()
    decisions = validate_recommended_decisions()
    panel = generate_control_panel()
    print(f"Catalog status: {validation['status']}")
    print(f"Recommended decisions status: {decisions['status']}")
    print(f"Control panel: {panel}")
    if validation["status"] != "ok" or decisions["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
