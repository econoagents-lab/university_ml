from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.decision_action_feedback_lab import evaluate_action_outcomes

if __name__ == "__main__":
    # Yo evalúo resultados 7d/30d para medir si intervenir salva operaciones.
    print(evaluate_action_outcomes())
