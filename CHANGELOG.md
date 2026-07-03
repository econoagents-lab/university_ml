# Changelog

## v0.1.0

- Proyecto end-to-end generado.
- 8 notebooks base con estructura pedagógica fija.
- Data sintética inmobiliaria.
- Pipeline de entrenamiento.
- API FastAPI.
- Contratos YAML.
- Tests mínimos.
- GitHub Actions.
- Model card.
- Control de avance progresivo.

## [0.2.0] - Sperant/Redshift Adaptation

### Added
- Conector Redshift seguro vía `.env`.
- Extractor a Parquet local: `scripts/00_extract_redshift_to_parquet.py`.
- Perfilador de fuentes: `scripts/09_profile_sperant_sources.py`.
- Adaptador Sperant para construir `gold.riesgo_caida_training`.
- Entrenamiento con gold table real: `scripts/11_train_from_sperant.py`.
- Contratos fuente y contrato de training dataset.
- Diccionario inicial de esquemas Sperant/Redshift.
- Endpoint batch y endpoints de metadata/contratos.

### Security
- `.env` y data real siguen excluidos del ZIP/Git por diseño.


## v0.3.0-foundations

### Added

- Capa de fundamentos para Data Science real.
- Model brief formal para riesgo de caída.
- Guía anti-leakage.
- Matriz de costo de errores.
- Protocolo de experimentación.
- Playbook de decisión por umbrales.
- Contrato de decisión y contrato anti-leakage en YAML.
- Módulo `src/mlu/foundations.py`.
- Script `scripts/12_validate_foundations.py`.
- Tests de fundamentos.
- `TODO_NEXT_INPUT.md` y plantilla para capturar reglas que no deben inventarse.

## v0.4.0-inferred-rules

### Added

- Reglas de negocio inferidas desde historial reciente Cygnus/Sperant.
- Documento `ASSUMPTIONS_FROM_RECENT_HISTORY.md` con separación, venta/minuta, caída, tubería, unidad de análisis, features, umbrales y TODO.
- Documento `TODO_NEXT_INPUT_FILLED_FROM_HISTORY.md` prellenado para que el usuario ajuste y congele reglas.
- Checklist `RULES_FREEZE_CHECKLIST.md` para pasar de borrador operativo a contrato oficial.
- Contrato YAML `contracts/inferred_business_rules_cygnus_sperant.yml`.
- Config YAML `config/business_rules_inferred.yml`.
- Módulo `src/mlu/business_rules.py` con reglas ejecutables.
- Script `scripts/13_build_from_inferred_rules.py` para crear gold table desde `procesos.parquet`.
- Tests para reglas inferidas.

### Changed

- La universidad ahora puede avanzar con reglas inferidas sin esperar al input perfecto, pero marca explícitamente qué debe revisarse.

### Warning

- v0.4 no declara reglas oficiales. Declara reglas inferidas auditables y ajustables.
