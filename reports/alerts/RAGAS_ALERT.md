# ⚠️ RAG Quality Gate

- Severidad: **WARNING**
- Fuente: `/mnt/data/machine_learning_university_v1_2_1_fix_colab_and_soft_gates/reports/uni_final/RAGAS_LIKE_SUMMARY.md`

## Checks
- ✅ `faithfulness_proxy_mean` = 0.8444 | mínimo = 0.75
- ❌ `answer_relevance_proxy_mean` = 0.2045 | mínimo = 0.55
- ✅ `context_relevance_proxy_mean` = 0.6 | mínimo = 0.6
- ❌ `trap_refusal_rate` = 0.6667 | mínimo = 1.0

## Recomendación
Yo revisaría recuperación, citas y preguntas trampa antes de presentar. Métricas débiles: answer_relevance_proxy_mean, trap_refusal_rate.