# Criterios de aceptación

El proyecto está cerrado cuando:

1. `python scripts/01_generate_sample_data.py` genera datos sintéticos.
2. `python scripts/02_train_model.py` entrena y guarda un modelo.
3. `pytest` pasa tests mínimos.
4. `uvicorn api.main:app --reload` levanta Swagger.
5. `/predict/riesgo-caida` responde score, nivel, decisión y responsable.
6. Cada notebook contiene las 12 secciones pedagógicas obligatorias.
7. El repositorio no contiene `.env` ni datos reales.
8. Existe model card con objetivo, datos, features, métricas, riesgos y decisión económica.


---

## v0.3 · Foundations Acceptance Criteria

- [x] Existe documento de fundamentos.
- [x] Existe model brief de riesgo de caída.
- [x] Existe guía anti-leakage.
- [x] Existe matriz de costo de errores.
- [x] Existe contrato de decisión.
- [x] Existe contrato anti-leakage.
- [x] Existe script de auditoría de fundamentos.
- [x] Existen tests de fundamentos.
- [x] Existe listado de insumos que no deben inventarse para la siguiente iteración.

---

## v0.4 · Acceptance Criteria

- [ ] Existe `docs/ASSUMPTIONS_FROM_RECENT_HISTORY.md`.
- [ ] Existe `docs/TODO_NEXT_INPUT_FILLED_FROM_HISTORY.md`.
- [ ] Existe `contracts/inferred_business_rules_cygnus_sperant.yml`.
- [ ] Existe `src/mlu/business_rules.py`.
- [ ] Existe `scripts/13_build_from_inferred_rules.py`.
- [ ] El script puede construir una gold table desde `data/raw/sperant/procesos.parquet`.
- [ ] La gold table resultante mantiene grano `codigo_proforma + codigo_unidad + fecha_snapshot`.
- [ ] La matriz del modelo excluye columnas prohibidas.
- [ ] Los tests de reglas inferidas pasan.
- [ ] El usuario puede corregir reglas en un siguiente input sin rearmar el proyecto desde cero.
