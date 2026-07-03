from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from economic_lab.story_builder import build_table_to_text_corpus

if __name__ == "__main__":
    # Yo convierto marts económicos en historias para el RAG.
    out = build_table_to_text_corpus("marts/output/mart_project_month.csv")
    print(f"OK: historias generadas en {out}")
