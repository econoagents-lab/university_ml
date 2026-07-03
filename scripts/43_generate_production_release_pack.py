from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mlu.production import build_release_manifest, build_production_readiness


def main():
    manifest = build_release_manifest()
    readiness = build_production_readiness()
    print({"release": manifest["version"], "readiness": readiness["status"], "checks": f"{readiness['checks_ok']}/{readiness['checks_total']}"})


if __name__ == "__main__":
    main()
