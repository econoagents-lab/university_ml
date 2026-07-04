from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.client_ready_branding_and_deployment import validate_client_ready_deployment

if __name__ == "__main__":
    result = validate_client_ready_deployment()
    print(result)
    raise SystemExit(1 if result.get("status") == "fail" else 0)
