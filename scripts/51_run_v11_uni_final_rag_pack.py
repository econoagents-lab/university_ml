from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

steps = [
    "scripts/46_build_economic_marts.py",
    "scripts/47_build_table_to_text_corpus.py",
    "scripts/48_build_rag_index.py",
    "scripts/49_run_rag_demo_questions.py",
    "scripts/50_evaluate_rag_uni.py",
    "scripts/52_generate_uni_final_report.py",
]

if __name__ == "__main__":
    # Yo ejecuto todo el pipeline final UNI de forma reproducible.
    for step in steps:
        print(f"[RUN] {step}")
        result = subprocess.run([sys.executable, step], cwd=ROOT)
        if result.returncode != 0:
            raise SystemExit(f"Falló el paso {step}")
    print("OK: v1.1 UNI final RAG pack ejecutado de inicio a fin.")
