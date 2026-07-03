# Machine Learning University - Bitacora Ejecutiva

Proyecto: C:\Repos\freelance\ml_university_ready
Fecha de ejecucion: 2026-07-03 01:24:48
Modo: sperant
Readiness: red

## 1. Resumen ejecutivo

Pasos ejecutados: 6
Pasos correctos: 2
Pasos fallidos: 4
Advertencias: 0

Interpretacion:
- El proyecto aun no esta listo para ser tratado como pipeline confiable. Revisar advertencias y logs.

## 2. Inventario del datacenter local

| Area | Valor |
|---|---:|
| Parquet raw | 0 |
| Parquet processed | 0 |
| CSV | 3 |
| Modelos | 1 |
| Contratos | 8 |
| Notebooks | 16 |
| Scripts Python | 12 |
| Archivos API | 3 |
| Docs Markdown | 20 |
| Size raw MB | 0 |
| Size processed MB | 0 |

## 3. Pasos ejecutados

| Paso | Estado | Exit code | Duracion seg | Log |
|---|---|---:|---:|---|
| Validate foundations | success | 0 | 1.85 | reports\executive_runs\20260703_012428\logs\10_validate_foundations.log |
| Build inferred rules gold table | failed |  | 1.65 | reports\executive_runs\20260703_012428\logs\11_build_inferred_rules.log |
| Extract Redshift to Parquet | failed |  | 4.85 | reports\executive_runs\20260703_012428\logs\20_extract_redshift.log |
| Profile Sperant sources | success | 0 | 4.77 | reports\executive_runs\20260703_012428\logs\21_profile_sperant_sources.log |
| Build Sperant training dataset | failed |  | 1.45 | reports\executive_runs\20260703_012428\logs\22_build_sperant_training.log |
| Train from Sperant | failed |  | 5.21 | reports\executive_runs\20260703_012428\logs\23_train_sperant.log |

## 4. Artefactos detectados

| Artefacto | Existe | KB |
|---|---|---:|
| reports\foundations\foundation_audit_riesgo_caida.json | True | 0.62 |
| reports\foundations\inferred_rules_build_report.json | False | 0 |
| reports\sperant_profile.json | False | 0 |
| reports\model_report.json | False | 0 |
| models\model_card.md | True | 0.72 |

## 5. Advertencias

- Sin advertencias.

## 6. Recomendaciones ejecutivas

- Add or extract real Sperant parquet files into data/raw/sperant for real-data training.

## 7. Proximo input recomendado

Copiar y completar:

```text
Quiero continuar Machine Learning University.
Adjunto o confirmo:
1. Reglas oficiales de separacion, venta/minuta y caida.
2. Horizonte final del target: 15, 30, 45 o 60 dias.
3. Grano oficial: codigo_proforma, codigo_unidad, o ambos.
4. Features permitidas antes del snapshot.
5. Umbrales bajo/medio/alto y capacidad comercial diaria.
6. Costos economicos de falso positivo y falso negativo.
7. Destino del feedback loop: parquet, Postgres, Supabase o Power BI.
```

## 8. Ubicaciones

Manifest JSON: C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_012428\run_manifest.json
Logs: C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_012428\logs
Artifacts: C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_012428\artifacts
