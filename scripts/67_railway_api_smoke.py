from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "reports" / "alerts"


def get_json(url: str) -> dict:
    """Yo consulto un endpoint Railway y guardo la respuesta como evidencia de salud productiva."""
    with urllib.request.urlopen(url, timeout=20) as response:
        body = response.read().decode("utf-8", errors="ignore")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {"raw": body[:1000]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.getenv("MLU_RAILWAY_BASE_URL", ""))
    args = parser.parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not args.base_url:
        payload = {"severity": "skipped", "reason": "No configuré MLU_RAILWAY_BASE_URL."}
    else:
        base = args.base_url.rstrip("/")
        endpoints = ["/production/health", "/metadata/release", "/metadata/model-registry"]
        results = {}
        severity = "ok"
        for endpoint in endpoints:
            try:
                results[endpoint] = get_json(base + endpoint)
            except Exception as exc:  # noqa: BLE001
                severity = "warning"
                results[endpoint] = {"error": str(exc)}
        payload = {"severity": severity, "base_url": base, "results": results}
    (OUTPUT_DIR / "RAILWAY_SMOKE.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Railway API Smoke", "", f"- Severidad: **{payload['severity'].upper()}**"]
    if "reason" in payload:
        lines.append(f"- {payload['reason']}")
    else:
        lines.append(f"- Base URL: `{payload.get('base_url')}`")
    (OUTPUT_DIR / "RAILWAY_SMOKE.md").write_text("\n".join(lines), encoding="utf-8")
    print("Railway smoke generado.")


if __name__ == "__main__":
    main()
