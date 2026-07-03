from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

Role = Literal["admin", "manager", "advisor", "analyst", "public"]


@dataclass(frozen=True)
class SecuritySettings:
    auth_enabled: bool
    api_key_configured: bool
    environment: str
    auth_mode: str


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def get_security_settings() -> SecuritySettings:
    return SecuritySettings(
        auth_enabled=_truthy(os.getenv("MLU_AUTH_ENABLED")),
        api_key_configured=bool(os.getenv("MLU_API_KEY")),
        environment=os.getenv("MLU_ENV", "local"),
        auth_mode=os.getenv("MLU_AUTH_MODE", "api_key_optional"),
    )


def require_api_key(provided_key: str | None) -> bool:
    """Return True when access is allowed.

    Local teaching mode keeps auth disabled by default. Production mode should set
    MLU_AUTH_ENABLED=true and MLU_API_KEY=<secret>.
    """
    settings = get_security_settings()
    if not settings.auth_enabled:
        return True
    expected = os.getenv("MLU_API_KEY", "")
    return bool(expected) and provided_key == expected


def role_capabilities(role: Role) -> dict:
    capabilities = {
        "public": ["health", "metadata_public"],
        "advisor": ["health", "decision_queue_own", "feedback_write"],
        "manager": ["health", "decision_queue_all", "dashboard", "feedback_write", "brief"],
        "analyst": ["health", "metadata", "monitoring", "registry", "reports"],
        "admin": ["all"],
    }
    return {"role": role, "capabilities": capabilities.get(role, capabilities["public"])}
