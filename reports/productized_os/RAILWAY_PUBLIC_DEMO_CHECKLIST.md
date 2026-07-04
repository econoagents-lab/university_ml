# Railway Public Demo Checklist

- [ ] `MLU_ENV=production`.
- [ ] `MLU_DISABLE_SAMPLE_FALLBACK=true`.
- [ ] Existe `reports/public/decision_dashboard_payload_public.json`.
- [ ] El payload público tiene `data_mode=crm`.
- [ ] No contiene clientes, DNI, teléfonos, emails, direcciones ni credenciales.
- [ ] `/public/decision-dashboard` responde sin filas individuales.
- [ ] `/metadata/productized-os` responde con estado del release.
- [ ] GitHub Actions sube artifacts agregados, no CRM crudo.