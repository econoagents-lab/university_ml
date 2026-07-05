"""
Yo ejecuto el plan CORE_ANALYTICS_30D_PLAN_v1.

Este runner no sube datos privados. Lee la carpeta indicada por --private-data-dir
o por MLU_PRIVATE_DATA_DIR y prepara la estructura de salidas core.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import json
import datetime


def resolve_private_data_dir(cli_value: str | None) -> Path:
    """
    Yo resuelvo dónde están los parquets privados del CRM.
    """
    raw = cli_value or os.getenv("MLU_PRIVATE_DATA_DIR") or r"C:\Repos\freelance\ml_university_ready\data\raw\sperant"
    return Path(raw)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-data-dir", default=None)
    args = parser.parse_args()

    private_dir = resolve_private_data_dir(args.private_data_dir)
    reports = Path("reports/core_analytics_30d")
    reports.mkdir(parents=True, exist_ok=True)

    manifest = {
        "run_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "private_data_dir": str(private_dir),
        "private_dir_exists": private_dir.exists(),
        "status": "ready_for_core_build" if private_dir.exists() else "private_dir_not_found",
        "next_steps": [
            "build_core_marts",
            "build_cohorts",
            "build_stock_cobranza",
            "recalibrate_model",
            "capture_feedback",
            "generate_ceo_brief",
        ],
    }

    (reports / "core_analytics_30d_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
