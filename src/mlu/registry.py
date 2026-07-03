from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .config import PROJECT_ROOT
from .official_rules import FEATURE_COLUMNS, TARGET

REGISTRY_DIR = PROJECT_ROOT / "models" / "registry"
ARTIFACTS_DIR = PROJECT_ROOT / "models" / "artifacts"
CARDS_DIR = PROJECT_ROOT / "models" / "cards"
DATASET_VERSIONS_DIR = PROJECT_ROOT / "data" / "processed" / "versions"
MODEL_REGISTRY_PATH = REGISTRY_DIR / "model_registry.json"
DATASET_REGISTRY_PATH = REGISTRY_DIR / "dataset_registry.json"
EXPERIMENT_HISTORY_PATH = REGISTRY_DIR / "experiment_history.parquet"
CHAMPION_POINTER_PATH = REGISTRY_DIR / "champion_model.txt"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_registry_dirs() -> None:
    for path in [REGISTRY_DIR, ARTIFACTS_DIR, CARDS_DIR, DATASET_VERSIONS_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def file_sha256(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    path = Path(path)
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def dataframe_fingerprint(df: pd.DataFrame) -> str:
    """Hash estable para registrar la versión lógica de un dataset tabular."""
    schema = "|".join(f"{c}:{str(df[c].dtype)}" for c in df.columns)
    sample_hash = pd.util.hash_pandas_object(df.head(500), index=True).astype("uint64").sum()
    raw = f"rows={len(df)}|cols={len(df.columns)}|schema={schema}|sample={int(sample_hash)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_json(path: str | Path, default: Any) -> Any:
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: str | Path, obj: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def dataset_version_id(project: str, data_mode: str, sequence: int, generated_at: str | None = None) -> str:
    date = (generated_at or utc_now())[:10].replace("-", "_")
    return f"dataset_{project}_{data_mode}_{date}_v{sequence:03d}"


def register_dataset_version(
    dataset_path: str | Path,
    project: str = "riesgo_caida",
    data_mode: str = "crm",
    source_system: str = "sperant_redshift_parquet",
    rules_version: str = "0.5.0-official_rules",
) -> dict:
    """Registra dataset model-ready sin copiar raw sensible.

    El registry guarda metadatos y copia el parquet model-ready versionado. No guarda .env ni credenciales.
    """
    ensure_registry_dirs()
    dataset_path = Path(dataset_path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"No existe dataset para registrar: {dataset_path}")

    df = pd.read_parquet(dataset_path)
    missing = [c for c in FEATURE_COLUMNS + [TARGET] if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset no es model-ready; faltan columnas: {missing}")

    registry = load_json(DATASET_REGISTRY_PATH, {"project": project, "datasets": []})
    sequence = len(registry.get("datasets", [])) + 1
    generated_at = utc_now()
    version_id = dataset_version_id(project, data_mode, sequence, generated_at)
    versioned_path = DATASET_VERSIONS_DIR / f"{version_id}.parquet"
    shutil.copy2(dataset_path, versioned_path)

    entry = {
        "dataset_version": version_id,
        "project": project,
        "data_mode": data_mode,
        "source_system": source_system,
        "rules_version": rules_version,
        "created_at": generated_at,
        "path": str(versioned_path.relative_to(PROJECT_ROOT)),
        "source_path": str(Path(dataset_path).as_posix()),
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "target_rate": float(df[TARGET].mean()) if len(df) else None,
        "feature_columns": FEATURE_COLUMNS,
        "target": TARGET,
        "file_sha256": file_sha256(versioned_path),
        "dataframe_fingerprint": dataframe_fingerprint(df),
    }
    registry.setdefault("datasets", []).append(entry)
    registry["latest_dataset"] = version_id
    registry["updated_at"] = generated_at
    save_json(DATASET_REGISTRY_PATH, registry)
    return entry


def load_dataset_registry() -> dict:
    return load_json(DATASET_REGISTRY_PATH, {"project": "riesgo_caida", "datasets": []})


def load_model_registry() -> dict:
    return load_json(MODEL_REGISTRY_PATH, {"project": "riesgo_caida", "current_champion": None, "models": []})


def save_model_registry(registry: dict) -> None:
    registry["updated_at"] = utc_now()
    save_json(MODEL_REGISTRY_PATH, registry)


def register_model(
    model_id: str,
    algorithm: str,
    artifact_path: str | Path,
    dataset_version: str,
    metrics: dict,
    status: str = "challenger",
    model_card_path: str | Path | None = None,
    notes: str = "",
) -> dict:
    ensure_registry_dirs()
    artifact_path = Path(artifact_path)
    if not artifact_path.exists():
        raise FileNotFoundError(f"No existe artifact_path: {artifact_path}")
    registry = load_model_registry()
    existing = [m for m in registry.get("models", []) if m.get("model_id") == model_id]
    if existing:
        registry["models"] = [m for m in registry.get("models", []) if m.get("model_id") != model_id]
    entry = {
        "model_id": model_id,
        "project": registry.get("project", "riesgo_caida"),
        "algorithm": algorithm,
        "status": status,
        "dataset_version": dataset_version,
        "registered_at": utc_now(),
        "artifact_path": str(artifact_path.relative_to(PROJECT_ROOT)) if artifact_path.is_relative_to(PROJECT_ROOT) else str(artifact_path),
        "artifact_sha256": file_sha256(artifact_path),
        "model_card_path": str(Path(model_card_path).relative_to(PROJECT_ROOT)) if model_card_path and Path(model_card_path).exists() and Path(model_card_path).is_relative_to(PROJECT_ROOT) else (str(model_card_path) if model_card_path else None),
        "metrics": metrics,
        "notes": notes,
    }
    registry.setdefault("models", []).append(entry)
    if status == "champion":
        promote_champion(model_id, registry=registry)
    else:
        save_model_registry(registry)
    return entry


def get_model(model_id: str, registry: dict | None = None) -> dict | None:
    registry = registry or load_model_registry()
    for model in registry.get("models", []):
        if model.get("model_id") == model_id:
            return model
    return None


def promote_champion(model_id: str, registry: dict | None = None, reason: str = "manual_or_policy_promotion") -> dict:
    ensure_registry_dirs()
    registry = registry or load_model_registry()
    if not get_model(model_id, registry):
        raise ValueError(f"No existe model_id en registry: {model_id}")
    for model in registry.get("models", []):
        if model.get("model_id") == model_id:
            model["status"] = "champion"
            model["champion_since"] = utc_now()
            model["promotion_reason"] = reason
        elif model.get("status") == "champion":
            model["status"] = "retired"
            model["retired_at"] = utc_now()
            model["retirement_reason"] = f"replaced_by_{model_id}"
    registry["current_champion"] = model_id
    CHAMPION_POINTER_PATH.write_text(model_id, encoding="utf-8")
    save_model_registry(registry)
    return registry


def append_experiment_history(rows: list[dict] | pd.DataFrame) -> pd.DataFrame:
    ensure_registry_dirs()
    new = pd.DataFrame(rows)
    if EXPERIMENT_HISTORY_PATH.exists():
        old = pd.read_parquet(EXPERIMENT_HISTORY_PATH)
        out = pd.concat([old, new], ignore_index=True)
        out = out.drop_duplicates(subset=["model_id"], keep="last") if "model_id" in out.columns else out
    else:
        out = new
    out.to_parquet(EXPERIMENT_HISTORY_PATH, index=False)
    out.to_csv(EXPERIMENT_HISTORY_PATH.with_suffix(".csv"), index=False)
    return out


def registry_metadata() -> dict:
    """Payload listo para endpoint /metadata/model-registry."""
    dataset_registry = load_dataset_registry()
    model_registry = load_model_registry()
    champion_id = model_registry.get("current_champion")
    champion = get_model(champion_id, model_registry) if champion_id else None
    return {
        "status": "ok" if champion else "registry_without_champion",
        "project": model_registry.get("project", "riesgo_caida"),
        "current_champion": champion_id,
        "champion": champion,
        "n_registered_models": len(model_registry.get("models", [])),
        "latest_dataset": dataset_registry.get("latest_dataset"),
        "n_dataset_versions": len(dataset_registry.get("datasets", [])),
        "data_modes": sorted({d.get("data_mode", "unknown") for d in dataset_registry.get("datasets", [])}),
        "registry_paths": {
            "model_registry": str(MODEL_REGISTRY_PATH.relative_to(PROJECT_ROOT)),
            "dataset_registry": str(DATASET_REGISTRY_PATH.relative_to(PROJECT_ROOT)),
            "experiment_history": str(EXPERIMENT_HISTORY_PATH.relative_to(PROJECT_ROOT)),
        },
    }
