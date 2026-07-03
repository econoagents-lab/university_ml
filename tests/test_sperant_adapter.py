from src.mlu.sperant_adapter import infer_channel_group, normalize_unit_family


def test_infer_channel_group():
    assert infer_channel_group("facebook") == "digital"
    assert infer_channel_group("Feria Urbania") == "digital" or infer_channel_group("Feria Urbania") in {"digital", "ferias"}
    assert infer_channel_group("sala de ventas") == "tradicional"


def test_normalize_unit_family():
    assert normalize_unit_family("departamento flat") == "departamento"
    assert normalize_unit_family("estacionamiento simple") == "estacionamiento"
    assert normalize_unit_family("depósito") == "deposito"
