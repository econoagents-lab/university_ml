# Multi-Tenant Client Packaging

Yo separo la demo por cliente para que cada prospecto vea una narrativa, módulos y payload adecuados sin tocar CRM crudo.

## Decisión de arquitectura

- Lenovo ejecuta CRM privado y genera payload agregado.
- Railway sirve demo segura por tenant.
- GitHub Actions valida PII y empaqueta artifacts.
- Cada cliente tiene token env var propio.

## Archivos clave

- `config/client_tenants.yml`
- `reports/client_tenants/<tenant_id>/landing.html`
- `reports/client_tenants/<tenant_id>/client_demo_package.json`
