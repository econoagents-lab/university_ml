import pandas as pd

from src.mlu.decision_dashboard import (
    build_dashboard_payload,
    build_decision_queue,
    compute_decision_kpis,
    generate_dashboard_html,
    generate_executive_brief,
)


def sample_ranking():
    return pd.DataFrame([
        {
            "codigo_proforma": "P-001",
            "codigo_unidad": "A101",
            "fecha_separacion": "2026-01-01",
            "proyecto": "Proyecto Aurora",
            "asesor": "Asesor Uno",
            "medio_captacion": "facebook",
            "canal_agrupado": "digital",
            "dormitorios": 2,
            "precio_departamento": 500000,
            "dias_en_tuberia": 140,
            "tiene_cuota_inicial": False,
            "cambios_unidad": 0,
            "interacciones_ult_7d": 0,
            "descuento_pct": 0.05,
            "riesgo_caida": 0.62,
            "nivel_riesgo": "medio",
            "decision_recomendada": "Priorizar",
            "responsable": "Asesor Uno",
            "valor_esperado_en_riesgo": 110000,
            "ranking_prioridad": 1,
        },
        {
            "codigo_proforma": "P-002",
            "codigo_unidad": "B202",
            "fecha_separacion": "2026-02-01",
            "proyecto": "Proyecto Bruma",
            "asesor": "Asesor Dos",
            "medio_captacion": "sala",
            "canal_agrupado": "tradicional",
            "dormitorios": 1,
            "precio_departamento": 300000,
            "dias_en_tuberia": 20,
            "tiene_cuota_inicial": True,
            "cambios_unidad": 0,
            "interacciones_ult_7d": 1,
            "descuento_pct": 0.01,
            "riesgo_caida": 0.12,
            "nivel_riesgo": "bajo",
            "decision_recomendada": "Monitorear",
            "responsable": "Asesor Dos",
            "valor_esperado_en_riesgo": 12000,
            "ranking_prioridad": 2,
        },
    ])


def test_build_decision_queue_adds_operational_columns():
    queue = build_decision_queue(sample_ranking())
    assert "prioridad_operativa" in queue.columns
    assert "sla_horas" in queue.columns
    assert "fecha_limite_accion" in queue.columns
    assert "ranking_decision" in queue.columns
    assert queue.iloc[0]["prioridad_operativa"] in {"P0_intervenir_hoy", "P1_24_horas"}


def test_decision_queue_strips_forbidden_columns():
    df = sample_ranking()
    df["fecha_caida"] = "2026-03-01"
    try:
        build_decision_queue(df)
    except ValueError as exc:
        assert "Anti-leakage" in str(exc)
    else:
        raise AssertionError("fecha_caida no debe entrar a decision queue")


def test_compute_decision_kpis_and_payload():
    queue = build_decision_queue(sample_ranking())
    kpis = compute_decision_kpis(queue)
    assert kpis["total_operaciones"] == 2
    assert kpis["valor_total_en_riesgo"] == 122000
    payload = build_dashboard_payload(queue)
    assert "kpis" in payload
    assert "action_plan" in payload


def test_generate_dashboard_html_and_brief(tmp_path, monkeypatch):
    queue = build_decision_queue(sample_ranking())
    payload = build_dashboard_payload(queue)
    html = generate_dashboard_html(payload)
    brief = generate_executive_brief(payload)
    assert html.exists()
    assert brief.exists()
