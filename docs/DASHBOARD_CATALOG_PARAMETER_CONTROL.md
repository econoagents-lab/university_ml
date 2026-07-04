# Dashboard Catalog Parameter Control v1.3

Hoy el sistema deja de ser una colección de reportes y se convierte en un catálogo gobernado de productos de decisión.

## Principio

Yo no cambio código para mover la estrategia comercial. Cambio contratos, parámetros y umbrales.

## Archivos centrales

- `config/dashboard_catalog.yml`: inventario de dashboards y productos de decisión.
- `config/dashboard_params.yml`: parámetros editables por dashboard.
- `config/model_params.yml`: horizontes, thresholds y reglas del modelo.
- `config/privacy_policy.yml`: política de datos públicos, PII y Railway.
- `config/market_sources.yml`: fuentes externas de mercado.
- `reports/dashboard_control/DASHBOARD_CONTROL_PANEL.md`: panel maestro generado.
- `reports/dashboard_control/INPUTS_TO_CONFIRM.md`: inputs críticos con columna `Donde cambiar`.

## Decisiones tomadas

- Railway solo muestra payload agregado CRM, no CRM live.
- Lenovo queda como runner privado para CRM completo.
- GitHub Actions conserva artifacts agregados o anonimizados.
- Proyectos pueden mostrarse en público solo como agregados.
- Asesores no se muestran reales en público; se anonimizan.
- Canales pueden mostrarse agregados.
- Valor en riesgo puede mostrarse agregado.
- Top operaciones, clientes, DNI, teléfonos, emails, direcciones y credenciales nunca se publican.
- RAG consulta solo tablas anonimizadas o agregadas.

## Ejecución

```powershell
python scripts/76_run_v13_dashboard_control.py
pytest -q
```
