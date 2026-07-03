# Contratos de datos anonimizados

## Separación válida

Una separación válida requiere operación identificable, fecha de separación, proyecto, unidad y estado comercial coherente.

## Minuta válida

Una minuta válida representa un avance formal de venta. Debe tener fecha oficial, proyecto y relación con la separación correspondiente.

## Caída válida

Una caída válida representa una anulación o desistimiento documentado. Para modelar riesgo, la fecha de caída se usa solo para construir el target y auditoría, nunca como feature.

## Tubería

La tubería corresponde a separaciones activas sin minuta final ni caída registrada al momento del corte.

## Anti-leakage

Las columnas futuras pueden existir en raw o auditoría, pero nunca en model-ready, matriz X, scoring ni RAG sensible.
