# Machine Learning University v1.2.2 · Railway Real Data Bridge

Esta versión agrega un puente seguro entre el scoring real del CRM y una demo/API pública en Railway.

La regla central es simple:

> Yo puedo publicar agregados comerciales. No publico clientes, documentos, teléfonos, emails, nombres completos, direcciones ni credenciales.

## Payload público autorizado

```text
reports/public/decision_dashboard_payload_public.json
```

Contiene solo:

```text
total_operaciones
valor_total_en_riesgo
riesgo_promedio
p0_p1
top_proyectos
top_asesores
top_canales
fecha_generacion
data_mode = crm
```

## Scripts nuevos

```text
scripts/69_export_public_dashboard_payload.py
scripts/70_validate_no_demo_data_in_production.py
scripts/71_sync_public_payload_to_railway.py
```

## API nueva

```text
GET /public/decision-dashboard/payload
GET /public/decision-dashboard
```

## Seguridad

En producción:

```text
MLU_ENV=production
MLU_DISABLE_SAMPLE_FALLBACK=true
```

Si el payload público CRM no existe, la API falla de forma explícita en vez de servir demo data.

## Validación

```text
71 passed, 1 warning
```

## v1.3 · Dashboard Catalog Parameter Control

Esta versión convierte los dashboards en productos de decisión gobernados por parámetros.

### Ejecutar control de dashboards

```powershell
python scripts/76_run_v13_dashboard_control.py
pytest -q
```

### Outputs principales

- `config/dashboard_catalog.yml`
- `config/dashboard_params.yml`
- `config/model_params.yml`
- `config/privacy_policy.yml`
- `reports/dashboard_control/DASHBOARD_CONTROL_PANEL.md`
- `reports/dashboard_control/INPUTS_TO_CONFIRM.md`

### Decisiones tomadas

- Railway sirve payload CRM agregado, no CRM live.
- Lenovo queda como runner privado para CRM completo.
- GitHub publica artifacts agregados o anonimizados.
- Proyectos públicos: sí, solo agregados.
- Asesores públicos: no, se anonimizan.
- Canales públicos: sí, agregados.
- Clientes, DNI, teléfonos, emails, direcciones y credenciales: nunca.

## v1.4 · Dashboard Generator From Catalog

Yo convierto `config/dashboard_catalog.yml` en dashboards reales Markdown/HTML/JSON. Ejecuta:

```powershell
python scripts/80_run_v14_dashboard_generator.py
# o
.\run_dashboard_generator_from_catalog.ps1 -RunTests -OpenIndex
```

Salida principal:

```text
reports/generated_dashboards/index.html
reports/generated_dashboards/DASHBOARD_INDEX.md
reports/generated_dashboards/dashboard_generation_manifest.json
```
