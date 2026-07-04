from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.real_marts import build_proxy_vs_official_gap, PROXY_GAP_MD

if __name__ == "__main__":
    result = build_proxy_vs_official_gap()
    print(f"Gap proxy vs oficial: {result['status']} -> {PROXY_GAP_MD}")
