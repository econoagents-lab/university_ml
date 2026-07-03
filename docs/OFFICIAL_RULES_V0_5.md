# Official Rules v0.5 - Riesgo de Caída

Esta versión congela reglas inferidas como borrador oficial operativo. No es todavía firma final de negocio, pero sí es suficiente para entrenar, evaluar y servir un modelo gobernado.

## Regla central

El modelo predice `caida_30d`: separación activa que cae dentro de los 30 días posteriores al snapshot.

## Grano

`codigo_proforma + codigo_unidad + fecha_snapshot`

## Política anti-leakage

El dataset de auditoría puede contener fechas de futuro para trazabilidad. El dataset model-ready no.

```text
gold audit/debug -> puede contener fecha_caida para auditoría
gold model-ready -> NO puede contener fecha_caida ni fecha_firma
X del modelo -> falla si contiene columnas prohibidas
```
