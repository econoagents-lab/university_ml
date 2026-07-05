from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mlu.core_value_hardening import run_core_value_hardening


def main() -> None:
    # Yo ejecuto todas las correcciones prioritarias de auditoría v2.7.
    manifest = run_core_value_hardening()
    print("v2.7 core value hardening generado")
    print(manifest.get("outputs"))


if __name__ == "__main__":
    main()
