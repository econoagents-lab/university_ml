# Railway Deployment Env Checklist

## Variables requeridas
- `MLU_ENV` = `production`
- `MLU_DISABLE_SAMPLE_FALLBACK` = `true`
- `MLU_DEMO_AUTH_ENABLED` = `true`
- `MLU_DEMO_TOKEN` = `<configurar_en_Railway>`

## Start command
`uvicorn api.main:app --host 0.0.0.0 --port $PORT`

## Checklist
- [ ] Payload público CRM agregado existe.
- [ ] No hay clientes, DNI, teléfonos, emails ni direcciones.
- [ ] MLU_DISABLE_SAMPLE_FALLBACK=true.
- [ ] La landing abre sin exponer filas operativas.
- [ ] Los endpoints de demo responden 200.
- [ ] GitHub Actions genera artifacts de demo y valida privacidad.