from __future__ import annotations

from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse
from pathlib import Path

from src.mlu.config import RAW_SPERANT_DIR, METADATA_DIR
from src.mlu.sperant_adapter import profile_sources


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perfila parquets de Sperant sin exponer datos sensibles.")
    parser.add_argument("--input-dir", default=str(RAW_SPERANT_DIR))
    parser.add_argument("--output", default=str(METADATA_DIR / "sperant_table_profile.parquet"))
    args = parser.parse_args()

    profile = profile_sources(Path(args.input_dir), Path(args.output))
    print(profile.to_string(index=False))
    print(f"OK: perfil guardado en {args.output}")
