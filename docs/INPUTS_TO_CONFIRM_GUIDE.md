# Guía de Inputs a Confirmar

Este documento explica cómo usar `reports/dashboard_control/INPUTS_TO_CONFIRM.md`.

Cada input representa una decisión de negocio o seguridad. La columna `Donde cambiar` indica el archivo exacto que debo modificar.

## Regla operativa

Si una métrica cambia por conversación gerencial, no debo tocar scripts primero. Debo buscar el parámetro, ajustar YAML, correr validación y recién regenerar outputs.

## Flujo

```text
pregunta gerencial
→ parámetro editable
→ contrato/config
→ validación
→ dashboard/report/API
```
