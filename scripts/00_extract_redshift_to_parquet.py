from __future__ import annotations

from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import os
import json
from datetime import datetime
from pathlib import Path

from src.mlu.config import RAW_SPERANT_DIR
from src.mlu.redshift_client import RedshiftConfig, extract_many_tables

DEFAULT_TABLES = [
    "proforma_unidad",
    "procesos",
    "datos_extras",
    "unidades",
    "clientes",
    "proyectos",
]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrae tablas Redshift/Sperant a Parquet local.")
    parser.add_argument("--tables", default=os.getenv("REDSHIFT_TABLES", ",".join(DEFAULT_TABLES)))
    parser.add_argument("--output-dir", default=str(RAW_SPERANT_DIR))
    parser.add_argument("--limit", type=int, default=0, help="Límite opcional para pruebas. 0 = sin límite.")
    args = parser.parse_args()

    tables = [t.strip() for t in args.tables.split(",") if t.strip()]
    output_dir = Path(args.output_dir)
    config = RedshiftConfig.from_env()
    paths = extract_many_tables(tables, output_dir, config=config, limit=args.limit or None)
    manifest = {
        "extracted_at": datetime.utcnow().isoformat() + "Z",
        "schema": config.schema,
        "tables": [p.stem for p in paths],
        "output_dir": str(output_dir),
        "note": "No incluye credenciales. No subir data/raw a GitHub.",
    }
    (output_dir / "_extract_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    for path in paths:
        print(f"OK: {path}")
