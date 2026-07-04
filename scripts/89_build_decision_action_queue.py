from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.decision_action_feedback_lab import build_decision_action_queue

if __name__ == "__main__":
    # Yo construyo la cola segura de acciones desde el ranking de riesgo.
    print(build_decision_action_queue())
