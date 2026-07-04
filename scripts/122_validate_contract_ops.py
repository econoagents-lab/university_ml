from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
from src.mlu.contract_to_signature_and_invoice_ops import load_config, load_proposal_packages, build_tenant_contract_ops, validate_contract_ops

if __name__ == "__main__":
    cfg = load_config()
    packages = [build_tenant_contract_ops(p, cfg) for p in load_proposal_packages()]
    result = validate_contract_ops(packages, cfg)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result.get("status") == "ok" else 2)
