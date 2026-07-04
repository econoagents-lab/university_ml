from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.client_proposal_and_contract_automation import build_client_proposals

if __name__ == "__main__":
    # Yo genero contratos junto con las propuestas porque cada venta necesita gobierno de métricas.
    result = build_client_proposals()
    print(f"Contratos generados para {result.get('tenant_count')} tenants")
