from __future__ import annotations

import json
from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.mlu.config import SPERANT_TRAINING_PATH, SAMPLE_DATA_PATH, REPORTS_DIR
from src.mlu.foundations import audit_training_dataset, build_model_matrix


def _adapt_sample_to_foundation_contract(df: pd.DataFrame) -> pd.DataFrame:
    """Adapta la sample data educativa al contrato gold mínimo.

    La sample data fue creada para enseñar ML. Esta adaptación agrega las columnas de
    grano temporal que la capa de fundamentos exige, sin tocar la data real de Sperant.
    """
    out = df.copy()
    if "codigo_proforma" not in out.columns and "id_operacion" in out.columns:
        out["codigo_proforma"] = out["id_operacion"]
    if "fecha_snapshot" not in out.columns and {"fecha_separacion", "dias_en_tuberia"}.issubset(out.columns):
        out["fecha_snapshot"] = (
            pd.to_datetime(out["fecha_separacion"], errors="coerce")
            + pd.to_timedelta(pd.to_numeric(out["dias_en_tuberia"], errors="coerce").fillna(0), unit="D")
        )
    return out


def load_candidate_dataset() -> tuple[str, pd.DataFrame]:
    if SPERANT_TRAINING_PATH.exists():
        return str(SPERANT_TRAINING_PATH), pd.read_parquet(SPERANT_TRAINING_PATH)
    if SAMPLE_DATA_PATH.exists():
        return str(SAMPLE_DATA_PATH), _adapt_sample_to_foundation_contract(pd.read_csv(SAMPLE_DATA_PATH))
    raise FileNotFoundError(
        "No encontré tabla gold de Sperant ni sample data. Ejecuta primero la extracción o el generador sample."
    )


def main() -> None:
    dataset_path, df = load_candidate_dataset()
    audit = audit_training_dataset(df)

    # Si está lista, probamos que X se construya sin columnas prohibidas.
    if audit["ready_for_training"]:
        x = build_model_matrix(df)
        audit["model_matrix_columns"] = list(x.columns)
        audit["model_matrix_rows"] = int(len(x))
    else:
        audit["model_matrix_columns"] = []
        audit["model_matrix_rows"] = 0

    audit["dataset_path"] = dataset_path

    out_dir = REPORTS_DIR / "foundations"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "foundation_audit_riesgo_caida.json"
    out_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(audit, indent=2, ensure_ascii=False))
    print(f"\nAuditoría guardada en: {out_path}")


if __name__ == "__main__":
    main()
