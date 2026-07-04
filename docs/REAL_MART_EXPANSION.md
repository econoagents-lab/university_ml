# Real Mart Expansion v1.6

Hoy no reemplazo dashboards: reemplazo dudas. La versión v1.6 crea marts reales, agregados y seguros para que la fábrica deje de usar proxies donde ya existe evidencia dura.

## Qué agrega

- `mart_funnel_stage_month.csv`: tasas por etapa desde leads/conversiones cuando existe fuente.
- `mart_cobranza_venta.csv`: avance de cobranza por mes/proyecto sin datos personales.
- `mart_stock_inicial_mensual.csv`: stock por mes/proyecto/tipo de unidad desde unidades.
- `mart_pricing_unit_m2.csv`: precio/m² por unidad con `unit_id` hasheado.
- `mart_project_vs_market.csv`: brecha precio/m² contra mercado o benchmark interno declarado.
- `mart_feedback_interventions.csv`: feedback comercial agregado con responsable hasheado.
- `mart_proxy_vs_official_gap.csv`: control de qué proxy fue reemplazado por mart real.

## Política de privacidad

No se exporta cliente, DNI, documento, email, teléfono, dirección, credenciales ni filas operativas individuales con identidad personal. Cuando una dimensión necesita trazabilidad operativa, se usa hash estable.

## Cómo usar data privada

Coloca parquets/CSVs privados fuera de Git o define:

```powershell
$env:MLU_PRIVATE_DATA_DIR="C:\\ruta\\privada\\crm"
python scripts/88_run_v16_real_mart_expansion.py
```

También puedes ejecutar:

```powershell
.\\run_real_mart_expansion.ps1 -PrivateDataDir "C:\\ruta\\privada\\crm" -RunTests -OpenReport
```

## Decisión de arquitectura

- Lenovo: corre extracción CRM real y genera marts privados/agregados.
- GitHub: valida y publica artifacts seguros.
- Railway: sirve solo payload público agregado, nunca CRM crudo.
