from pathlib import Path

from src.mlu.contracts import validate_contract
from src.mlu.data_loader import load_operations
from src.mlu.official_rules import build_model_ready_dataset


def test_data_contract_is_valid():
    """Valida el contrato correcto según la fuente cargada.

    - Synthetic: valida el contrato educativo/raw.
    - Sperant/gold: transforma primero a model-ready y valida el contrato estricto.
    """
    raw_df = load_operations()

    is_sperant_like = {"codigo_proforma", "codigo_unidad", "fecha_snapshot"}.issubset(raw_df.columns)
    if is_sperant_like:
        df_to_validate = build_model_ready_dataset(raw_df)
        contract_path = Path("contracts/model_ready_contract_riesgo_caida.yml")
    else:
        df_to_validate = raw_df
        contract_path = Path("contracts/data_contract_riesgo_caida.yml")

    result = validate_contract(df_to_validate, contract_path)
    assert result["is_valid"], {
        "contract": result["contract"],
        "missing_columns": result["missing_columns"],
        "forbidden_columns_present": result["forbidden_columns_present"],
    }
