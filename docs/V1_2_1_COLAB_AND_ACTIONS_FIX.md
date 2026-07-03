# v1.2.1 · Colab and GitHub Actions Soft Gates Fix

## Qué corregí

1. Corregí el notebook final `UNI_Final_RAG_Asistente_Economico_Inmobiliario.ipynb`.
   - El error venía de una celda con `print("` y un salto de línea antes de `CITAS:`.
   - Ahora queda como `print("\\nCITAS:")`.

2. Cambié `rag_quality_gate.yml` para que las alertas RAG no fallen el workflow por defecto.
   - Antes, una alerta `warning` generaba issue/artifacts y luego fallaba con exit code 2.
   - Ahora el workflow avisa, publica summary, crea issue si corresponde y queda verde por defecto.
   - Si quiero bloquear a propósito, ejecuto manualmente el workflow con `fail_on_alert=true`.

3. Agregué un test de sintaxis del notebook.
   - `tests/test_notebook_syntax.py` compila las celdas de código del notebook final.
   - Esto evita volver a subir a Colab un notebook con strings incompletos.

## Cómo validar

```powershell
python scripts/66_build_all_alerts.py
python scripts/68_export_alerts_static_site.py
pytest -q
```

## Cómo ejecutar GitHub Actions

Para uso normal:

- `RAG Quality Gate` con `fail_on_alert=false` o sin tocar el input.
- `Intelligence Factory Alerts All` para resumen consolidado.

Para modo estricto:

- Ejecutar manualmente `RAG Quality Gate` con `fail_on_alert=true`.

## Decisión de arquitectura

Yo separo dos comportamientos:

- **alertar**: informar y abrir tareas sin detener el flujo.
- **bloquear**: fallar el workflow solo cuando decido usar un quality gate estricto.
