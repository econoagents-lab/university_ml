# v2.4 · Contract to Signature & Invoice Ops

Esta versión convierte una propuesta aceptada en un expediente operativo: orden de trabajo, hitos, entregables, proforma, calendario de pagos y seguimiento de avance.

## Principio

El sistema no debe morir en una propuesta bonita. Debe terminar en ejecución, caja y cierre.

```text
propuesta aceptada
→ orden de trabajo
→ hitos
→ calendario de implementación
→ entregables
→ factura/proforma
→ seguimiento de avance
→ cierre comercial
```

## Outputs principales

- `reports/contract_ops/contract_ops_index.html`
- `reports/contract_ops/CONTRACT_OPS_INDEX.md`
- `reports/contract_ops/<tenant>/work_order.md`
- `reports/contract_ops/<tenant>/work_order.html`
- `reports/contract_ops/<tenant>/invoice_proforma.json`
- `reports/contract_ops/<tenant>/payment_schedule.csv`
- `reports/contract_ops/<tenant>/deliverables_register.csv`
- `reports/contract_ops/<tenant>/contract_ops_package.json`

## Seguridad

No se exportan clientes finales, DNI, teléfonos, emails, direcciones, códigos de proforma, unidades ni credenciales. Los artifacts usan metadata comercial del tenant, hitos, precios y entregables.
