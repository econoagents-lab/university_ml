from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse
from src.mlu.progress import assert_unlocked

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", required=True)
    args = parser.parse_args()
    assert_unlocked(args.chapter)
    print(f"OK: capítulo {args.chapter} desbloqueado")
