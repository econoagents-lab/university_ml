from __future__ import annotations

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

import json
from pathlib import Path

from src.mlu.decision_dashboard import build_dashboard_payload, load_decision_queue, save_decision_artifacts


def main() -> None:
    queue = load_decision_queue()
    payload = build_dashboard_payload(queue)
    artifacts = save_decision_artifacts(queue, payload)
    out = Path("reports/dashboard/dashboard_data_generation_report.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    report = {"status": "ok", "artifacts": artifacts, "kpis": payload["kpis"]}
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
