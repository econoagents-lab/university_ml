# Railway Real Data Bridge v1.2.2

## 1. Propósito

Yo uso este bridge para llevar a Railway un dashboard público basado en CRM real sin exponer filas operativas, clientes, documentos, teléfonos ni credenciales.

El archivo autorizado para Railway es:

```text
reports/public/decision_dashboard_payload_public.json
```

## 2. Qué contiene

El payload público contiene solamente agregados:

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

`top_asesores` usa identificadores anónimos estables, por ejemplo `Asesor_AB12CD34`. Yo no publico nombres personales.

## 3. Qué no debe contener

No debe contener:

```text
cliente
documento
DNI
email
teléfono
nombre completo
dirección
credenciales
tokens
passwords
filas individuales de operaciones
```

## 4. Flujo recomendado

```text
CRM / scoring interno
→ data/processed/scoring/ranking_operaciones_riesgo_caida.csv
→ scripts/69_export_public_dashboard_payload.py
→ reports/public/decision_dashboard_payload_public.json
→ scripts/70_validate_no_demo_data_in_production.py
→ Railway sirve /public/decision-dashboard/payload
```

## 5. Comandos

```powershell
python scripts/69_export_public_dashboard_payload.py
python scripts/70_validate_no_demo_data_in_production.py --environment production
```

Opcional, si creas un endpoint receptor en Railway:

```powershell
$env:RAILWAY_PUBLIC_PAYLOAD_SYNC_URL="https://tu-app.up.railway.app/admin/sync-public-payload"
$env:RAILWAY_PUBLIC_PAYLOAD_SYNC_TOKEN="token_seguro"
python scripts/71_sync_public_payload_to_railway.py
```

## 6. Producción sin fallback demo

En Railway configura:

```text
MLU_ENV=production
MLU_DISABLE_SAMPLE_FALLBACK=true
```

Con eso, la API aplica esta regla:

```python
# Yo bloqueo datos demo cuando estoy en producción.
if environment == "production" and disable_sample_fallback and not public_payload.exists():
    raise RuntimeError("No hay payload CRM público disponible. No sirvo data demo en producción.")
```

## 7. Railway vs Lenovo

- Yo uso Lenovo para ejecutar CRM real, Redshift, PS1, parquets y scoring privado.
- Yo uso Railway para servir una demo pública/API con agregados no sensibles.
- Yo uso GitHub Actions para validar que el payload no tenga PII ni data demo.

## 8. Endpoint nuevo

```text
GET /public/decision-dashboard/payload
GET /public/decision-dashboard
```

Si falta el payload y producción bloquea fallback, Railway responde `503` en vez de inventar demo data.
