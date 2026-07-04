from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.client_ready_branding_and_deployment import run_client_ready_branding_and_deployment

if __name__ == "__main__":
    result = run_client_ready_branding_and_deployment()
    print(result["validation"])
    raise SystemExit(1 if result["validation"].get("status") == "fail" else 0)
