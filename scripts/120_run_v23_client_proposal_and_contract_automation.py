from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.client_proposal_and_contract_automation import run_client_proposal_and_contract_automation

if __name__ == "__main__":
    result = run_client_proposal_and_contract_automation()
    print(result["validation"])
    raise SystemExit(0 if result["validation"].get("status") == "ok" else 1)
