from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.contract_to_signature_and_invoice_ops import run_contract_to_signature_and_invoice_ops

if __name__ == "__main__":
    manifest = run_contract_to_signature_and_invoice_ops()
    print(f"Contrato ops generado: {manifest.get('tenant_count')} tenants · status={manifest.get('status')}")
