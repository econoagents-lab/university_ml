from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mlu.core_value_hardening import validate_no_forbidden_public_content


def main() -> None:
    # Yo bloqueo salidas públicas que filtren campos sensibles.
    result = validate_no_forbidden_public_content()
    print(result)
    if result.get("status") != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
