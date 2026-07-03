from __future__ import annotations

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

import json
from pathlib import Path

import yaml

from src.mlu.retraining import evaluate_retraining_policy


def main() -> None:
    policy_path = Path("contracts/retraining_policy.yml")
    policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))["triggers"] if policy_path.exists() else None
    result = evaluate_retraining_policy(policy=policy)
    out_dir = Path("reports/registry")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "retraining_policy_decision.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    md = "# Retraining Policy Decision\n\n"
    md += f"Estado: **{result['status']}**\n\n"
    md += "## Razones\n\n"
    if result["reasons"]:
        for r in result["reasons"]:
            md += f"- {r}\n"
    else:
        md += "- Sin disparadores activos.\n"
    md += f"\nPromover challenger: {result['should_promote_challenger']}\n"
    md += f"\nCandidato: {result['promotion_candidate']}\n"
    (out_dir / "retraining_decision_report.md").write_text(md, encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
