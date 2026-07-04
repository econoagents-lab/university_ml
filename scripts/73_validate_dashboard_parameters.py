from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
from src.mlu.dashboard_control import VALIDATION_REPORT_PATH, validate_dashboard_catalog, validate_recommended_decisions


def main() -> None:
    """
    Yo valido el catálogo y las decisiones recomendadas antes de publicar dashboards.
    """
    report = {
        "catalog": validate_dashboard_catalog(),
        "recommended_decisions": validate_recommended_decisions(),
    }
    VALIDATION_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["catalog"]["status"] != "ok" or report["recommended_decisions"]["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
