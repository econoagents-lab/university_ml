from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
import sys

PROJECT_ROOT_CANDIDATE = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT_CANDIDATE) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT_CANDIDATE))

from typing import Any

import pandas as pd

from src.mlu.config import PROJECT_ROOT
from src.mlu.decision_dashboard import classify_operational_priority

RANKING_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "scoring" / "ranking_operaciones_riesgo_caida.csv"
RANKING_PARQUET_PATH = PROJECT_ROOT / "data" / "processed" / "scoring" / "ranking_operaciones_riesgo_caida.parquet"
PUBLIC_DIR = PROJECT_ROOT / "reports" / "public"
PUBLIC_PAYLOAD_PATH = PUBLIC_DIR / "decision_dashboard_payload_public.json"

ALLOWED_TOP_LEVEL_KEYS = {
    "total_operaciones",
    "valor_total_en_riesgo",
    "riesgo_promedio",
    "p0_p1",
    "top_proyectos",
    "top_asesores",
    "top_canales",
    "fecha_generacion",
    "data_mode",
}

SENSITIVE_KEY_PATTERNS = [
    "cliente",
    "documento",
    "dni",
    "email",
    "correo",
    "teléfono",
    "telefono",
    "phone",
    "celular",
    "nombre_completo",
    "nombre completo",
    "direccion",
    "dirección",
    "address",
    "credencial",
    "credential",
    "password",
    "secret",
    "token",
    "api_key",
]

PERSON_NAME_COLUMN_PATTERNS = [
    "cliente",
    "documento",
    "dni",
    "email",
    "correo",
    "teléfono",
    "telefono",
    "celular",
    "direccion",
    "dirección",
]


def normalize_column_name(column: str) -> str:
    """
    Yo normalizo nombres de columnas para poder encontrar métricas aunque el CSV cambie de versión.
    """
    return str(column).strip().lower().replace(" ", "_")


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """
    Yo busco una columna entre varios alias porque mis outputs pueden evolucionar por versión.
    """
    normalized = {normalize_column_name(column): column for column in df.columns}
    for candidate in candidates:
        key = normalize_column_name(candidate)
        if key in normalized:
            return normalized[key]
    return None


def read_ranking(path: Path | None = None) -> pd.DataFrame:
    """
    Yo cargo el ranking operativo real. Prefiero CSV porque es el output más simple de mover a Railway.
    """
    source = path or (RANKING_CSV_PATH if RANKING_CSV_PATH.exists() else RANKING_PARQUET_PATH)
    if not source.exists():
        raise FileNotFoundError(
            "No encuentro ranking operativo. Ejecuta primero scripts/14_score_actual_riesgo_caida.py "
            "o scripts/41_run_v09_decision_dashboard_pipeline.py."
        )
    if source.suffix.lower() == ".parquet":
        return pd.read_parquet(source)
    return pd.read_csv(source, encoding="utf-8-sig")


def assert_no_sensitive_columns(df: pd.DataFrame) -> None:
    """
    Yo bloqueo columnas sensibles antes de construir un payload público.
    La data personal puede existir en CRM, pero nunca debe viajar a Railway como JSON público.
    """
    violations: list[str] = []
    for column in df.columns:
        column_norm = normalize_column_name(column)
        if any(pattern in column_norm for pattern in PERSON_NAME_COLUMN_PATTERNS):
            violations.append(str(column))
    if violations:
        raise ValueError(f"El ranking contiene columnas sensibles para payload público: {violations}")


def stable_anon_label(value: Any, prefix: str = "Asesor") -> str:
    """
    Yo reemplazo nombres personales por identificadores anónimos estables.
    No necesito saber quién es la persona para presentar concentración comercial.
    """
    raw = str(value).strip() if value is not None else "sin_asesor"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8].upper()
    return f"{prefix}_{digest}"


def ensure_numeric(df: pd.DataFrame, column: str | None, default: float = 0.0) -> pd.Series:
    """
    Yo convierto columnas numéricas de forma defensiva para que el bridge no falle por formatos mixtos.
    """
    if column is None or column not in df.columns:
        return pd.Series([default] * len(df), index=df.index)
    return pd.to_numeric(df[column], errors="coerce").fillna(default)


def prepare_public_frame(df: pd.DataFrame) -> pd.DataFrame:
    """
    Yo reduzco el ranking real a columnas agregables y no personales.
    """
    risk_col = find_column(df, ["riesgo_caida", "risk_score", "probabilidad_caida", "score_riesgo"])
    value_col = find_column(df, ["valor_esperado_en_riesgo", "expected_value_at_risk", "valor_riesgo"])
    project_col = find_column(df, ["proyecto", "project"])
    advisor_col = find_column(df, ["asesor", "advisor", "responsable"])
    channel_col = find_column(df, ["canal_agrupado", "canal", "medio_captacion", "medio", "source_channel"])
    days_col = find_column(df, ["dias_en_tuberia", "days_in_pipeline"])

    if risk_col is None:
        raise ValueError("No encuentro columna de riesgo para construir payload público.")
    if value_col is None:
        raise ValueError("No encuentro columna de valor esperado en riesgo para construir payload público.")

    public = pd.DataFrame(index=df.index)
    public["proyecto"] = df[project_col].fillna("Sin proyecto") if project_col else "Sin proyecto"
    public["asesor_anon"] = df[advisor_col].apply(stable_anon_label) if advisor_col else "Asesor_SIN_DATO"
    public["canal"] = df[channel_col].fillna("Sin canal") if channel_col else "Sin canal"
    public["riesgo_caida"] = ensure_numeric(df, risk_col)
    public["valor_esperado_en_riesgo"] = ensure_numeric(df, value_col)
    public["dias_en_tuberia"] = ensure_numeric(df, days_col)

    if "prioridad_operativa" in df.columns:
        public["prioridad_operativa"] = df["prioridad_operativa"].fillna("P3_monitoreo")
    else:
        public["prioridad_operativa"] = public.apply(classify_operational_priority, axis=1)

    return public


def aggregate_dimension(public: pd.DataFrame, group_col: str, label_col: str, top_n: int = 10) -> list[dict[str, Any]]:
    """
    Yo agrego dimensiones para Railway sin exponer filas operativas ni datos personales.
    """
    agg = (
        public.groupby(group_col, dropna=False)
        .agg(
            operaciones=("riesgo_caida", "size"),
            valor_en_riesgo=("valor_esperado_en_riesgo", "sum"),
            riesgo_promedio=("riesgo_caida", "mean"),
            p0_p1=("prioridad_operativa", lambda s: int(s.isin(["P0_intervenir_hoy", "P1_24_horas"]).sum())),
        )
        .reset_index()
        .sort_values(["valor_en_riesgo", "operaciones"], ascending=[False, False])
        .head(top_n)
    )
    agg = agg.rename(columns={group_col: label_col})
    agg["valor_en_riesgo"] = agg["valor_en_riesgo"].round(2)
    agg["riesgo_promedio"] = agg["riesgo_promedio"].round(4)
    return agg.to_dict(orient="records")


def build_public_payload(ranking: pd.DataFrame) -> dict[str, Any]:
    """
    Yo construyo un payload público agregado para Railway.
    Este JSON sirve para dashboard comercial sin exponer clientes, documentos ni credenciales.
    """
    public = prepare_public_frame(ranking)
    p0_p1_mask = public["prioridad_operativa"].isin(["P0_intervenir_hoy", "P1_24_horas"])

    payload: dict[str, Any] = {
        "total_operaciones": int(len(public)),
        "valor_total_en_riesgo": round(float(public["valor_esperado_en_riesgo"].sum()), 2),
        "riesgo_promedio": round(float(public["riesgo_caida"].mean()), 4) if len(public) else 0.0,
        "p0_p1": {
            "operaciones": int(p0_p1_mask.sum()),
            "valor_en_riesgo": round(float(public.loc[p0_p1_mask, "valor_esperado_en_riesgo"].sum()), 2),
        },
        "top_proyectos": aggregate_dimension(public, "proyecto", "proyecto"),
        "top_asesores": aggregate_dimension(public, "asesor_anon", "asesor_anon"),
        "top_canales": aggregate_dimension(public, "canal", "canal"),
        "fecha_generacion": datetime.now().isoformat(timespec="seconds"),
        "data_mode": "crm",
    }
    assert set(payload.keys()) == ALLOWED_TOP_LEVEL_KEYS
    assert_public_payload_is_safe(payload)
    return payload


def walk_payload(value: Any, path: str = "root") -> list[tuple[str, Any]]:
    """
    Yo recorro el payload para auditar claves y valores antes de publicarlo.
    """
    items: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            items.append((f"{path}.{key}", key))
            items.extend(walk_payload(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            items.extend(walk_payload(child, f"{path}[{idx}]"))
    else:
        items.append((path, value))
    return items


def assert_public_payload_is_safe(payload: dict[str, Any]) -> None:
    """
    Yo valido que el payload público no contenga nombres, documentos, teléfonos ni credenciales.
    """
    violations: list[str] = []
    sensitive_regexes = [
        re.compile(r"\b\d{8}\b"),  # DNI peruano típico.
        re.compile(r"\b9\d{8}\b"),  # celular peruano típico.
        re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    ]

    for path, value in walk_payload(payload):
        text = str(value)
        key_text = path.lower()
        if any(pattern in key_text for pattern in SENSITIVE_KEY_PATTERNS):
            violations.append(f"clave sensible en {path}")
        if isinstance(value, str) and any(regex.search(text) for regex in sensitive_regexes):
            violations.append(f"valor con patrón sensible en {path}")
        if isinstance(value, str) and any(pattern in text.lower() for pattern in ["password", "secret", "redshift_password", "api_key"]):
            violations.append(f"valor con posible credencial en {path}")

    if violations:
        raise ValueError("Payload público inseguro: " + "; ".join(violations[:20]))


def export_public_payload(input_path: Path | None = None, output_path: Path = PUBLIC_PAYLOAD_PATH) -> Path:
    """
    Yo exporto el payload público que Railway puede servir sin tocar datos personales.
    """
    ranking = read_ranking(input_path)
    payload = build_public_payload(ranking)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Exporta payload público agregado para Railway.")
    parser.add_argument("--input", type=Path, default=None, help="Ranking CSV/Parquet opcional.")
    parser.add_argument("--output", type=Path, default=PUBLIC_PAYLOAD_PATH, help="Ruta JSON pública.")
    args = parser.parse_args()
    output = export_public_payload(args.input, args.output)
    print(f"Payload público generado: {output}")


if __name__ == "__main__":
    main()
