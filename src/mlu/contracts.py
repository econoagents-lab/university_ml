from __future__ import annotations

from pathlib import Path
import yaml
import pandas as pd


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_required_columns(df: pd.DataFrame, required_columns: list[str]) -> list[str]:
    return [col for col in required_columns if col not in df.columns]


def _required_columns_from_contract(contract: dict) -> list[str]:
    """Soporta contratos legacy y contratos model-ready.

    Legacy:
      columns: [{name, required}]

    Model-ready:
      primary_key + feature_columns + target
    """
    if contract.get("columns"):
        return [c["name"] for c in contract.get("columns", []) if c.get("required", True)]

    required: list[str] = []
    required.extend(contract.get("primary_key", []) or [])
    required.extend(contract.get("feature_columns", []) or [])
    target = contract.get("target")
    if target:
        required.append(target)

    # conservar orden sin duplicados
    seen = set()
    return [col for col in required if not (col in seen or seen.add(col))]


def validate_contract(df: pd.DataFrame, contract_path: Path) -> dict:
    contract = load_yaml(contract_path)
    required_columns = _required_columns_from_contract(contract)
    missing = validate_required_columns(df, required_columns)

    forbidden_columns = contract.get("forbidden_columns", []) or []
    forbidden_present = [col for col in forbidden_columns if col in df.columns]
    strict_forbidden = bool(contract.get("strict_forbidden_columns", bool(forbidden_columns)))

    is_valid = len(missing) == 0 and (not strict_forbidden or len(forbidden_present) == 0)
    return {
        "contract": contract.get("name") or contract.get("contract_name"),
        "is_valid": is_valid,
        "missing_columns": missing,
        "required_columns": required_columns,
        "forbidden_columns_present": forbidden_present,
        "strict_forbidden_columns": strict_forbidden,
    }
