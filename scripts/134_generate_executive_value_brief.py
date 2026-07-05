from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mlu.core_value_hardening import build_executive_value_brief


def main() -> None:
    # Yo concentro la demo en una página ejecutiva de valor.
    manifest = build_executive_value_brief()
    print(manifest["outputs"])


if __name__ == "__main__":
    main()
