# TODO · Información que falta para la siguiente iteración

Estas piezas no deben inventarse. Deben venir del negocio, de Sperant/Redshift o de tus reglas operativas.

---

## 1. Reglas exactas de procesos

Necesito que confirmes:

- Nombre exacto del flujo de separación oficial.
- Nombre exacto del flujo de venta/minuta oficial.
- Nombre exacto del flujo de anulación/caída.
- Estados que deben incluirse o excluirse.
- Qué procesos antiguos deben considerarse “flujo anterior”.

Formato sugerido:

```text
Separación válida = ...
Venta/minuta válida = ...
Caída válida = ...
Excluir = ...
```

---

## 2. Definición oficial de caída

Confirmar:

- ¿Caída incluye separación caída antes de minuta?
- ¿Incluye minuta anulada?
- ¿Incluye cambio de unidad?
- ¿Incluye desistimiento financiero?
- ¿Cuál es la fecha oficial de caída?

---

## 3. Horizonte de predicción

Elegir uno:

```text
15 días
30 días
45 días
60 días
```

Recomendación actual: 30 días.

---

## 4. Unidad de análisis

Confirmar si el modelo debe predecir por:

```text
codigo_proforma
codigo_proforma + codigo_unidad
cliente + proyecto
separación principal solamente
```

Recomendación actual: `codigo_proforma + codigo_unidad + fecha_snapshot`.

---

## 5. Tipos de unidad

Confirmar clasificación final:

```text
departamento
estacionamiento
depósito
local
otro
```

Recomendación actual: entrenar primero solo departamentos.

---

## 6. Features disponibles antes del snapshot

Confirmar si existen y cómo se llaman:

- interacciones comerciales;
- fecha de último contacto;
- monto de cuota inicial pagado antes del snapshot;
- cambios de unidad;
- evaluación financiera;
- banco/crédito;
- motivo de demora;
- canal inicial y canal de cierre.

---

## 7. Umbrales de decisión

Validar con negocio:

```text
riesgo alto >= 0.70
riesgo medio >= 0.40
riesgo bajo < 0.40
```

Necesito saber la capacidad diaria real del equipo para intervenir operaciones.

---

## 8. Costos económicos

Ingresar o estimar:

- Valor promedio de venta perdida.
- Margen estimado o proxy de caja.
- Costo de seguimiento extra.
- Costo de escalamiento gerencial.

---

## 9. Feedback loop

Confirmar dónde guardar:

```text
PostgreSQL / Supabase
Parquet local
Excel temporal
Power BI table
```

Recomendación: empezar Parquet local, luego Postgres/Supabase.

---

## 10. Despliegue

Confirmar target:

```text
solo local
Railway
Render
Supabase Edge + API externa
servidor/laptop 24/7
```

Recomendación actual: local primero + Railway cuando API esté estable.
