from __future__ import annotations

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.mlu.decision_dashboard import generate_dashboard_html, generate_executive_brief, load_dashboard_payload


def main() -> None:
    payload = load_dashboard_payload()
    html_path = generate_dashboard_html(payload)
    brief_path = generate_executive_brief(payload)
    print(f"Dashboard HTML generado: {html_path}")
    print(f"Brief ejecutivo generado: {brief_path}")


if __name__ == "__main__":
    main()
