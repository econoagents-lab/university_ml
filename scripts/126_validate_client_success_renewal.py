from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mlu.client_success_and_renewal_intelligence import load_config, load_tenant_inputs, build_tenant_success_package, validate_client_success_outputs

if __name__ == "__main__":
    cfg = load_config()
    packages = [build_tenant_success_package(raw, cfg) for raw in load_tenant_inputs()]
    print(validate_client_success_outputs(packages, cfg))
