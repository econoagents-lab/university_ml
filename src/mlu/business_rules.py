from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ProcessRuleConfig:
    """Configuración inferida para Cygnus/Sperant.

    La configuración es deliberadamente explícita: el alumno puede discutirla,
    cambiarla y ver cómo cambia el dataset de entrenamiento.
    """

    horizon_days: int = 30
    unit_focus: str = "departamentos"
    allow_inactive_historical_for_training: bool = True
    use_estado_activo_for_current_scoring: bool = True


DEFAULT_RULE_CONFIG = ProcessRuleConfig()


DEPARTMENT_TOKENS = ("departamento", "depa", "flat", "duplex", "dúplex", "triplex", "tríplex")
PARKING_TOKENS = ("estacionamiento", "cochera", "parking")
STORAGE_TOKENS = ("deposito", "depósito")
LOCAL_TOKENS = ("local",)


def normalize_text(value) -> str:
    """Normaliza texto para reglas flexibles.

    Nunca asumimos que Sperant tendrá el mismo casing, acentos o espacios.
    """
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def first_existing_column(df: pd.DataFrame, candidates: Iterable[str], default=None) -> pd.Series:
    """Devuelve la primera columna existente entre varias candidatas.

    Evita romper scripts cuando una tabla viene de Redshift, Power BI export o parquet intermedio.
    """
    for column in candidates:
        if column in df.columns:
            return df[column]
    return pd.Series([default] * len(df), index=df.index)


def coalesce_dates(df: pd.DataFrame, candidates: Iterable[str]) -> pd.Series:
    """Devuelve la primera fecha no nula según prioridad de negocio."""
    result = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")
    for column in candidates:
        if column in df.columns:
            candidate = pd.to_datetime(df[column], errors="coerce")
            result = result.fillna(candidate)
    return result


def normalize_unit_family(tipo_unidad) -> str:
    """Clasifica unidades en familias analíticas.

    Separar departamentos de estacionamientos/depósitos es obligatorio antes de modelar.
    """
    text = normalize_text(tipo_unidad)
    if any(token in text for token in DEPARTMENT_TOKENS):
        return "departamento"
    if any(token in text for token in PARKING_TOKENS):
        return "estacionamiento"
    if any(token in text for token in STORAGE_TOKENS):
        return "deposito"
    if any(token in text for token in LOCAL_TOKENS):
        return "local"
    return "otro"


def infer_channel_group(medio) -> str:
    text = normalize_text(medio)
    # Las ferias se evalúan antes que portales como Urbania porque "Feria Urbania"
    # en los reportes comerciales se interpreta como evento/feria, no como portal puro.
    if any(token in text for token in ["feria", "expo"]):
        return "ferias"
    if any(token in text for token in ["facebook", "fb", "instagram", "google", "web", "nexo", "urbania", "digital", "portal"]):
        return "digital"
    if any(token in text for token in ["sala", "referido", "mayra", "seguimiento", "whatsapp", "call"]):
        return "tradicional"
    return "sin_clasificar"


def build_process_flags(procesos: pd.DataFrame) -> pd.DataFrame:
    """Agrega banderas de separación, venta/minuta, caída y familia de unidad.

    Estas reglas están inferidas desde el historial reciente. El valor educativo es que
    quedan en código, no escondidas en DAX o memoria oral.
    """
    df = procesos.copy()

    flow = first_existing_column(df, ["nombre_flujo", "flujo", "nombre"], "").map(normalize_text)
    cancel_flow = first_existing_column(df, ["flujo_anulacion"], "").map(normalize_text)
    momento_caida = first_existing_column(df, ["momento_caida"], "").map(normalize_text)

    has_proforma = first_existing_column(df, ["codigo_proforma"], None).notna()
    fecha_inicio = pd.to_datetime(first_existing_column(df, ["fecha_inicio"], pd.NaT), errors="coerce")
    fecha_anulacion = pd.to_datetime(first_existing_column(df, ["fecha_anulacion"], pd.NaT), errors="coerce")

    df["_is_separacion_valida"] = has_proforma & fecha_inicio.notna() & flow.str.contains("separ", na=False)

    # Venta/Minuta: separar "Separación de venta" de procesos de venta reales cuando sea posible.
    contains_minuta = flow.str.contains("minuta", na=False)
    contains_proceso_venta = flow.str.contains("proceso de venta", na=False)
    df["_is_venta_minuta_valida"] = has_proforma & (contains_minuta | contains_proceso_venta)

    df["_is_caida_valida"] = has_proforma & (
        fecha_anulacion.notna()
        | cancel_flow.str.contains("anul|caid", na=False)
        | flow.str.contains("anul|caid", na=False)
        | momento_caida.isin(["proceso", "venta"])
    )

    df["_fecha_separacion"] = fecha_inicio.where(df["_is_separacion_valida"])
    df["_fecha_venta_minuta"] = coalesce_dates(df, ["fecha_fin", "fecha_inicio", "fecha_contrato", "fecha_minuta"]).where(
        df["_is_venta_minuta_valida"]
    )
    df["_fecha_caida"] = coalesce_dates(df, ["fecha_anulacion", "fecha_fin", "fecha_inicio"]).where(df["_is_caida_valida"])

    unidad_tipo = first_existing_column(df, ["tipo_unidad_principal", "tipo_unidad"], "")
    df["_familia_unidad"] = unidad_tipo.map(normalize_unit_family)

    return df


def build_operation_lifecycle(procesos: pd.DataFrame, unit_focus: str = "departamentos") -> pd.DataFrame:
    """Construye una operación consolidada por proforma/unidad.

    Salida: una fila por `codigo_proforma + codigo_unidad` con fechas de separación,
    venta/minuta y caída.
    """
    eventos = build_process_flags(procesos)

    if unit_focus == "departamentos":
        eventos = eventos[eventos["_familia_unidad"].eq("departamento")].copy()

    keys = [column for column in ["codigo_proforma", "codigo_unidad"] if column in eventos.columns]
    if not keys:
        raise ValueError("La tabla procesos debe contener codigo_proforma y/o codigo_unidad.")

    sep = eventos[eventos["_is_separacion_valida"]].copy()
    if sep.empty:
        raise ValueError("No se encontraron separaciones válidas con las reglas inferidas.")

    sep = sep.sort_values(keys + ["_fecha_separacion"])
    base = sep.groupby(keys, dropna=False).first().reset_index()

    venta = (
        eventos[eventos["_is_venta_minuta_valida"]]
        .groupby(keys, dropna=False)["_fecha_venta_minuta"]
        .min()
        .reset_index()
        .rename(columns={"_fecha_venta_minuta": "fecha_firma"})
    )

    caida = (
        eventos[eventos["_is_caida_valida"]]
        .groupby(keys, dropna=False)["_fecha_caida"]
        .min()
        .reset_index()
        .rename(columns={"_fecha_caida": "fecha_caida"})
    )

    out = base.merge(venta, on=keys, how="left").merge(caida, on=keys, how="left")
    out = out.rename(columns={"_fecha_separacion": "fecha_separacion"})
    return out


def build_gold_riesgo_caida_from_processes(
    procesos: pd.DataFrame,
    snapshot_days: Iterable[int] = (7, 14, 30),
    horizon_days: int = 30,
    unit_focus: str = "departamentos",
) -> pd.DataFrame:
    """Construye gold table de riesgo de caída usando reglas inferidas.

    Grano: `codigo_proforma + codigo_unidad + fecha_snapshot`.
    Target: caída dentro de `horizon_days` posteriores al snapshot.
    """
    ops = build_operation_lifecycle(procesos, unit_focus=unit_focus)
    ops["fecha_separacion"] = pd.to_datetime(ops["fecha_separacion"], errors="coerce")
    ops["fecha_firma"] = pd.to_datetime(ops.get("fecha_firma"), errors="coerce")
    ops["fecha_caida"] = pd.to_datetime(ops.get("fecha_caida"), errors="coerce")

    rows = []
    for day in snapshot_days:
        snap = ops.copy()
        snap["snapshot_day"] = int(day)
        snap["fecha_snapshot"] = snap["fecha_separacion"] + pd.to_timedelta(int(day), unit="D")

        signed_before = snap["fecha_firma"].notna() & (snap["fecha_firma"] <= snap["fecha_snapshot"])
        dropped_before = snap["fecha_caida"].notna() & (snap["fecha_caida"] <= snap["fecha_snapshot"])
        snap = snap[~signed_before & ~dropped_before].copy()

        snap["caida_30d"] = (
            snap["fecha_caida"].notna()
            & (snap["fecha_caida"] > snap["fecha_snapshot"])
            & (snap["fecha_caida"] <= snap["fecha_snapshot"] + pd.Timedelta(days=int(horizon_days)))
        ).astype(int)
        rows.append(snap)

    if not rows:
        raise ValueError("No hay filas para gold de riesgo de caída después de snapshots.")

    df = pd.concat(rows, ignore_index=True)

    medio = first_existing_column(df, ["origen_proforma", "medio_captacion", "utm_source", "utm_medium"], "sin medio")
    precio = first_existing_column(df, ["precio_venta", "precio_base_proforma", "precio_lista"], np.nan)
    descuento = pd.to_numeric(first_existing_column(df, ["descuento_venta"], 0), errors="coerce").fillna(0)
    precio_num = pd.to_numeric(precio, errors="coerce").fillna(0)

    gold = pd.DataFrame(
        {
            "codigo_proforma": first_existing_column(df, ["codigo_proforma"], ""),
            "codigo_unidad": first_existing_column(df, ["codigo_unidad"], ""),
            "fecha_separacion": df["fecha_separacion"],
            "fecha_snapshot": df["fecha_snapshot"],
            "snapshot_day": df["snapshot_day"].astype(int),
            "proyecto": first_existing_column(df, ["nombre_proyecto", "codigo_proyecto"], "sin proyecto").fillna("sin proyecto").astype(str),
            "asesor": first_existing_column(df, ["nombres_usuario", "username", "usuario_separacion"], "sin asesor").fillna("sin asesor").astype(str),
            "medio_captacion": medio.fillna("sin medio").astype(str),
            "canal_agrupado": medio.fillna("sin medio").map(infer_channel_group),
            "dormitorios": pd.to_numeric(first_existing_column(df, ["total_habitaciones", "unidad_total_habitaciones"], 0), errors="coerce").fillna(0).clip(0, 10),
            "precio_departamento": precio_num,
            "dias_en_tuberia": df["snapshot_day"].astype(int),
            "tiene_cuota_inicial": pd.to_numeric(first_existing_column(df, ["total_pagado", "monto_pagado_cuota_inicial"], 0), errors="coerce").fillna(0).gt(0),
            "cambios_unidad": 0,
            "interacciones_ult_7d": 0,
            "descuento_pct": (descuento / precio_num.replace(0, np.nan)).replace([np.inf, -np.inf], np.nan).fillna(0).clip(0, 1),
            "fecha_firma": df["fecha_firma"],
            "fecha_caida": df["fecha_caida"],
            "caida_30d": df["caida_30d"].astype(int),
            "source_system": "sperant_redshift",
            "rule_version": "0.4.0-inferred",
        }
    )
    return gold[gold["precio_departamento"].gt(0)].copy()


def summarize_inferred_rules(procesos: pd.DataFrame) -> dict:
    """Genera resumen de impacto de reglas sobre procesos."""
    eventos = build_process_flags(procesos)
    return {
        "rows": int(len(eventos)),
        "separaciones_validas": int(eventos["_is_separacion_valida"].sum()),
        "ventas_minutas_validas": int(eventos["_is_venta_minuta_valida"].sum()),
        "caidas_validas": int(eventos["_is_caida_valida"].sum()),
        "familias_unidad": eventos["_familia_unidad"].value_counts(dropna=False).to_dict(),
        "fecha_inicio_min": str(pd.to_datetime(first_existing_column(eventos, ["fecha_inicio"], pd.NaT), errors="coerce").min()),
        "fecha_inicio_max": str(pd.to_datetime(first_existing_column(eventos, ["fecha_inicio"], pd.NaT), errors="coerce").max()),
    }
