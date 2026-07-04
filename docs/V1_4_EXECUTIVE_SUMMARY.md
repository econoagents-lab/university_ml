# v1.4 · Executive Summary

v1.4 convierte el catálogo de dashboards en una fábrica de tableros navegables. Ya no solo existe una lista de 60 productos de decisión: ahora cada producto se genera como Markdown, HTML y JSON.

## Valor comercial

- Permite mostrar una demo amplia sin tocar Power BI.
- Ordena dashboards por familia de decisión: ejecutivo, comercial, riesgo, stock/pricing, cobranza, MLOps, RAG, UNI, privacidad y mercado.
- Mantiene la columna `Donde cambiar` viva dentro de cada tablero.
- Facilita publicar artifacts en GitHub Actions o servir un índice HTML desde Railway si se decide hacerlo solo con agregados.

## Salida principal

```text
reports/generated_dashboards/index.html
reports/generated_dashboards/DASHBOARD_INDEX.md
reports/generated_dashboards/dashboard_generation_manifest.json
reports/generated_dashboards/dashboard_generation_validation.json
```

## Regla de oro

Yo cambio estrategia modificando YAML, no editando dashboards manualmente.
