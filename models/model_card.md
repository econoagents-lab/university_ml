# Model Card - Riesgo de Caída v0.5

- Modelo: riesgo_caida_model
- Versión: 0.5.0-official_rules
- Target: caida_30d
- Uso: priorizar separaciones activas con riesgo de caída en 30 días.

## Métricas

| Métrica | Valor |
|---|---:|
| ROC AUC | 0.499 |
| Average Precision | 0.112 |
| Precision | 0.095 |
| Recall | 0.844 |
| F1 | 0.171 |

## Features

```json
[
  "proyecto",
  "asesor",
  "medio_captacion",
  "canal_agrupado",
  "dormitorios",
  "precio_departamento",
  "dias_en_tuberia",
  "tiene_cuota_inicial",
  "cambios_unidad",
  "interacciones_ult_7d",
  "descuento_pct"
]
```

## Limitaciones

No usar para decisiones automáticas de anulación ni evaluación punitiva de asesores.
