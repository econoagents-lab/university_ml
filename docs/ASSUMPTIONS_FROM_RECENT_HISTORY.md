# Supuestos inferidos desde el historial reciente

> Estado: **BORRADOR OPERATIVO**. Este archivo llena lo que sí puede inferirse desde el historial del proyecto, la estructura Sperant/Redshift y las reglas Cygnus trabajadas recientemente. No reemplaza validación oficial con el dueño del proceso.

## 1. Principio

Un modelo de riesgo de caída no puede nacer de una tabla sin contrato. Este documento convierte las reglas repetidas en el historial del proyecto en un primer contrato ajustable.

La lógica viene de estos patrones ya trabajados:

- `procesos` es la tabla central para reconstruir separación, venta/minuta, caída/anulación, tubería, asesor, proyecto, unidad, cliente, fechas, estado y proforma.
- La capa de marts esperada incluye `fact_separaciones`, `fact_ventas`/`fact_firmas_minutas`, `fact_tuberia`, `fact_caidas`, `dim_clientes`, `dim_proyectos`, `dim_unidades`.
- El foco inicial del modelo debe ser **departamentos**, dejando estacionamientos, depósitos y locales como familias separadas.
- Toda predicción debe tener fecha de corte/snapshot para evitar leakage.
- El modelo no termina en score: termina en responsable, acción, SLA y feedback.

---

## 2. Reglas oficiales inferidas

### Separación válida

**Versión inferida:**

Una separación válida es un proceso con:

- `codigo_proforma` no nulo;
- `codigo_unidad` no nulo cuando la unidad sea parte del análisis;
- flujo/proceso que contenga separación;
- fecha oficial: `fecha_inicio`, salvo que el negocio confirme otra;
- se recomienda filtrar a `tipo_unidad_principal` de familia departamento para el primer modelo.

**Regla técnica flexible:**

```text
LOWER(nombre_flujo) contiene 'separ'
AND codigo_proforma IS NOT NULL
AND fecha_inicio IS NOT NULL
```

**Nota:** el historial menciona `procesos.nombre='Separación'`, pero en los parquets recientes `nombre` aparece anonimizado como unidad/código. Por eso la implementación usa `nombre_flujo` como fuente operativa primaria y deja `nombre` como fallback configurable.

---

### Venta / minuta válida

**Versión inferida:**

Una venta/minuta válida es un proceso de venta o minuta con:

- `codigo_proforma` no nulo;
- flujo/proceso que contenga `venta` o `minuta`;
- fecha oficial: máximo entre `fecha_fin`, `fecha_inicio` o `fecha_contrato`, según disponibilidad;
- se usa por `codigo_proforma` para saber si la separación convirtió.

**Regla técnica flexible:**

```text
LOWER(nombre_flujo) contiene 'proceso de venta' OR 'minuta'
AND codigo_proforma IS NOT NULL
AND fecha oficial de venta no nula
```

**Regla Power BI reciente a conservar:**

Cuando `flujo_separacion = 'Separación Oficial'` y `flujo_venta = 'Minuta Oficial'`, el flujo es correcto. Si `flujo_venta` está en blanco, pero `flujo_separacion = 'Separación Oficial'`, también debe tratarse como flujo correcto para el control de separación.

---

### Caída válida

**Versión inferida:**

Una caída válida es una operación con evidencia de anulación/caída:

- `fecha_anulacion` no nula; o
- `flujo_anulacion` contiene `Anulación`; o
- `nombre_flujo` contiene `Anulación`; o
- `momento_caida` indica `proceso` o `venta`.

**Fecha oficial de caída:**

1. `fecha_anulacion`, si existe;
2. `fecha_fin`, si el proceso de anulación está completado;
3. `fecha_inicio`, como fallback.

---

### Tubería válida

Una operación está en tubería en un snapshot si:

```text
fecha_separacion <= fecha_snapshot
AND no firmó antes o en fecha_snapshot
AND no cayó antes o en fecha_snapshot
```

Para scoring actual:

```text
fecha_separacion existe
AND fecha_firma es nula o posterior a hoy/snapshot
AND fecha_caida es nula o posterior a hoy/snapshot
```

---

### Horizonte de predicción

**Recomendación inferida:** `30 días`.

Razón: conecta con control comercial semanal/mensual y con la métrica generada en `caida_30d`. Para entrenamiento avanzado se pueden comparar 15, 30, 45 y 60 días, pero el MVP debe quedar en 30 días.

---

### Unidad de análisis

**Recomendación inferida:**

```text
Una separación activa por codigo_proforma + codigo_unidad + fecha_snapshot
```

Si una proforma contiene varias unidades, el modelo debe poder separar familias:

- departamento;
- estacionamiento;
- depósito;
- local;
- otro.

Para el primer modelo productivo: **solo departamentos**.

---

### Features permitidas inicialmente

Solo variables disponibles antes del snapshot:

- `proyecto`;
- `asesor`;
- `medio_captacion`;
- `canal_agrupado`;
- `dormitorios`;
- `precio_departamento`;
- `dias_en_tuberia`;
- `tiene_cuota_inicial`;
- `cambios_unidad`;
- `interacciones_ult_7d`;
- `descuento_pct`.

---

### Features prohibidas inicialmente

Nunca deben entrar a `X`:

- `fecha_caida`;
- `motivo_caida`;
- `momento_caida`;
- `flujo_anulacion`;
- `fecha_anulacion`;
- `fecha_firma` futura;
- `fecha_minuta` futura;
- `estado_final`;
- cualquier pago posterior al snapshot;
- cualquier estado de cobranza posterior al snapshot.

---

### Umbrales de decisión inferidos

| Score | Nivel | Acción | Responsable | SLA |
|---:|---|---|---|---|
| 0.00–0.39 | Bajo | Seguimiento estándar | Asesor | Semana |
| 0.40–0.69 | Medio | Contacto priorizado | Asesor | 24 horas |
| 0.70–1.00 | Alto | Escalamiento comercial | Jefe comercial | Hoy |

---

### Costo económico inicial

Hasta confirmar costos reales, usar proxy:

```text
valor_en_riesgo = probabilidad_caida * precio_departamento
```

Costo de falso negativo mayor que falso positivo:

- Falso negativo: operación cae sin intervención → venta/caja potencial perdida.
- Falso positivo: operación recibe seguimiento extra → costo operativo bajo/moderado.

---

## 3. TODO que sigue abierto

Estos puntos deben confirmarse en el siguiente input o con gerencia/operaciones:

1. Si `estado='Activo'` debe ser obligatorio en separación válida o si separaciones históricas inactivas también deben entrar al entrenamiento.
2. Si la fecha oficial de venta debe ser `fecha_fin`, `fecha_inicio`, `fecha_contrato`, `fecha_minuta` o una combinación.
3. Si cambios de departamento/proyecto deben contar como caída, evento separado o exclusión.
4. Si anulaciones de estacionamientos/depositos deben entrar a otro modelo.
5. Umbrales reales según capacidad diaria de asesores/jefe comercial.
6. Costos reales de intervención, caída y recuperación.
7. Lugar oficial del feedback loop: Parquet, Postgres/Supabase, Power BI o tabla Sperant externa.

