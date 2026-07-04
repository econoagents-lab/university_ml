from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.dashboard_generator import generate_family_indexes, generate_dashboard_index, read_json_if_exists, MANIFEST_PATH

if __name__ == "__main__":
    manifest = read_json_if_exists(MANIFEST_PATH)
    if not manifest:
        raise SystemExit("No existe manifest. Ejecuta primero scripts/77_generate_dashboards_from_catalog.py")
    generate_dashboard_index(manifest)
    outputs = generate_family_indexes(manifest)
    print(f"Índices por familia generados: {len(outputs)}")
