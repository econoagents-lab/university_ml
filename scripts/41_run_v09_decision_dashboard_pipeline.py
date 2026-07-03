from __future__ import annotations

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

import subprocess
import sys

STEPS = [
    "scripts/14_score_actual_riesgo_caida.py",
    "scripts/37_build_decision_queue.py",
    "scripts/38_generate_decision_dashboard_data.py",
    "scripts/39_generate_decision_dashboard_html.py",
    "scripts/40_daily_decision_api_control.py",
]


def main() -> None:
    for step in STEPS:
        print(f"\n=== Ejecutando {step} ===")
        subprocess.run([sys.executable, step], check=True)
    print("\nOK v0.9 decision dashboard pipeline completado.")


if __name__ == "__main__":
    main()
