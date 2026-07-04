from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.decision_action_feedback_lab import run_decision_action_feedback_lab

if __name__ == "__main__":
    # Yo ejecuto el laboratorio completo de decisión, acción, feedback y aprendizaje.
    result = run_decision_action_feedback_lab()
    print(result)
