# Runbook del experimento comercial

## 1. Antes de correr

Yo valido que exista la cola segura:

```powershell
python scripts/94_run_v17_decision_action_feedback_lab.py
```

## 2. Ejecutar experimento

```powershell
python scripts/99_run_v18_experimentation_causal_impact_lab.py
```

## 3. Completar feedback real

El equipo comercial debe registrar `accion_tomada`, `resultado_7d`, `resultado_30d` y `caida_real_30d` en la plantilla segura del laboratorio v1.7.

## 4. Interpretar impacto

- `estimated`: hay muestra mínima y outcomes observados.
- `needs_more_feedback`: todavía no hay evidencia suficiente.

## 5. Decisión económica

Si la reducción de tasa negativa es positiva y estable, se escala intervención. Si no existe diferencia, se revisa acción, segmentación, SLA o modelo.
