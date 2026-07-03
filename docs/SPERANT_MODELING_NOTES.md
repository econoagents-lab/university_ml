# Notas de modelamiento · Riesgo de Caída con Sperant

## Problema que resolvemos

No queremos predecir por curiosidad. Queremos responder: ¿qué operaciones vivas pueden caer y qué responsable debe actuar antes de perder valor de venta?

## Grano correcto

Una fila no debe ser “cliente” ni “proyecto”. Una fila debe ser:

```text
operación inmobiliaria + unidad + snapshot temporal
```

Ejemplo:

```text
Proforma 2026-0000001 / Unidad A1202 / snapshot día 14 después de separación
```

## Trampa principal: leakage

No se debe usar como feature:

- fecha_caida
- motivo_caida
- estado final
- fecha_firma futura
- observaciones posteriores al snapshot

## Mejoras futuras

1. Incorporar pagos reales de cuota inicial por fecha.
2. Incorporar interacciones comerciales antes del snapshot.
3. Diferenciar departamentos, estacionamientos, depósitos y locales.
4. Entrenar modelos separados por familia de unidad si hay volumen.
5. Medir ganancia económica: ventas salvadas / ventas en riesgo intervenidas.
