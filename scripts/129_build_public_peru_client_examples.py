from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.public_peru_demo import run_public_peru_demo_build


if __name__ == "__main__":
    result = run_public_peru_demo_build()
    print(result)
