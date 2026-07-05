# Core Value Hardening v2.7

Esta versión corrige las debilidades detectadas en la auditoría ejecutiva:

1. P0/P1 se calcula por capacidad comercial, no por umbral bruto.
2. El modelo se comunica como ranking gobernado, no como predicción de alta precisión.
3. El dashboard público se anonimiza por defecto para evitar exposición competitiva.
4. La demo se reduce a una historia ejecutiva de valor.
5. Se crea un scorecard de defendibilidad económica.

## Puertas maestras

- `/dashboard/executive-value-brief`
- `/public/decision-dashboard`
- `/decision/riesgo-caida/capacity-queue`
- `/metadata/core-value-hardening`

## Regla de producto

No seguir construyendo superficie hasta ejecutar `CORE_ANALYTICS_30D_PLAN_v1` sobre CRM privado y validar cohortes, stock/cobranza, feedback y recalibración.
