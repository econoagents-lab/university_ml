# Roadmap

## MVP

- Track completo de riesgo de caída.
- 8 notebooks progresivos.
- Data sintética segura.
- Baseline vs modelo.
- API `/predict/riesgo-caida`.
- Model card y contratos.

## Profesional

- Track de lead scoring.
- Track de propensión a minuta.
- Track de stock lento.
- Track de cobranza en riesgo.
- Dashboard ejecutivo de errores y acciones.

## Enterprise

- Feature store simple con DuckDB/Postgres.
- Model registry con versionado.
- Monitoreo de drift.
- Feedback loop operativo.
- RAG table-to-text para historias comerciales.
- CEO brief automático semanal.

## Recomendación

Cerrar primero el MVP de riesgo de caída. Después convertir la plantilla en fábrica de tracks predictivos.

## Próxima frontera después de v0.2

1. Incorporar pagos de cuota inicial con fecha real para evitar proxies.
2. Crear feature table de interacciones antes del snapshot.
3. Separar tracks: riesgo caída, lead scoring, conversión a minuta, stock lento y cobranza.
4. Agregar MLflow o registry liviano.
5. Agregar feedback loop: acción tomada, responsable, resultado y valor salvado.


---

## Próxima iteración recomendada · v0.4

Objetivo: reemplazar supuestos generales por reglas oficiales de Sperant/Cygnus.

Entradas necesarias:

1. Reglas oficiales de flujos de separación, venta/minuta y caída.
2. Horizonte de predicción confirmado.
3. Grano final del modelo.
4. Features disponibles antes del snapshot.
5. Umbrales validados por capacidad operativa.
6. Lugar de almacenamiento del feedback loop.
7. Decisión de despliegue: local, laptop 24/7 o Railway.

---

## v0.4 · Reglas inferidas → reglas oficiales

Objetivo: convertir memoria reciente del proyecto en reglas ejecutables.

### Entregado

- Contrato inferido de separación, venta/minuta, caída y tubería.
- Script para construir gold table con reglas inferidas.
- Checklist de congelamiento de reglas.

### Siguiente paso

v0.5 debe recibir el input corregido del usuario y generar:

- `contracts/official_business_rules_cygnus_sperant.yml`;
- versión oficial de `business_rules.py`;
- tests con casos reales anonimizados;
- notebook `00_Reglas_Oficiales_del_Negocio.ipynb`;
- comparación entre reglas inferidas vs reglas oficiales.
