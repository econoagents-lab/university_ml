# Machine Learning University · v1.8 Experimentation Causal Impact Lab

Esta versión integra la fábrica completa hasta el laboratorio de experimentación: riesgo, dashboards, marts reales, feedback operativo y medición de impacto.

## Ejecución principal

```powershell
python scripts/99_run_v18_experimentation_causal_impact_lab.py
pytest -q tests/test_experimentation_causal_impact_lab.py
```

## Con datos privados en Lenovo

```powershell
.\run_experimentation_causal_impact_lab.ps1 -PrivateDataDir "C:\Repos\freelance\ml_university_ready\data\raw\sperant" -RunTests -OpenReport
```

## Qué produce

- diseño experimental auditado;
- asignación tratamiento/control con IDs seguros;
- outcomes 7d/30d;
- resumen de impacto;
- reporte ejecutivo;
- validación anti-PII.
## v1.9 Experiment Power & Policy Engine

Yo agrego poder estadístico, compliance, impacto por segmento, SLA/capacidad y política de escalamiento P0/P1/P2 para convertir el experimento en política comercial.
