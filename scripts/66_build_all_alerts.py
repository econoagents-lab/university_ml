from __future__ import annotations

from pathlib import Path
import argparse
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ALERTS_DIR = ROOT / "reports" / "alerts"


def run_step(name: str, command: list[str]) -> dict:
    """Yo ejecuto cada alerta sin detener toda la bitácora si una pieza falla."""
    print(f"[INFO] {name}: {' '.join(command)}")
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    status = "ok" if result.returncode == 0 else "fail"
    return {
        "name": name,
        "status": status,
        "returncode": result.returncode,
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fail-on-critical", action="store_true")
    args = parser.parse_args()
    ALERTS_DIR.mkdir(parents=True, exist_ok=True)
    python = sys.executable
    steps = [
        ("commercial_digest", [python, "scripts/61_build_commercial_alert_digest.py"]),
        ("ragas_gate", [python, "scripts/63_validate_ragas_quality_gate.py"]),
        ("uni_readiness", [python, "scripts/62_validate_uni_readiness.py"]),
        ("issue_body", [python, "scripts/64_create_alert_issue_body.py"]),
    ]
    manifest = [run_step(name, command) for name, command in steps]
    (ALERTS_DIR / "alerts_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Intelligence Factory Alerts Manifest", ""]
    for item in manifest:
        icon = "✅" if item["status"] == "ok" else "🚨"
        lines.append(f"- {icon} **{item['name']}**: {item['status']}")
    (ALERTS_DIR / "ALERTS_MANIFEST.md").write_text("\n".join(lines), encoding="utf-8")
    if args.fail_on_critical and any(item["status"] == "fail" for item in manifest):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
