from __future__ import annotations

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STEPS = [
    "29_register_dataset_version.py",
    "30_train_challenger_models.py",
    "31_compare_champion_vs_challengers.py",
    "32_promote_champion_model.py",
    "33_retraining_policy_check.py",
    "34_generate_congress_figures.py",
    "35_build_registry_metadata.py",
]


def run(script: str) -> dict:
    proc = subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT, capture_output=True, text=True)
    return {"script": script, "returncode": proc.returncode, "stdout": proc.stdout[-1200:], "stderr": proc.stderr[-1200:]}


def main() -> None:
    rows = [run(s) for s in STEPS]
    failed = [r for r in rows if r["returncode"] != 0]
    for r in rows:
        status = "OK" if r["returncode"] == 0 else "FAIL"
        print(f"[{status}] {r['script']}")
        if r["returncode"] != 0:
            print(r["stderr"])
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
