from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mlu.production import build_production_readiness


def main():
    report = build_production_readiness()
    print(report)
    if report["checks_ok"] < max(1, report["checks_total"] - 1):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
