# Production Data Privacy Policy v1.2.2

## Principio

Yo separo la verdad operativa del CRM de la exposición pública. La API pública puede mostrar agregados comerciales, pero nunca datos personales ni filas de clientes.

## Datos permitidos en Railway

```text
conteos agregados
valor total en riesgo
riesgo promedio
P0/P1 agregado
top proyectos agregados
top canales agregados
top asesores anonimizados
fecha de generación
data_mode crm
```

## Datos prohibidos

```text
cliente
documento
DNI
email
teléfono
nombre completo
dirección
credenciales
passwords
tokens
secretos
filas individuales
comentarios comerciales con PII
```

## Regla de producción

Yo no sirvo data demo si la variable `MLU_DISABLE_SAMPLE_FALLBACK=true` está activa en producción.

Esto evita que una demo en Railway parezca real cuando el payload CRM no existe.

## Validación automática

El script:

```text
scripts/70_validate_no_demo_data_in_production.py
```

falla si detecta:

- claves sensibles;
- patrones de DNI;
- patrones de teléfono;
- emails;
- palabras tipo `demo`, `sample`, `fake` o `synthetic`;
- `data_mode` distinto de `crm`.

## Política de nombres de asesores

Yo anonimizo asesores en payload público usando un hash estable. Eso permite ver concentración operativa sin exponer nombres personales.

## Checklist antes de publicar

```text
[ ] Existe reports/public/decision_dashboard_payload_public.json
[ ] data_mode = crm
[ ] No contiene cliente/documento/email/teléfono
[ ] top_asesores está anonimizado
[ ] Railway tiene MLU_ENV=production
[ ] Railway tiene MLU_DISABLE_SAMPLE_FALLBACK=true
[ ] GitHub Action Railway Public Payload Bridge pasa en verde
```
