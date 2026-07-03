# Lenovo self-hosted runner vs Railway

## Mi decisión recomendada

Yo uso ambos, pero para cosas distintas.

| Opción | Mejor para | No ideal para |
|---|---|---|
| Lenovo self-hosted runner | Redshift real, Parquets locales, PowerShell, refresh completo, datos privados | Alta disponibilidad pública |
| Railway | API demo, endpoint estable, dashboard ligero, smoke tests, acceso externo | Procesos pesados, credenciales locales, Power BI Desktop |
| GitHub cloud runner | Tests, alertas sobre outputs ya versionados, readiness UNI | CRM privado o extracción completa |

## Arquitectura recomendada

```text
Lenovo self-hosted
→ extrae CRM / genera ranking / corre PS1 / produce reports
→ GitHub Actions sube artifacts y abre alertas

Railway
→ sirve API/dashboard demo
→ GitHub Actions hace smoke test diario
→ si falla, abre alerta
```

## Cuándo uso cada uno

- Yo uso Lenovo cuando quiero verdad operativa completa.
- Yo uso Railway cuando quiero mostrar la fábrica como producto accesible.
- Yo uso GitHub cloud cuando quiero checks livianos, reproducibles y sin tocar datos sensibles.
