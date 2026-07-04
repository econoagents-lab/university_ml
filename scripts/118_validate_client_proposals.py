from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.client_proposal_and_contract_automation import validate_client_proposals

if __name__ == "__main__":
    result = validate_client_proposals()
    print(result)
    raise SystemExit(0 if result.get('status') == 'ok' else 1)
