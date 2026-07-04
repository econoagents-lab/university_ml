from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.dashboard_control import generate_inputs_to_confirm


def main() -> None:
    """
    Yo genero la tabla de inputs críticos y dónde cambiarlos.
    """
    path = generate_inputs_to_confirm()
    print(f"Inputs to confirm generado: {path}")


if __name__ == "__main__":
    main()
