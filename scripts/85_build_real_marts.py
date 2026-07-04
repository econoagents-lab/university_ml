from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.real_marts import build_all_real_marts

if __name__ == "__main__":
    manifest = build_all_real_marts()
    print(f"Marts reales generados: {len(manifest.get('marts', []))}")
    for item in manifest.get("marts", []):
        print(f"- {item.get('mart')}: {item.get('status')} ({item.get('rows')} filas)")
