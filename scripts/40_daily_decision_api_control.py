from __future__ import annotations

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

import json
from pathlib import Path

from src.mlu.decision_dashboard import (
    build_dashboard_payload,
    build_decision_queue,
    generate_dashboard_figures,
    generate_dashboard_html,
    generate_executive_brief,
    save_decision_artifacts,
)


def main() -> None:
    queue = build_decision_queue()
    payload = build_dashboard_payload(queue)
    artifacts = save_decision_artifacts(queue, payload)
    html = generate_dashboard_html(payload)
    brief = generate_executive_brief(payload)
    figures = generate_dashboard_figures(queue)
    report = {
        "status": "ok",
        "step": "daily_decision_api_control",
        "queue_rows": int(len(queue)),
        "artifacts": artifacts,
        "html": str(html),
        "brief": str(brief),
        "figures": figures,
        "decision": "usar cola P0/P1 como control diario, registrar feedback y monitorear drift",
    }
    out = Path("reports/dashboard/daily_decision_api_control_report.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
