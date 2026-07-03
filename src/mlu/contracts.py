from __future__ import annotations

from pathlib import Path
import yaml
import pandas as pd


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_required_columns(df: pd.DataFrame, required_columns: list[str]) -> list[str]:
    return [col for col in required_columns if col not in df.columns]


def validate_contract(df: pd.DataFrame, contract_path: Path) -> dict:
    contract = load_yaml(contract_path)
    required_columns = [c["name"] for c in contract.get("columns", []) if c.get("required", True)]
    missing = validate_required_columns(df, required_columns)
    return {
        "contract": contract.get("name"),
        "is_valid": len(missing) == 0,
        "missing_columns": missing,
        "required_columns": required_columns,
    }
