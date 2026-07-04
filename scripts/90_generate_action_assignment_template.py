from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.decision_action_feedback_lab import generate_action_assignment_template

if __name__ == "__main__":
    # Yo genero la plantilla que comercial debe completar con acciones y resultados.
    print(generate_action_assignment_template())
