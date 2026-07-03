# Machine Learning University v1.1 · UNI Final RAG Economic Hypothesis Pack

Esta versión convierte la plataforma de ML inmobiliario en un entregable final para UNI: un **Sistema RAG vertical de dominio inmobiliario** con hipótesis económicas, corpus propio, FAISS/fallback vectorial, guardrails, Text-to-SQL, evaluación RAGAS-like y demo Gradio.

## Qué problema resuelve

Yo construyo un asistente que permite consultar y explicar decisiones comerciales inmobiliarias: riesgo de caída, conversión, tubería, pricing, stock, drift y acciones comerciales. El sistema responde con evidencia recuperada, citas y restricciones de seguridad.

## Modo seguro

No incluyo `.env`, credenciales ni datos personales reales. El corpus incluido es `sample_safe` y está anonimizado para evaluación académica.

## Ejecución rápida

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/51_run_v11_uni_final_rag_pack.py
pytest -q
```

## Notebook final UNI

```text
notebooks/UNI_Final_RAG_Asistente_Economico_Inmobiliario.ipynb
```

## Demo Gradio

```powershell
python app/gradio_app.py
```

## Artefactos principales

```text
reports/uni_final/
├── RAGAS_LIKE_RESULTS.csv
├── RAGAS_LIKE_SUMMARY.md
├── BENCHMARK_BASE_VS_ADVANCED.md
├── DEMO_ANSWERS.md
└── FINAL_TECHNICAL_REPORT.md
```

## Comentarios en primera persona

Los módulos nuevos tienen comentarios y docstrings en primera persona. Ejemplo:

```python
# Yo limpio el corpus antes de indexarlo para evitar exponer PII.
```
