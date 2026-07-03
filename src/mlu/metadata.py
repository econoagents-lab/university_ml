from __future__ import annotations

from .registry import registry_metadata


def model_registry_payload() -> dict:
    return registry_metadata()
