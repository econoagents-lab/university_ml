from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from rag.pipeline import EconomicRagPipeline
from rag.text_to_sql import run_sql_question

pipeline = EconomicRagPipeline(corpus_dir="corpus", prefer_semantic_embeddings=False).build()


def responder(question: str, usar_sql: bool = False):
    """
    Yo respondo desde Gradio usando RAG y opcionalmente Text-to-SQL controlado.
    """
    ans = pipeline.ask(question)
    text = ans.answer
    if usar_sql and not ans.refused:
        sql_result = run_sql_question(question)
        text += "\n\nSQL controlado:\n" + sql_result["sql"]
        text += "\n\nResultado:\n" + str(sql_result["rows"])
    if ans.citations:
        text += "\n\nCitas:\n" + "\n".join(f"- {c}" for c in ans.citations)
    return text


if __name__ == "__main__":
    import gradio as gr
    demo = gr.Interface(
        fn=responder,
        inputs=[
            gr.Textbox(label="Pregunta", value="¿Por qué días en tubería puede aumentar riesgo de caída?"),
            gr.Checkbox(label="Usar Text-to-SQL controlado", value=False),
        ],
        outputs=gr.Textbox(label="Respuesta con evidencia"),
        title="Asistente RAG económico inmobiliario",
        description="Yo respondo con corpus seguro, citas, guardrails y evidencia económica.",
    )
    demo.launch()
