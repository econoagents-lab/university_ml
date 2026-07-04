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
