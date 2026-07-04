# Runbook · Contract Ops

## Ejecutar

```powershell
python scripts/124_run_v24_contract_to_signature_and_invoice_ops.py
pytest -q tests/test_contract_to_signature_and_invoice_ops.py
```

## Flujo recomendado

1. Generar propuestas v2.3.
2. Confirmar paquete y precio en `config/client_proposals.yml`.
3. Ajustar términos en `config/contract_ops.yml`.
4. Ejecutar v2.4.
5. Revisar `reports/contract_ops/contract_ops_index.html`.
6. Enviar orden de trabajo y proforma al cliente.
7. Registrar pago inicial.
8. Agendar kickoff.

## Dónde cambiar

| Input | Donde cambiar |
|---|---|
| Moneda | `config/contract_ops.yml > contract_ops_engine.currency` |
| Impuesto | `config/contract_ops.yml > contract_ops_engine.default_tax_pct` |
| Serie de proforma | `config/contract_ops.yml > contract_ops_engine.invoice_series` |
| Porcentaje inicial | `config/contract_ops.yml > invoice_rules.upfront_pct` |
| Hitos | `config/contract_ops.yml > milestone_templates` |
| Entregables | `config/contract_ops.yml > deliverable_templates` |
| Precio | `config/client_proposals.yml > packages` |
