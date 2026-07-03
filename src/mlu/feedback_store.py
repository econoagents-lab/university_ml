from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from src.mlu.config import PROJECT_ROOT
from src.mlu.feedback import FEEDBACK_COLUMNS, validate_feedback_log

FEEDBACK_STORE_DIR = PROJECT_ROOT / "data" / "feedback"
FEEDBACK_API_CSV = FEEDBACK_STORE_DIR / "feedback_log_api.csv"
FEEDBACK_API_PARQUET = FEEDBACK_STORE_DIR / "feedback_log_api.parquet"
FEEDBACK_STORE_MANIFEST = FEEDBACK_STORE_DIR / "feedback_store_manifest.json"


def feedback_store_mode() -> str:
    """MVP is local-first. Postgres/Supabase is contract-ready via SQL and env vars."""
    if os.getenv("MLU_FEEDBACK_DATABASE_URL"):
        return "postgres_configured_local_write_default"
    if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        return "supabase_configured_local_write_default"
    return "local_files"


def normalize_feedback_payload(payload: dict[str, Any]) -> dict[str, Any]:
    row = {col: payload.get(col, "") for col in FEEDBACK_COLUMNS}
    row["ingested_at"] = datetime.now().isoformat(timespec="seconds")
    row["feedback_source"] = payload.get("feedback_source", "api")
    return row


def append_feedback_record(payload: dict[str, Any]) -> dict[str, Any]:
    FEEDBACK_STORE_DIR.mkdir(parents=True, exist_ok=True)
    row = normalize_feedback_payload(payload)
    df_new = pd.DataFrame([{col: row.get(col, "") for col in FEEDBACK_COLUMNS}])
    validation = validate_feedback_log(df_new)
    if not validation["is_valid"]:
        raise ValueError(f"Feedback inválido: {validation}")

    if FEEDBACK_API_CSV.exists():
        df_old = pd.read_csv(FEEDBACK_API_CSV)
        df_out = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_out = df_new
    df_out.to_csv(FEEDBACK_API_CSV, index=False, encoding="utf-8-sig")
    try:
        df_out.to_parquet(FEEDBACK_API_PARQUET, index=False)
    except Exception:
        pass

    manifest = {
        "store_mode": feedback_store_mode(),
        "rows": int(len(df_out)),
        "csv_path": str(FEEDBACK_API_CSV),
        "parquet_path": str(FEEDBACK_API_PARQUET),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "note": "v1.0 escribe local-first. Supabase/Postgres queda habilitable con SQL y variables de entorno.",
    }
    FEEDBACK_STORE_MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"status": "ok", "output_path": str(FEEDBACK_API_CSV), "rows_written": int(len(df_out)), "store_mode": manifest["store_mode"]}


def feedback_store_schema() -> dict[str, Any]:
    return {
        "columns": FEEDBACK_COLUMNS,
        "local_csv": str(FEEDBACK_API_CSV),
        "local_parquet": str(FEEDBACK_API_PARQUET),
        "store_mode": feedback_store_mode(),
        "sql_path": str(PROJECT_ROOT / "sql" / "production_feedback_store_schema.sql"),
    }
