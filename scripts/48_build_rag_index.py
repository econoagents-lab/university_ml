from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from rag.pipeline import EconomicRagPipeline

if __name__ == "__main__":
    # Yo construyo el índice RAG sobre corpus seguro y table-to-text.
    pipeline = EconomicRagPipeline(corpus_dir="corpus", prefer_semantic_embeddings=False).build()
    pipeline.save_manifest()
    print("OK: índice RAG construido.")
