# Productized Commercial Intelligence OS v2.0

## La tesis
Yo no empaqueto scripts: empaqueto una forma de operar comercialmente con evidencia. El sistema une API, dashboards, RAG, GitHub Actions, Railway, feedback, experimentos y política comercial.

## Arquitectura de producto

```text
CRM privado / parquets raw
→ marts reales y seguros
→ scoring y ranking
→ cola de acciones
→ dashboards por catálogo
→ payload público Railway
→ RAG con evidencia
→ GitHub alerts
→ feedback 7d/30d
→ experimento y política
```

## Reglas de seguridad
- Railway sirve solo agregados.
- Lenovo o self-hosted runner procesa CRM privado.
- GitHub artifacts no deben contener CRM crudo.
- La API pública no expone clientes, DNI, teléfono, email, dirección ni credenciales.

## Módulos vendibles
1. CEO Brief & Decision Cockpit.
2. Risk-to-Action Queue.
3. Railway Public Safe Dashboard.
4. RAG Business Memory.
5. Real Mart Evidence Layer.
6. Experiment & Policy Engine.
7. GitHub Alerts & Automation Tower.
