# Checklist para congelar reglas oficiales

Antes de llamar “oficial” a v0.4, marcar cada punto.

## Contratos

- [ ] Separación válida confirmada por Comercial/Operaciones.
- [ ] Venta/minuta válida confirmada por Comercial/Legal/Administración.
- [ ] Caída válida confirmada por Comercial/Operaciones.
- [ ] Tratamiento de cambio de departamento/proyecto confirmado.
- [ ] Tipos de unidad confirmados: departamento, estacionamiento, depósito, local, otro.
- [ ] Grano oficial confirmado: `codigo_proforma + codigo_unidad + fecha_snapshot`.
- [ ] Horizonte oficial confirmado: 30 días.

## Anti-leakage

- [ ] Ninguna columna futura entra a `X`.
- [ ] `fecha_caida`, `motivo_caida`, `fecha_anulacion`, `flujo_anulacion` quedan solo para auditoría/target.
- [ ] Features de pago/cobranza se calculan solo hasta snapshot.

## Decisión económica

- [ ] Umbrales de bajo/medio/alto validados con capacidad comercial.
- [ ] Responsable por nivel validado.
- [ ] SLA validado.
- [ ] Feedback loop definido.

## Producción

- [ ] Script construye gold table.
- [ ] Auditoría de fundamentos pasa.
- [ ] Tests pasan.
- [ ] API devuelve score + acción + responsable + valor en riesgo.
