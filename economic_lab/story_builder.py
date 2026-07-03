from __future__ import annotations

from pathlib import Path
import pandas as pd


def project_month_to_stories(df: pd.DataFrame) -> list[dict]:
    """
    Yo convierto filas mensuales por proyecto en historias de negocio citables por el RAG.
    """
    stories = []
    for _, row in df.iterrows():
        proyecto = row.get("proyecto", "Proyecto no identificado")
        periodo = row.get("periodo_mes", "periodo no identificado")
        text = (
            f"En {periodo}, {proyecto} registró {int(row.get('separaciones', 0))} separaciones, "
            f"{int(row.get('minutas', 0))} minutas y {int(row.get('caidas', 0))} caídas. "
            f"La conversión separación a minuta fue {row.get('conversion_sep_minuta', 0):.1%}, "
            f"la tasa de caída fue {row.get('caida_rate', 0):.1%}, "
            f"y el valor en riesgo aproximado fue S/ {row.get('valor_en_riesgo', 0):,.0f}. "
            f"La brecha de precio por m² frente al mercado fue {row.get('brecha_precio_m2', 0):,.0f} soles."
        )
        stories.append({
            "doc_id": f"story_{periodo}_{proyecto}".replace(" ", "_").lower(),
            "source": "mart_project_month",
            "title": f"Historia mensual de {proyecto} - {periodo}",
            "text": text,
            "metadata": {"periodo_mes": str(periodo), "proyecto": str(proyecto), "type": "table_to_text"},
        })
    return stories


def write_stories_markdown(stories: list[dict], output_path: str | Path) -> Path:
    """
    Yo escribo historias generadas desde tablas en Markdown para que entren al corpus RAG.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Historias table-to-text del mart mensual", ""]
    for story in stories:
        lines.append(f"## {story['title']}")
        lines.append("")
        lines.append(story["text"])
        lines.append("")
        lines.append(f"Fuente: `{story['source']}` · doc_id: `{story['doc_id']}`")
        lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def build_table_to_text_corpus(mart_path: str | Path, output_path: str | Path = "corpus/generated_stories/project_month_stories.md") -> Path:
    """
    Yo orquesto la conversión de marts económicos en memoria narrativa para el RAG.
    """
    mart_path = Path(mart_path)
    df = pd.read_parquet(mart_path) if mart_path.suffix == ".parquet" else pd.read_csv(mart_path)
    stories = project_month_to_stories(df)
    return write_stories_markdown(stories, output_path)


if __name__ == "__main__":
    build_table_to_text_corpus("marts/output/mart_project_month.csv")
