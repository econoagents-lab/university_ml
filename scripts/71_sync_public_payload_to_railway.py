from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

PROJECT_ROOT_CANDIDATE = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT_CANDIDATE) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT_CANDIDATE))

from urllib import request

from src.mlu.config import PROJECT_ROOT

PUBLIC_PAYLOAD_PATH = PROJECT_ROOT / "reports" / "public" / "decision_dashboard_payload_public.json"


def sync_public_payload(payload_path: Path = PUBLIC_PAYLOAD_PATH, url: str | None = None, token: str | None = None) -> dict:
    """
    Yo sincronizo el payload público hacia una API en Railway cuando existe un endpoint receptor.
    Si no hay URL configurada, no fallo: dejo el payload listo para que Railway lo lea desde el repo o artifact.
    """
    if not payload_path.exists():
        raise FileNotFoundError(f"No existe payload público para sincronizar: {payload_path}")

    target_url = url or os.getenv("RAILWAY_PUBLIC_PAYLOAD_SYNC_URL", "").strip()
    auth_token = token or os.getenv("RAILWAY_PUBLIC_PAYLOAD_SYNC_TOKEN", "").strip()

    if not target_url:
        return {
            "status": "skipped",
            "reason": "RAILWAY_PUBLIC_PAYLOAD_SYNC_URL no está configurado.",
            "payload_path": str(payload_path),
        }

    payload_bytes = payload_path.read_bytes()
    req = request.Request(
        target_url,
        data=payload_bytes,
        headers={
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {auth_token}"} if auth_token else {}),
        },
        method="POST",
    )
    with request.urlopen(req, timeout=30) as response:
        body = response.read().decode("utf-8", errors="replace")
        return {"status": "ok", "status_code": response.status, "response": body[:1000]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Sincroniza payload público agregado hacia Railway.")
    parser.add_argument("--payload", type=Path, default=PUBLIC_PAYLOAD_PATH)
    parser.add_argument("--url", default=None)
    parser.add_argument("--token", default=None)
    args = parser.parse_args()
    result = sync_public_payload(args.payload, args.url, args.token)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
