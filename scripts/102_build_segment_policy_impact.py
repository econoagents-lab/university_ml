from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mlu.experiment_power_policy_engine import build_segment_policy_impact

if __name__ == '__main__':
    df = build_segment_policy_impact()
    print(df.head(20).to_string(index=False))
