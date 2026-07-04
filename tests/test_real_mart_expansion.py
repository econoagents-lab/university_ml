from pathlib import Path

import pandas as pd

from src.mlu.config import PROJECT_ROOT
from src.mlu.real_marts import (
    build_all_real_marts,
    validate_no_pii_in_marts,
    real_mart_metadata,
    MART_FUNNEL,
    MART_COBRANZA,
    MART_STOCK,
    MART_PRICING,
    MART_MARKET,
    MART_FEEDBACK,
    MART_PROXY_GAP,
)
from src.mlu.dashboard_metrics_engine import build_family_metrics, metrics_for_dashboard


def test_real_marts_are_generated_without_pii_columns():
    manifest = build_all_real_marts()
    validation = validate_no_pii_in_marts()
    assert len(manifest["marts"]) >= 7
    assert validation["status"] == "ok"
    for path in [MART_FUNNEL, MART_COBRANZA, MART_STOCK, MART_PRICING, MART_MARKET, MART_FEEDBACK, MART_PROXY_GAP]:
        assert path.exists(), path


def test_pricing_mart_uses_hashed_unit_id_not_raw_unit_code():
    build_all_real_marts()
    df = pd.read_csv(MART_PRICING)
    assert "unit_id" in df.columns
    forbidden = {"codigo_unidad", "codigo", "nombre_unidad", "documento_cliente", "cliente", "email", "celular"}
    assert not forbidden.intersection(set(df.columns))
    if not df.empty:
        assert df["unit_id"].astype(str).str.startswith("UNIT_").all()


def test_dashboard_metrics_engine_uses_real_marts_family():
    build_all_real_marts()
    bundle = build_family_metrics()
    assert "real_marts" in bundle["families"]
    assert bundle["families"]["real_marts"]["status"] in {"ok", "warning"}
    assert metrics_for_dashboard("proxy_vs_official_gap", "real_marts")["metric_group"] == "real_marts"


def test_real_mart_metadata_api_payload_shape():
    metadata = real_mart_metadata()
    assert metadata["validation_status"] == "ok"
    assert "marts" in metadata
    assert metadata["safe_aggregate_only"] is True
