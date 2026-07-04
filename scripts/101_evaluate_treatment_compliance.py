from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mlu.experiment_power_policy_engine import build_treatment_compliance

if __name__ == '__main__':
    print(build_treatment_compliance().to_string(index=False))
