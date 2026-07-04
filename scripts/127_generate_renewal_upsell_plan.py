from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mlu.client_success_and_renewal_intelligence import run_client_success_and_renewal_intelligence

if __name__ == "__main__":
    result = run_client_success_and_renewal_intelligence()
    for package in result["packages"]:
        print(package["tenant_id"], package["renewal_plan"]["renewal_recommendation"], package["renewal_plan"]["estimated_upsell_value"])
