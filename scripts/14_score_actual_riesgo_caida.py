from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import joblib
import pandas as pd

from src.mlu.official_rules import FEATURE_COLUMNS
from src.mlu.leakage import assert_no_forbidden_columns

DEFAULT_INPUT = Path("data/processed/gold/riesgo_caida_scoring_actual.parquet")
DEFAULT_MODEL = Path("models/riesgo_caida_model.joblib")
DEFAULT_OUT_PARQUET = Path("data/processed/scoring/ranking_operaciones_riesgo_caida.parquet")
DEFAULT_OUT_CSV = Path("data/processed/scoring/ranking_operaciones_riesgo_caida.csv")
DEFAULT_REPORT = Path("reports/scoring/scoring_report.json")


def risk_level(score: float) -> str:
    if score >= 0.70:
        return "alto"
    if score >= 0.40:
        return "medio"
    return "bajo"


def decision(score: float) -> str:
    if score >= 0.70:
        return "Escalar a gerente comercial y contactar hoy."
    if score >= 0.40:
        return "Priorizar seguimiento del asesor en 24 horas."
    return "Seguimiento comercial estándar."


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera ranking actual de riesgo de caída.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--model", default=str(DEFAULT_MODEL))
    parser.add_argument("--out-parquet", default=str(DEFAULT_OUT_PARQUET))
    parser.add_argument("--out-csv", default=str(DEFAULT_OUT_CSV))
    args = parser.parse_args()

    input_path = Path(args.input)
    model_path = Path(args.model)
    if not input_path.exists():
        raise FileNotFoundError(f"No existe scoring actual: {input_path}")
    if not model_path.exists():
        raise FileNotFoundError(f"No existe modelo: {model_path}")

    df = pd.read_parquet(input_path)
    assert_no_forbidden_columns(df, context="scoring_actual_input")
    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            df[col] = False if col == "tiene_cuota_inicial" else 0
    X = df[FEATURE_COLUMNS].copy()
    X["tiene_cuota_inicial"] = X["tiene_cuota_inicial"].astype(bool).astype(int)
    assert_no_forbidden_columns(X, context="scoring_X")
    model = joblib.load(model_path)
    scores = model.predict_proba(X)[:, 1]
    out = df.copy()
    out["riesgo_caida"] = scores
    out["nivel_riesgo"] = out["riesgo_caida"].map(risk_level)
    out["decision_recomendada"] = out["riesgo_caida"].map(decision)
    out["responsable"] = out.get("asesor", "asesor")
    out["valor_esperado_en_riesgo"] = (out["riesgo_caida"] * out["precio_departamento"].fillna(0) * 0.15).round(2)
    out = out.sort_values(["valor_esperado_en_riesgo", "riesgo_caida"], ascending=False)
    out["ranking_prioridad"] = range(1, len(out) + 1)

    out_parquet = Path(args.out_parquet)
    out_csv = Path(args.out_csv)
    out_parquet.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(out_parquet, index=False)
    out.to_csv(out_csv, index=False, encoding="utf-8-sig")

    report = {
        "rows": int(len(out)),
        "riesgo_promedio": float(out["riesgo_caida"].mean()),
        "valor_esperado_en_riesgo_total": float(out["valor_esperado_en_riesgo"].sum()),
        "output_parquet": str(out_parquet),
        "output_csv": str(out_csv),
    }
    DEFAULT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
