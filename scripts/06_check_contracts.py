from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pathlib import Path
from src.mlu.data_loader import load_operations
from src.mlu.contracts import validate_contract

if __name__ == "__main__":
    df = load_operations()
    result = validate_contract(df, Path("contracts/data_contract_riesgo_caida.yml"))
    if not result["is_valid"]:
        raise SystemExit(f"Contrato inválido. Faltan columnas: {result['missing_columns']}")
    print("OK: contrato de datos válido")
