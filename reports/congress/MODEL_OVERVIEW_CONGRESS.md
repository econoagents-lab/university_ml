# Model Overview para Congreso · Riesgo de Caída Inmobiliaria

## Título sugerido

De CRM operativo a Machine Learning gobernado: predicción de riesgo de caída inmobiliaria con anti-leakage, monitoreo, feedback y model registry.

## Problema

Las separaciones inmobiliarias pueden caer antes de convertirse en venta/minuta. La pregunta no es solo predictiva: es operativa y económica.

> ¿Qué operaciones activas tienen mayor probabilidad de caer en los próximos 30 días y deben priorizar seguimiento comercial?

## Arquitectura

```text
Sperant / Redshift / Parquets locales
→ gold audit/debug
→ model-ready anti-leakage
→ feature table
→ champion/challenger
→ registry
→ scoring actual
→ feedback loop
→ monitoring/retraining
```

## Champion actual

| Campo | Valor |
|---|---|
| Model ID | `riesgo_caida_random_forest_dataset_riesgo_caida_crm_2026_07_03_v001_c02` |
| Algoritmo | `random_forest` |
| Dataset version | `dataset_riesgo_caida_crm_2026_07_03_v001` |
| Data mode | `crm` |

## Métricas principales

| Métrica | Valor |
|---|---:|
| ROC AUC | 0.524 |
| Average Precision | 0.116 |
| Precision | 0.091 |
| Recall | 0.961 |
| F1 | 0.166 |
| Top Decile Lift | 0.779 |

## Aporte metodológico

1. El diseño separa columnas raw, auditables, target y model-ready.
2. La columna `fecha_caida` puede existir para auditoría y construcción del target, pero no entra a X.
3. El sistema no elige modelos por intuición: usa champion/challenger y policy de retraining.
4. El ranking se controla con monitoreo de drift y calibración.
5. La salida no es un score aislado: es una priorización comercial con responsable y feedback.

## Figuras incluidas

- `reports/figures/congress/01_problem_funnel.png`
- `reports/figures/congress/02_target_distribution.png`
- `reports/figures/congress/03_temporal_split.png`
- `reports/figures/congress/04_anti_leakage_architecture.png`
- `reports/figures/congress/05_roc_curve.png`
- `reports/figures/congress/06_pr_curve.png`
- `reports/figures/congress/07_confusion_matrix.png`
- `reports/figures/congress/08_lift_deciles.png`
- `reports/figures/congress/09_calibration_curve.png`
- `reports/figures/congress/10_drift_heatmap.png`
- `reports/figures/congress/11_champion_vs_challenger.png`
- `reports/figures/congress/12_feature_importance.png`
- `reports/figures/congress/13_intervention_effect.png`
