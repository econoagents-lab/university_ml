from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.dashboard_control import generate_control_panel


def main() -> None:
    """
    Yo genero el panel maestro de dashboards con la columna Donde cambiar.
    """
    path = generate_control_panel()
    print(f"Dashboard control panel generado: {path}")


if __name__ == "__main__":
    main()
