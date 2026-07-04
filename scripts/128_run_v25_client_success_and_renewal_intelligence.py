from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mlu.client_success_and_renewal_intelligence import run_client_success_and_renewal_intelligence, INDEX_HTML, REPORT_MD

if __name__ == "__main__":
    result = run_client_success_and_renewal_intelligence()
    print("v2.5 Client Success & Renewal Intelligence")
    print("status=", result["validation"].get("status"))
    print("tenants=", result["validation"].get("tenant_count"))
    print("report=", REPORT_MD)
    print("index=", INDEX_HTML)
