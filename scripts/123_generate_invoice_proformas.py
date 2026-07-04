from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.contract_to_signature_and_invoice_ops import run_contract_to_signature_and_invoice_ops

if __name__ == "__main__":
    manifest = run_contract_to_signature_and_invoice_ops()
    for tenant in manifest.get("tenants", []):
        print(f"{tenant['tenant_id']} -> {tenant['invoice_id']} -> {tenant['total']}")
