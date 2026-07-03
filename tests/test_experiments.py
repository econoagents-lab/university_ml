import pandas as pd

from src.mlu.experiments import create_experiment_assignments, analyze_intervention_effect


def test_create_experiment_assignments_has_groups():
    ranking = pd.DataFrame({
        "codigo_proforma": [f"P{i}" for i in range(50)],
        "codigo_unidad": [f"U{i}" for i in range(50)],
        "ranking_prioridad": list(range(1, 51)),
        "riesgo_caida": [0.5] * 50,
    })
    out = create_experiment_assignments(ranking, top_n=50, holdout_rate=0.2, random_state=7)
    assert len(out) == 50
    assert {"intervention", "control_holdout"}.issubset(set(out["experiment_group"]))


def test_analyze_intervention_effect_insufficient_without_outcomes():
    feedback = pd.DataFrame({"accion_tomada": ["pendiente"], "caida_real_30d": [""]})
    result = analyze_intervention_effect(feedback)
    assert result["status"] in {"insufficient_data", "no_data", "missing_outcome"}
