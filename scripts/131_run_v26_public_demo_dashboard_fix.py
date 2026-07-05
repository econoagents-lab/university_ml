from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import subprocess
import sys

from src.mlu.public_peru_demo import run_public_peru_demo_build
from src.mlu.dashboard_generator import generate_dashboards_from_catalog


def main() -> None:
    """
    Yo ejecuto el hotfix online: landing pública Perú + links reales de dashboards generados.
    """
    print("[v2.6] Generando landing pública Perú...")
    print(run_public_peru_demo_build())
    print("[v2.6] Regenerando dashboards del catálogo...")
    manifest = generate_dashboards_from_catalog()
    print({"dashboards": manifest.get("total_generated"), "generated_at": manifest.get("generated_at")})
    print("[v2.6] Validando rutas FastAPI...")
    subprocess.check_call([sys.executable, "scripts/130_validate_dashboard_static_routes.py"])


if __name__ == "__main__":
    main()
