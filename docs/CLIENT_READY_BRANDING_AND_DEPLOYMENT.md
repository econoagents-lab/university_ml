# Client Ready Branding & Deployment v2.1

Esta versión convierte el Intelligence OS en una demo externa lista para cliente: landing ejecutiva, marca oscuro/dorado, rutas seguras, política Railway y token simple opcional.

## Principio
Lenovo procesa CRM privado. Railway expone solo payload público agregado. GitHub Actions valida privacidad y genera artifacts. El cliente ve decisión, no data sensible.

## Rutas
- `/demo/client-ready`
- `/demo/landing`
- `/metadata/client-ready`
- `/public/decision-dashboard`
- `/dashboard/productized-os`
- `/product/demo/package`

## Variables Railway recomendadas
```text
MLU_ENV=production
MLU_DISABLE_SAMPLE_FALLBACK=true
MLU_DEMO_AUTH_ENABLED=true
MLU_DEMO_TOKEN=<secret>
```
