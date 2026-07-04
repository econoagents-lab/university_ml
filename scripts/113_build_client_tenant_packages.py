from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mlu.multi_tenant_client_packaging import build_all_tenant_packages

if __name__ == '__main__':
    manifest = build_all_tenant_packages()
    print(f"Paquetes cliente generados: {manifest.get('tenant_count')}")
