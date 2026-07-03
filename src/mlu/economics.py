from __future__ import annotations


def recommend_decision(riesgo: float, asesor: str) -> dict:
    if riesgo >= 0.70:
        return {
            "nivel_riesgo": "alto",
            "decision_recomendada": "Escalar a gerente comercial y contactar al cliente hoy.",
            "responsable": asesor,
            "sla_horas": 4,
        }
    if riesgo >= 0.40:
        return {
            "nivel_riesgo": "medio",
            "decision_recomendada": "Priorizar seguimiento del asesor en las próximas 24 horas.",
            "responsable": asesor,
            "sla_horas": 24,
        }
    return {
        "nivel_riesgo": "bajo",
        "decision_recomendada": "Mantener seguimiento comercial estándar.",
        "responsable": asesor,
        "sla_horas": 72,
    }


def expected_value_at_risk(riesgo: float, precio_departamento: float, recovery_rate: float = 0.15) -> float:
    """Valor esperado en riesgo si no se actúa.

    recovery_rate representa la proporción recuperable si se interviene a tiempo.
    """
    return float(riesgo * precio_departamento * recovery_rate)
