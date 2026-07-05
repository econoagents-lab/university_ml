# Dashboard Static Route Fix

Problema observado:

```text
/dashboard/reports/generated_dashboards/executive/ceo_brief.html -> {"detail":"Not Found"}
```

Causa:

El catálogo generaba archivos HTML en `reports/generated_dashboards`, pero FastAPI no tenía una ruta para servirlos en Railway.

Solución:

Se agregaron alias seguros:

```text
/dashboard/reports/generated_dashboards/{file_path:path}
/reports/generated_dashboards/{file_path:path}
/dashboard/{file_path:path}
```

La última ruta permite que links relativos desde `/dashboard/catalog` abran como:

```text
/dashboard/executive/ceo_brief.html
```

La función solo sirve `.html`, `.md`, `.txt` y `.json` desde `reports/generated_dashboards`.
