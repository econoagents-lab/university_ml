import pandas as pd

from src.mlu.feedback import build_feedback_template, validate_feedback_log, merge_feedback_with_ranking


def test_feedback_template_is_valid():
    ranking = pd.DataFrame({
        "codigo_proforma": ["P1"],
        "codigo_unidad": ["U1"],
        "riesgo_caida": [0.7],
        "nivel_riesgo": ["alto"],
        "ranking_prioridad": [1],
        "responsable": ["Asesor"],
    })
    template = build_feedback_template(ranking, top_n=1, fecha_score="2026-07-03")
    validation = validate_feedback_log(template)
    assert validation["is_valid"]
    assert template.loc[0, "accion_tomada"] == "pendiente"


def test_merge_feedback_with_ranking():
    feedback = pd.DataFrame({
        "codigo_proforma": ["P1"],
        "codigo_unidad": ["U1"],
        "fecha_score": ["2026-07-03"],
        "riesgo_caida": [0.7],
        "nivel_riesgo": ["alto"],
        "ranking_prioridad": [1],
        "responsable": ["Asesor"],
        "accion_tomada": ["pendiente"],
        "fecha_accion": [""],
        "resultado_7d": ["pendiente"],
        "resultado_30d": ["pendiente"],
        "caida_real_30d": [""],
        "comentario": [""],
    })
    ranking = pd.DataFrame({"codigo_proforma": ["P1"], "codigo_unidad": ["U1"], "proyecto": ["Proyecto X"], "asesor": ["Asesor"]})
    merged = merge_feedback_with_ranking(feedback, ranking)
    assert merged.loc[0, "proyecto"] == "Proyecto X"
