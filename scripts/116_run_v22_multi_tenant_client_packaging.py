from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mlu.multi_tenant_client_packaging import run_multi_tenant_client_packaging, validate_multi_tenant_packaging

if __name__ == '__main__':
    manifest = run_multi_tenant_client_packaging()
    validation = validate_multi_tenant_packaging()
    print(f"Tenants generados: {manifest.get('tenant_count')}")
    print(f"Validación: {validation.get('status')}")
    if validation.get('status') == 'fail':
        raise SystemExit(1)
