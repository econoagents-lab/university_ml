from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app
from src.mlu.core_value_hardening import (
    build_capacity_based_queue,
    build_capacity_public_payload,
    run_core_value_hardening,
    validate_no_forbidden_public_content,
)


def test_capacity_prioritization_limits_p0_p1():
    queue = build_capacity_based_queue()
    assert not queue.empty
    counts = queue["prioridad_capacity"].value_counts().to_dict()
    assert counts.get("P0_top_capacity_today", 0) <= 30
    assert counts.get("P1_next_48h", 0) <= 70


def test_public_payload_is_aggregated_and_safe():
    queue = build_capacity_based_queue()
    payload = build_capacity_public_payload(queue)
    text = str(payload).lower()
    assert payload["prioritization_mode"] == "capacity_based_top_n"
    assert "codigo_proforma" not in text
    assert "codigo_unidad" not in text
    assert "dni" not in text


def test_core_value_hardening_endpoints():
    run_core_value_hardening()
    client = TestClient(app)
    r = client.get("/metadata/core-value-hardening")
    assert r.status_code == 200
    assert r.json()["version"] == "v2.7_core_value_hardening"
    r = client.get("/dashboard/executive-value-brief")
    assert r.status_code == 200
    assert "Core Value Hardening" in r.text
    r = client.get("/decision/riesgo-caida/capacity-queue?limit=5")
    assert r.status_code == 200
    assert r.json()["total"] <= 5


def test_public_validation_ok():
    run_core_value_hardening()
    validation = validate_no_forbidden_public_content()
    assert validation["status"] == "ok"
