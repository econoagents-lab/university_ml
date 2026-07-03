from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.mlu.config import PROJECT_ROOT
from src.mlu.security import get_security_settings
from src.mlu.feedback_store import feedback_store_schema

PRODUCTION_DIR = PROJECT_ROOT / "reports" / "production"
READINESS_JSON = PRODUCTION_DIR / "production_readiness_report.json"
READINESS_MD = PRODUCTION_DIR / "PRODUCTION_READINESS_REPORT.md"
RELEASE_MANIFEST = PRODUCTION_DIR / "release_manifest_v1_0.json"

REQUIRED_PATHS = {
    "model": PROJECT_ROOT / "models" / "riesgo_caida_model.joblib",
    "feature_columns": PROJECT_ROOT / "models" / "feature_columns.json",
    "model_registry": PROJECT_ROOT / "models" / "registry" / "model_registry.json",
    "decision_queue": PROJECT_ROOT / "reports" / "dashboard" / "decision_queue_riesgo_caida.parquet",
    "dashboard_html": PROJECT_ROOT / "reports" / "dashboard" / "DECISION_DASHBOARD_RIESGO_CAIDA.html",
    "feedback_sql": PROJECT_ROOT / "sql" / "production_feedback_store_schema.sql",
    "release_checklist": PROJECT_ROOT / "docs" / "PRODUCTION_RELEASE_CHECKLIST.md",
}


def build_release_manifest() -> dict[str, Any]:
    security = get_security_settings()
    manifest = {
        "project": "Machine Learning University",
        "release": "v1.0_production_release",
        "version": "1.0.0",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "data_mode": "crm_first_demo_supported",
        "api": {
            "framework": "FastAPI",
            "health": "/health",
            "dashboard": "/dashboard/riesgo-caida",
            "model_registry": "/metadata/model-registry",
            "production_readiness": "/metadata/production-readiness",
            "feedback_schema": "/feedback/store/schema",
        },
        "security": security.__dict__,
        "feedback_store": feedback_store_schema(),
        "roles": ["admin", "manager", "advisor", "analyst", "public"],
    }
    PRODUCTION_DIR.mkdir(parents=True, exist_ok=True)
    RELEASE_MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def build_production_readiness() -> dict[str, Any]:
    checks = []
    for name, path in REQUIRED_PATHS.items():
        checks.append({"check": name, "path": str(path), "exists": path.exists()})
    n_ok = sum(1 for c in checks if c["exists"])
    n_total = len(checks)
    status = "production_ready" if n_ok == n_total else "ready_with_warnings"
    report = {
        "status": status,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "checks_ok": n_ok,
        "checks_total": n_total,
        "checks": checks,
        "security": get_security_settings().__dict__,
        "recommended_next_action": "Deploy local/Railway only after setting MLU_AUTH_ENABLED=true and MLU_API_KEY in production." if status == "production_ready" else "Completar artefactos faltantes antes de deployment estable.",
    }
    PRODUCTION_DIR.mkdir(parents=True, exist_ok=True)
    READINESS_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# Production Readiness Report v1.0",
        "",
        f"Estado: **{status}**",
        f"Checks OK: {n_ok}/{n_total}",
        "",
        "## Checks",
        "",
        "| Check | Estado | Path |",
        "|---|---:|---|",
    ]
    for c in checks:
        lines.append(f"| {c['check']} | {'ok' if c['exists'] else 'missing'} | `{c['path']}` |")
    lines += ["", "## Siguiente acción", "", report["recommended_next_action"]]
    READINESS_MD.write_text("\n".join(lines), encoding="utf-8")
    return report


def load_release_metadata() -> dict[str, Any]:
    if not RELEASE_MANIFEST.exists():
        return build_release_manifest()
    return json.loads(RELEASE_MANIFEST.read_text(encoding="utf-8"))


def load_readiness_metadata() -> dict[str, Any]:
    if not READINESS_JSON.exists():
        return build_production_readiness()
    return json.loads(READINESS_JSON.read_text(encoding="utf-8"))
