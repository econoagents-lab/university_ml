from pathlib import Path
from src.mlu.data_loader import load_operations
from src.mlu.contracts import validate_contract


def test_data_contract_is_valid():
    df = load_operations()
    result = validate_contract(df, Path("contracts/data_contract_riesgo_caida.yml"))
    assert result["is_valid"], result["missing_columns"]
