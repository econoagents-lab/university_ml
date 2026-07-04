# Machine Learning University · v2.4 Contract to Signature & Invoice Ops

Esta versión convierte propuestas aceptadas en expedientes comerciales operativos: orden de trabajo, hitos, entregables, calendario de implementación, proforma y seguimiento de pagos.

## Ejecutar

```powershell
python scripts/124_run_v24_contract_to_signature_and_invoice_ops.py
pytest -q tests/test_contract_to_signature_and_invoice_ops.py
```

O:

```powershell
.\run_contract_to_signature_and_invoice_ops.ps1 -RunTests -OpenIndex
```

## Abrir

- `reports/contract_ops/contract_ops_index.html`
- `reports/contract_ops/CONTRACT_TO_SIGNATURE_AND_INVOICE_OPS.md`

## Seguridad

No se incluyen `.env`, credenciales, clientes finales, DNI, teléfonos, emails ni códigos operativos CRM.
