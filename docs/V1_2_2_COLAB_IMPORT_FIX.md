# v1.2.2 · Colab import fix + soft gates

## Problema corregido

En Colab podía aparecer:

```text
ModuleNotFoundError: No module named 'rag'
```

La causa no era que faltara el paquete `rag`. La causa era que el notebook estaba ejecutándose desde una carpeta que no era la raíz del proyecto, o que se había subido solo el notebook sin el ZIP completo.

## Solución

Yo agregué una celda bootstrap al notebook final:

```text
notebooks/UNI_Final_RAG_Asistente_Economico_Inmobiliario.ipynb
```

La celda ahora:

1. Busca la raíz del proyecto.
2. Verifica que exista `rag/pipeline.py`.
3. Si encuentra un ZIP `machine_learning_university*.zip`, lo descomprime automáticamente.
4. Hace `os.chdir(PROJECT_ROOT)`.
5. Agrega `PROJECT_ROOT` a `sys.path`.
6. Explica qué falta si solo se subió el notebook.

## Uso recomendado en Colab

1. Sube el ZIP completo del proyecto a `/content`.
2. Abre el notebook.
3. Ejecuta la celda de preparación de entorno.
4. Ejecuta el resto del notebook.

No basta con subir únicamente el archivo `.ipynb`, porque el notebook importa módulos locales como `rag.pipeline`.
