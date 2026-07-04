# v1.4 · Dashboard Generator From Catalog

## Escena técnica

Yo dejo de crear dashboards como piezas sueltas. Ahora uso `config/dashboard_catalog.yml` como contrato maestro y genero artefactos reales en Markdown, HTML y JSON.

## Qué resuelve

- El catálogo deja de ser inventario y empieza a producir tableros.
- Cada dashboard conserva pregunta económica, owner, audiencia, prioridad y `donde cambiar`.
- La generación es segura por diseño: solo usa agregados y payload público cuando corresponde.
- La demo puede abrirse localmente desde `reports/generated_dashboards/index.html`.

## Flujo

```text
config/dashboard_catalog.yml
+ config/dashboard_params.yml
+ config/model_params.yml
+ reports/public/decision_dashboard_payload_public.json
+ data/processed/scoring/ranking_operaciones_riesgo_caida.csv
        ↓
scripts/80_run_v14_dashboard_generator.py
        ↓
reports/generated_dashboards/
├── index.html
├── DASHBOARD_INDEX.md
├── <familia>/<dashboard>.html
├── <familia>/<dashboard>.md
└── <familia>/<dashboard>.json
```

## Comandos

```powershell
python scripts/80_run_v14_dashboard_generator.py
pytest -q
```

## Política

Yo no uso filas individuales para generar dashboards de catálogo. Uso agregados comerciales, payload público y parámetros. Si quiero publicar en Railway, uso solo `reports/public/decision_dashboard_payload_public.json`.
