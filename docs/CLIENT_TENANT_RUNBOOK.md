# Client Tenant Runbook

1. Crear tenant en `config/client_tenants.yml`.
2. Definir módulos habilitados.
3. Definir token env var, nunca el token real.
4. Generar paquetes con `scripts/116_run_v22_multi_tenant_client_packaging.py`.
5. Revisar `reports/client_tenants/tenant_index.html`.
6. En Railway configurar `MLU_ENV=production` y el token del tenant.
