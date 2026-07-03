# API Endpoints v0.9

## Decisión diaria

- `GET /decision/riesgo-caida/kpis`
- `GET /decision/riesgo-caida/queue?limit=50&prioridad=P0_intervenir_hoy`
- `GET /decision/riesgo-caida/by-proyecto`
- `GET /decision/riesgo-caida/by-asesor`
- `GET /decision/riesgo-caida/action-plan?limit=25`
- `GET /decision/riesgo-caida/brief`
- `GET /dashboard/riesgo-caida`

## Modelo y gobierno

- `GET /metadata/model-registry`
- `GET /monitoring/riesgo-caida/latest`
- `GET /feedback/riesgo-caida/schema`
- `POST /feedback/riesgo-caida`

## Predicción

- `POST /predict/riesgo-caida`
- `POST /predict/riesgo-caida/batch`
