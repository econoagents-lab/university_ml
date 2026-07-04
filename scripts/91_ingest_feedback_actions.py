from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.decision_action_feedback_lab import ingest_feedback_actions

if __name__ == "__main__":
    # Yo convierto feedback operativo en eventos seguros para análisis.
    print(ingest_feedback_actions())
