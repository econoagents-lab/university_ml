from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .config import RAW_SPERANT_DIR, SPERANT_TRAINING_PATH, SPERANT_SCORING_PATH, METADATA_DIR

SOURCE_FILES = {
    "procesos": "procesos.parquet",
    "unidades": "unidades.parquet",
    "clientes": "clientes.parquet",
    "proyectos": "proyectos.parquet",
    "datos_extras": "datos_extras.parquet",
    "proforma_unidad": "proforma_unidad.parquet",
    "fact_leads_enriched": "fact_leads_enriched.parquet",
    "fact_conversion_leads": "fact_conversion_leads.parquet",
    "fact_separaciones": "fact_separaciones.parquet",
    "fact_firmas_minutas": "fact_firmas_minutas.parquet",
    "fact_caidas": "fact_caidas.parquet",
    "fact_separacion_cuota_inicial": "fact_separacion_cuota_inicial.parquet",
}


def normalize_text(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def infer_channel_group(medio: str) -> str:
    medio_norm = normalize_text(medio)
    if any(token in medio_norm for token in ["facebook", "fb", "instagram", "google", "web", "nexo", "urbania", "digital", "portal"]):
        return "digital"
    if any(token in medio_norm for token in ["feria", "expo"]):
        return "ferias"
    if any(token in medio_norm for token in ["sala", "referido", "mayra", "seguimiento", "whatsapp", "call"]):
        return "tradicional"
    return "sin_clasificar"


def normalize_unit_family(tipo: str) -> str:
    tipo_norm = normalize_text(tipo)
    if "departamento" in tipo_norm:
        return "departamento"
    if "estacionamiento" in tipo_norm or "cochera" in tipo_norm:
        return "estacionamiento"
    if "dep" in tipo_norm:
        return "deposito"
    if "local" in tipo_norm:
        return "local"
    return "otro"


def read_sources(input_dir: Path = RAW_SPERANT_DIR) -> dict[str, pd.DataFrame]:
    sources: dict[str, pd.DataFrame] = {}
    for name, filename in SOURCE_FILES.items():
        path = input_dir / filename
        if path.exists():
            sources[name] = pd.read_parquet(path)
    if "procesos" not in sources:
        available = ", ".join(sorted(p.name for p in input_dir.glob("*.parquet")))
        raise FileNotFoundError(
            f"No encontré procesos.parquet en {input_dir}. Archivos disponibles: {available}"
        )
    return sources


def profile_sources(input_dir: Path = RAW_SPERANT_DIR, output_path: Path | None = None) -> pd.DataFrame:
    rows = []
    for path in sorted(input_dir.glob("*.parquet")):
        df = pd.read_parquet(path)
        rows.append({
            "table_name": path.stem,
            "rows": int(len(df)),
            "columns": int(df.shape[1]),
            "null_cells": int(df.isna().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
        })
    profile = pd.DataFrame(rows).sort_values("table_name") if rows else pd.DataFrame(
        columns=["table_name", "rows", "columns", "null_cells", "duplicate_rows"]
    )
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        profile.to_parquet(output_path, index=False)
    return profile


def _first_existing(df: pd.DataFrame, candidates: Iterable[str], default=None):
    for col in candidates:
        if col in df.columns:
            return df[col]
    return pd.Series([default] * len(df), index=df.index)


def _safe_pct(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    den = pd.to_numeric(denominator, errors="coerce").replace(0, np.nan)
    num = pd.to_numeric(numerator, errors="coerce")
    return (num / den).replace([np.inf, -np.inf], np.nan).fillna(0).clip(lower=0, upper=1)


def _build_event_table(procesos: pd.DataFrame) -> pd.DataFrame:
    df = procesos.copy()
    for date_col in ["fecha_inicio", "fecha_fin", "fecha_minuta", "fecha_anulacion", "fecha_actualizacion"]:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    flow = _first_existing(df, ["nombre_flujo", "flujo_anulacion", "nombre"], "").astype(str).str.lower()
    df["_is_separacion"] = flow.str.contains("separ", na=False)
    df["_is_firma"] = flow.str.contains("minuta|proceso de venta|venta", na=False) & ~flow.str.contains("separ", na=False)
    df["_is_caida"] = flow.str.contains("anul|caid", na=False) | df.get("fecha_anulacion", pd.Series(pd.NaT, index=df.index)).notna()
    df["_unidad_familia"] = _first_existing(df, ["tipo_unidad_principal", "tipo_unidad"], "").apply(normalize_unit_family)
    return df


def _aggregate_operations(sources: dict[str, pd.DataFrame], unit_focus: str = "departamentos") -> pd.DataFrame:
    eventos = _build_event_table(sources["procesos"])

    if unit_focus == "departamentos":
        eventos = eventos[eventos["_unidad_familia"].eq("departamento")].copy()

    keys = [col for col in ["codigo_proforma", "codigo_unidad"] if col in eventos.columns]
    if not keys:
        raise ValueError("procesos.parquet debe contener codigo_proforma y/o codigo_unidad.")

    sep = eventos[eventos["_is_separacion"]].copy()
    if sep.empty:
        raise ValueError("No encontré eventos de separación en procesos.nombre_flujo.")

    sort_cols = keys + ["fecha_inicio"]
    sep = sep.sort_values(sort_cols)
    base = sep.groupby(keys, dropna=False).first().reset_index()
    base = base.rename(columns={"fecha_inicio": "fecha_separacion"})

    firma = (
        eventos[eventos["_is_firma"]]
        .groupby(keys, dropna=False)["fecha_inicio"]
        .min()
        .reset_index()
        .rename(columns={"fecha_inicio": "fecha_firma"})
    )
    caida_date_col = "fecha_anulacion" if "fecha_anulacion" in eventos.columns else "fecha_inicio"
    caida = eventos[eventos["_is_caida"]].copy()
    caida["fecha_caida_evento"] = caida[caida_date_col].fillna(caida.get("fecha_inicio"))
    caida = (
        caida.groupby(keys, dropna=False)["fecha_caida_evento"]
        .min()
        .reset_index()
        .rename(columns={"fecha_caida_evento": "fecha_caida"})
    )

    out = base.merge(firma, on=keys, how="left").merge(caida, on=keys, how="left")

    if "unidades" in sources and "codigo" in sources["unidades"].columns and "codigo_unidad" in out.columns:
        unidades = sources["unidades"].copy()
        unit_cols = [
            c for c in [
                "codigo", "tipo_unidad", "total_habitaciones", "area_techada", "area_libre",
                "area_total", "precio_lista", "precio_m2", "piso", "estado_comercial",
            ] if c in unidades.columns
        ]
        unidades = unidades[unit_cols].drop_duplicates("codigo")
        out = out.merge(unidades, left_on="codigo_unidad", right_on="codigo", how="left", suffixes=("", "_unidad"))

    return out


def build_riesgo_caida_training_dataset(
    input_dir: Path = RAW_SPERANT_DIR,
    output_path: Path = SPERANT_TRAINING_PATH,
    unit_focus: str = "departamentos",
    snapshot_days: Iterable[int] = (7, 14, 30),
) -> pd.DataFrame:
    """Construye una tabla gold para entrenar riesgo de caída desde Sperant.

    Grain recomendado:
        una fila = una operación inmobiliaria observada en un día de snapshot posterior a la separación.

    Target:
        caida_30d = 1 si la operación cae dentro de los 30 días posteriores al snapshot.

    Esta lógica evita una trampa común: usar datos futuros como features. El profesor solo puede ver
    lo que existe hasta el día del snapshot.
    """
    sources = read_sources(input_dir)
    ops = _aggregate_operations(sources, unit_focus=unit_focus)
    ops["fecha_separacion"] = pd.to_datetime(ops["fecha_separacion"], errors="coerce")
    ops["fecha_firma"] = pd.to_datetime(ops.get("fecha_firma"), errors="coerce")
    ops["fecha_caida"] = pd.to_datetime(ops.get("fecha_caida"), errors="coerce")
    ops = ops[ops["fecha_separacion"].notna()].copy()

    rows = []
    for snapshot_day in snapshot_days:
        snap = ops.copy()
        snap["snapshot_day"] = int(snapshot_day)
        snap["fecha_snapshot"] = snap["fecha_separacion"] + pd.to_timedelta(snapshot_day, unit="D")

        # En el día snapshot solo queremos operaciones que todavía podían decidirse.
        signed_before = snap["fecha_firma"].notna() & (snap["fecha_firma"] <= snap["fecha_snapshot"])
        dropped_before = snap["fecha_caida"].notna() & (snap["fecha_caida"] <= snap["fecha_snapshot"])
        snap = snap[~signed_before & ~dropped_before].copy()

        snap["caida_30d"] = (
            snap["fecha_caida"].notna()
            & (snap["fecha_caida"] > snap["fecha_snapshot"])
            & (snap["fecha_caida"] <= snap["fecha_snapshot"] + pd.Timedelta(days=30))
        ).astype(int)
        rows.append(snap)

    if not rows:
        raise ValueError("No hay filas suficientes para entrenamiento después de aplicar snapshots.")

    df = pd.concat(rows, ignore_index=True)

    medio = _first_existing(df, ["origen_proforma", "medio_captacion", "utm_source", "utm_medium"], "sin medio")
    asesor = _first_existing(df, ["nombres_usuario", "username", "usuario_separacion"], "sin asesor")
    proyecto = _first_existing(df, ["nombre_proyecto", "codigo_proyecto"], "sin proyecto")
    dormitorios = _first_existing(df, ["total_habitaciones"], np.nan)
    precio = _first_existing(df, ["precio_venta", "precio_base_proforma", "precio_lista"], np.nan)
    descuento = _first_existing(df, ["descuento_venta"], 0)
    total_pagado = _first_existing(df, ["total_pagado"], 0)

    gold = pd.DataFrame({
        "codigo_proforma": _first_existing(df, ["codigo_proforma"], ""),
        "codigo_unidad": _first_existing(df, ["codigo_unidad"], ""),
        "fecha_separacion": df["fecha_separacion"],
        "fecha_snapshot": df["fecha_snapshot"],
        "snapshot_day": df["snapshot_day"],
        "proyecto": proyecto.fillna("sin proyecto").astype(str),
        "asesor": asesor.fillna("sin asesor").astype(str),
        "medio_captacion": medio.fillna("sin medio").astype(str),
        "canal_agrupado": medio.fillna("sin medio").astype(str).map(infer_channel_group),
        "dormitorios": pd.to_numeric(dormitorios, errors="coerce").fillna(0).clip(lower=0, upper=10),
        "precio_departamento": pd.to_numeric(precio, errors="coerce").fillna(0),
        "dias_en_tuberia": df["snapshot_day"].astype(int),
        "tiene_cuota_inicial": pd.to_numeric(total_pagado, errors="coerce").fillna(0).gt(0),
        "cambios_unidad": 0,
        "interacciones_ult_7d": 0,
        "descuento_pct": _safe_pct(descuento, precio),
        "fecha_firma": df["fecha_firma"],
        "fecha_caida": df["fecha_caida"],
        "caida_30d": df["caida_30d"].astype(int),
        "source_system": "sperant_redshift",
        "dataset_version": "v0.2",
    })

    gold = gold[gold["precio_departamento"].gt(0)].copy()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gold.to_parquet(output_path, index=False)

    metadata = {
        "rows": int(len(gold)),
        "target_rate": float(gold["caida_30d"].mean()) if len(gold) else math.nan,
        "unit_focus": unit_focus,
        "snapshot_days": [int(x) for x in snapshot_days],
        "columns": list(gold.columns),
    }
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    (METADATA_DIR / "riesgo_caida_training_manifest.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return gold


def build_current_scoring_dataset(
    input_dir: Path = RAW_SPERANT_DIR,
    output_path: Path = SPERANT_SCORING_PATH,
    unit_focus: str = "departamentos",
    as_of_date: str | None = None,
) -> pd.DataFrame:
    """Construye una tabla actual de tubería para scorear operaciones vivas."""
    sources = read_sources(input_dir)
    ops = _aggregate_operations(sources, unit_focus=unit_focus)
    ops["fecha_separacion"] = pd.to_datetime(ops["fecha_separacion"], errors="coerce")
    ops["fecha_firma"] = pd.to_datetime(ops.get("fecha_firma"), errors="coerce")
    ops["fecha_caida"] = pd.to_datetime(ops.get("fecha_caida"), errors="coerce")
    if as_of_date:
        current = pd.to_datetime(as_of_date)
    else:
        current = pd.to_datetime(ops["fecha_separacion"].max())
    live = ops[ops["fecha_separacion"].notna()].copy()
    live = live[(live["fecha_firma"].isna() | (live["fecha_firma"] > current)) & (live["fecha_caida"].isna() | (live["fecha_caida"] > current))]
    medio = _first_existing(live, ["origen_proforma", "medio_captacion", "utm_source", "utm_medium"], "sin medio")
    precio = _first_existing(live, ["precio_venta", "precio_base_proforma", "precio_lista"], np.nan)
    descuento = _first_existing(live, ["descuento_venta"], 0)
    total_pagado = _first_existing(live, ["total_pagado"], 0)
    out = pd.DataFrame({
        "codigo_proforma": _first_existing(live, ["codigo_proforma"], ""),
        "codigo_unidad": _first_existing(live, ["codigo_unidad"], ""),
        "fecha_separacion": live["fecha_separacion"],
        "proyecto": _first_existing(live, ["nombre_proyecto", "codigo_proyecto"], "sin proyecto").astype(str),
        "asesor": _first_existing(live, ["nombres_usuario", "username", "usuario_separacion"], "sin asesor").astype(str),
        "medio_captacion": medio.astype(str),
        "canal_agrupado": medio.astype(str).map(infer_channel_group),
        "dormitorios": pd.to_numeric(_first_existing(live, ["total_habitaciones"], 0), errors="coerce").fillna(0),
        "precio_departamento": pd.to_numeric(precio, errors="coerce").fillna(0),
        "dias_en_tuberia": (current - live["fecha_separacion"]).dt.days.clip(lower=0).astype(int),
        "tiene_cuota_inicial": pd.to_numeric(total_pagado, errors="coerce").fillna(0).gt(0),
        "cambios_unidad": 0,
        "interacciones_ult_7d": 0,
        "descuento_pct": _safe_pct(descuento, precio),
    })
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(output_path, index=False)
    return out
