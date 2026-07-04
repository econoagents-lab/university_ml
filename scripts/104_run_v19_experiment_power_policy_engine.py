from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mlu.experiment_power_policy_engine import run_experiment_power_policy_engine

if __name__ == '__main__':
    result = run_experiment_power_policy_engine()
    print('v1.9 Experiment Power & Policy Engine ejecutado')
    print(result)
