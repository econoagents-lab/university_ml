# Data Quality

**Familia:** `data_quality`  
**Owner:** CDO / Analytics Engineering  
**Audiencia:** Data Team  
**Prioridad:** governance  
**Estado:** cataloged

## Pregunta económica

¿Qué tablas tienen nulos, duplicados o llaves rotas?

## KPIs agregados disponibles

- Total operaciones: **763**
- Valor total en riesgo: **S/ 21,232,580.48**
- Riesgo promedio: **0.398**
- Operaciones P0/P1: **{'operaciones': 761, 'valor_en_riesgo': 21191194.15}**
- Data mode: **crm**
- Fecha generación KPI: **2026-07-04T20:10:16**

## Top proyectos agregados

| proyecto | operaciones | valor_en_riesgo | riesgo_promedio | p0_p1 |
| --- | --- | --- | --- | --- |
| Tizón y Bueno | 82 | 2769922.88 | 0.5073 | 82 |
| Edificio Cuba Connect | 83 | 1986299.7 | 0.2822 | 83 |
| Edificio Urbanzen | 45 | 1783878.84 | 0.4903 | 45 |
| Edificio Santa Cruz Infinite | 84 | 1772295.82 | 0.2639 | 84 |
| Modena | 53 | 1672002.71 | 0.4932 | 53 |

## Top asesores agregados

| asesor_anon | operaciones | valor_en_riesgo | riesgo_promedio | p0_p1 |
| --- | --- | --- | --- | --- |
| Asesor_26DEBB0E | 130 | 4395201.77 | 0.4635 | 130 |
| Asesor_10B2BE3F | 216 | 3678489.2 | 0.2044 | 216 |
| Asesor_C931A67B | 66 | 2219467.94 | 0.4375 | 65 |
| Asesor_1F3B24E1 | 58 | 1961023.49 | 0.5103 | 58 |
| Asesor_B56EAA59 | 58 | 1892075.93 | 0.5045 | 58 |

## Top canales agregados

| canal | operaciones | valor_en_riesgo | riesgo_promedio | p0_p1 |
| --- | --- | --- | --- | --- |
| sin_clasificar | 763 | 21232580.48 | 0.3982 | 761 |

## Métricas específicas de esta familia

| Métrica | Valor |
|---|---|
| `metric_group` | executive |
| `status` | ok |
| `decision` | Yo combino riesgo, RAG y MLOps para decidir qué debe revisar gerencia. |

## Acción recomendada

Usar el tablero para convertir datos en decisión, responsable, plazo y métrica de resultado.

## Donde cambiar

`contracts/data_contract_riesgo_caida.yml`

## Parámetros actuales usados como contexto

```yaml
name: data_contract_riesgo_caida
version: 0.6.1
owner: Chief Data Officer + Chief Economist
contract_type: raw_or_audit_learning_dataset
business_question: ¿Qué separaciones tienen mayor riesgo de caída a 30 días?
grain: una fila por operación/separación o una fila por operación/snapshot según fuente
source_type: synthetic_or_sperant_gold_audit
privacy: no debe contener PII en repositorio
model_ready_contract: contracts/model_ready_contract_riesgo_caida.yml
columns:
- name: proyecto
  type: string
  required: true
- name: asesor
  type: string
  required: true
- name: medio_captacion
  type: string
  required: true
- name: canal_agrupado
  type: string
  required: true
- name: dormitorios
  type: integer
  required: true
- name: precio_departamento
  type: float
  required: true
- name: dias_en_tuberia
  type: integer
  required: true
- name: tiene_cuota_inicial
  type: boolean
  required: true
- name: cambios_unidad
  type: integer
  required: true
- name: interacciones_ult_7d
  type: integer
  required: true
- name: descuento_pct
  type: float
  required: true
- name: caida_30d
  type: integer
  required: true
  description: Variable objetivo. 1 si la separación cae dentro del horizonte definido.
audit_columns_allowed_in_raw_not_model_ready:
- fecha_caida
- fecha_firma
- motivo_caida
- fecha_anulacion
quality_rules:
- precio_departamento > 0
- dias_en_tuberia >= 0
- caida_30d in [0, 1]
- audit columns may exist only before model-ready transformation
output:
  audit_gold_table: gold.fact_riesgo_caida_training
  model_ready_table: gold.riesgo_caida_training_model_ready
  model_endpoint: /predict/riesgo-caida
  decision_owner: asesor_comercial

```

## Regla de gobierno

Yo genero este dashboard desde `config/dashboard_catalog.yml` y sus parámetros asociados. Si cambia la decisión económica, cambio configuración; no reescribo el tablero a mano.
