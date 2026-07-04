# v2.2 · Multi-Tenant Client Packaging

Yo convierto el Commercial Intelligence OS en una máquina de empaquetar demos por cliente: tema visual, módulos habilitados, token, payload agregado, landing, one-pager y paquete JSON.

## Qué genera

- `reports/client_tenants/tenant_index.html`
- `reports/client_tenants/TENANT_INDEX.md`
- `reports/client_tenants/<tenant_id>/landing.html`
- `reports/client_tenants/<tenant_id>/one_pager.md`
- `reports/client_tenants/<tenant_id>/public_payload.json`
- `reports/client_tenants/<tenant_id>/client_demo_package.json`

## Comando

```powershell
python scripts/116_run_v22_multi_tenant_client_packaging.py
pytest -q tests/test_multi_tenant_client_packaging.py
```

## Producción

En Railway o una demo externa, activa tokens por tenant:

```text
MLU_ENV=production
MLU_DEMO_TOKEN_CLIENTE_ALPHA=<secret>
MLU_DEMO_TOKEN_CLIENTE_BRAVO=<secret>
MLU_DEMO_TOKEN_CLIENTE_CONDOR=<secret>
```

No subas clientes, DNI, teléfonos, emails, direcciones, códigos crudos ni credenciales.
