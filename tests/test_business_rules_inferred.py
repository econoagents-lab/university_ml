import pandas as pd

from src.mlu.business_rules import (
    build_gold_riesgo_caida_from_processes,
    build_process_flags,
    infer_channel_group,
    normalize_unit_family,
)


def _procesos_demo():
    return pd.DataFrame(
        [
            {
                "codigo_proforma": "PF-001",
                "codigo_unidad": "U-001",
                "nombre_flujo": "Separación Oficial",
                "flujo_anulacion": None,
                "momento_caida": None,
                "fecha_inicio": "2026-05-01",
                "fecha_fin": "2026-05-01",
                "fecha_anulacion": None,
                "tipo_unidad_principal": "departamento flat",
                "nombre_proyecto": "Proyecto Demo",
                "nombres_usuario": "Asesor Demo",
                "origen_proforma": "facebook",
                "precio_venta": 400000,
                "descuento_venta": 10000,
                "total_pagado": 0,
            },
            {
                "codigo_proforma": "PF-001",
                "codigo_unidad": "U-001",
                "nombre_flujo": "Anulación",
                "flujo_anulacion": "Anulación",
                "momento_caida": "proceso",
                "fecha_inicio": "2026-05-20",
                "fecha_fin": "2026-05-20",
                "fecha_anulacion": "2026-05-20",
                "tipo_unidad_principal": "departamento flat",
                "nombre_proyecto": "Proyecto Demo",
                "nombres_usuario": "Asesor Demo",
                "origen_proforma": "facebook",
                "precio_venta": 400000,
                "descuento_venta": 10000,
                "total_pagado": 0,
            },
        ]
    )


def test_normalize_unit_family():
    assert normalize_unit_family("departamento duplex") == "departamento"
    assert normalize_unit_family("estacionamiento simple") == "estacionamiento"
    assert normalize_unit_family("depósito") == "deposito"


def test_infer_channel_group():
    assert infer_channel_group("facebook") == "digital"
    assert infer_channel_group("Feria Urbania") == "ferias"
    assert infer_channel_group("sala de ventas") == "tradicional"


def test_build_process_flags():
    flags = build_process_flags(_procesos_demo())
    assert flags["_is_separacion_valida"].sum() == 1
    assert flags["_is_caida_valida"].sum() == 1
    assert flags["_familia_unidad"].iloc[0] == "departamento"


def test_build_gold_riesgo_caida_from_processes():
    gold = build_gold_riesgo_caida_from_processes(_procesos_demo(), snapshot_days=(7,), horizon_days=30)
    assert len(gold) == 1
    assert gold["caida_30d"].iloc[0] == 1
    assert gold["dias_en_tuberia"].iloc[0] == 7
