from __future__ import annotations

import subprocess
import sys
from pathlib import Path

STEPS = [
    [sys.executable, "scripts/14_score_actual_riesgo_caida.py"],
    [sys.executable, "scripts/17_evaluate_lift_deciles.py"],
    [sys.executable, "scripts/18_initialize_feedback_loop.py"],
    [sys.executable, "scripts/19_merge_feedback_outcomes.py"],
    [sys.executable, "scripts/20_generate_executive_lift_report.py"],
]


def main() -> None:
    for step in STEPS:
        print(f"[RUN] {' '.join(step)}")
        subprocess.run(step, check=True)
    print("[OK] Control diario de riesgo generado.")


if __name__ == "__main__":
    main()
