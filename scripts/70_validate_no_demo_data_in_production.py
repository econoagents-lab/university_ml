from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
import sys

PROJECT_ROOT_CANDIDATE = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT_CANDIDATE) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT_CANDIDATE))

from typing import Any

from src.mlu.config import PROJECT_ROOT

PUBLIC_PAYLOAD_PATH = PROJECT_ROOT / "reports" / "public" / "decision_dashboard_payload_public.json"
ALLOWED_TOP_LEVEL_KEYS = {
    "total_operaciones",
    "valor_total_en_riesgo",
    "riesgo_promedio",
    "p0_p1",
    "top_proyectos",
    "top_asesores",
    "top_canales",
    "fecha_generacion",
    "data_mode",
}
SENSITIVE_TERMS = [
    "cliente",
    "documento",
    "dni",
    "email",
    "correo",
    "teléfono",
    "telefono",
    "phone",
    "celular",
    "nombre completo",
    "nombre_completo",
    "direccion",
    "dirección",
    "credencial",
    "credential",
    "password",
    "secret",
    "token",
    "api_key",
    "redshift",
]
DEMO_TERMS = ["demo", "sample", "synthetic", "sintetico", "sintético", "fake", "dummy"]


def walk(value: Any, path: str = "root") -> list[tuple[str, Any]]:
    """
    Yo recorro cualquier JSON para revisar claves y valores antes de publicarlo.
    """
    items: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            items.append((f"{path}.{key}", key))
            items.extend(walk(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            items.extend(walk(child, f"{path}[{idx}]"))
    else:
        items.append((path, value))
    return items


def validate_public_payload(payload: dict[str, Any], environment: str = "production") -> dict[str, Any]:
    """
    Yo valido que Railway reciba solo agregados CRM, nunca filas demo ni datos personales.
    """
    errors: list[str] = []
    warnings: list[str] = []

    keys = set(payload.keys())
    if keys != ALLOWED_TOP_LEVEL_KEYS:
        errors.append(f"Top-level keys inválidas. Esperado={sorted(ALLOWED_TOP_LEVEL_KEYS)} actual={sorted(keys)}")

    if payload.get("data_mode") != "crm":
        errors.append("data_mode debe ser 'crm' para producción.")

    if environment == "production":
        for path, value in walk(payload):
            text = str(value)
            lower = text.lower()
            key_lower = path.lower()
            if any(term in key_lower for term in SENSITIVE_TERMS):
                errors.append(f"Clave sensible detectada en {path}")
            if isinstance(value, str) and any(term in lower for term in SENSITIVE_TERMS):
                errors.append(f"Valor sensible detectado en {path}")
            if isinstance(value, str) and any(term in lower for term in DEMO_TERMS):
                errors.append(f"Valor demo/sample detectado en {path}")
            if isinstance(value, str) and re.search(r"\b\d{8}\b", text):
                errors.append(f"Posible DNI detectado en {path}")
            if isinstance(value, str) and re.search(r"\b9\d{8}\b", text):
                errors.append(f"Posible teléfono detectado en {path}")
            if isinstance(value, str) and re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text):
                errors.append(f"Email detectado en {path}")

    return {"status": "fail" if errors else "ok", "errors": errors, "warnings": warnings}


def load_payload(path: Path = PUBLIC_PAYLOAD_PATH) -> dict[str, Any]:
    """
    Yo cargo el payload público generado por el bridge CRM → Railway.
    """
    if not path.exists():
        raise FileNotFoundError(f"No existe payload público: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida que producción no sirva datos demo ni PII.")
    parser.add_argument("--payload", type=Path, default=PUBLIC_PAYLOAD_PATH)
    parser.add_argument("--environment", default=os.getenv("MLU_ENV", "production"))
    args = parser.parse_args()

    payload = load_payload(args.payload)
    result = validate_public_payload(payload, environment=args.environment)
    report_path = PROJECT_ROOT / "reports" / "public" / "production_public_payload_validation.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
