from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mlu.core_value_hardening import build_model_baseline_lift_review


def main() -> None:
    # Yo genero el reporte que evita sobreprometer el modelo.
    result = build_model_baseline_lift_review()
    print(result)


if __name__ == "__main__":
    main()
