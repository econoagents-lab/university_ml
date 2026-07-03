from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json
import os
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ALERTS_DIR = ROOT / "reports" / "alerts"


def read_message(alert_file: Path) -> str:
    """Yo leo la alerta Markdown y la reduzco si el webhook tiene límite de tamaño."""
    if not alert_file.exists():
        return "No encontré alerta generada."
    text = alert_file.read_text(encoding="utf-8", errors="ignore")
    return text[:3500]


def post_json(url: str, payload: dict[str, Any]) -> None:
    """Yo envío JSON a un webhook sin agregar dependencias externas."""
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=20) as response:
        print(f"Webhook respondió HTTP {response.status}")


def send_slack_or_discord(message: str) -> bool:
    """Yo envío la alerta a Slack o Discord si existe un webhook en secrets."""
    slack = os.getenv("SLACK_WEBHOOK_URL")
    discord = os.getenv("DISCORD_WEBHOOK_URL")
    if slack:
        post_json(slack, {"text": message})
        return True
    if discord:
        post_json(discord, {"content": message})
        return True
    return False


def send_telegram(message: str) -> bool:
    """Yo envío la alerta a Telegram si encuentro token y chat id en variables de entorno."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False
    query = urllib.parse.urlencode({"chat_id": chat_id, "text": message[:3900], "parse_mode": "Markdown"})
    url = f"https://api.telegram.org/bot{token}/sendMessage?{query}"
    with urllib.request.urlopen(url, timeout=20) as response:
        print(f"Telegram respondió HTTP {response.status}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alert-file", default=str(ALERTS_DIR / "EXECUTIVE_KPI_DIGEST.md"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    message = read_message(Path(args.alert_file))
    if args.dry_run:
        print(message)
        return
    sent = send_slack_or_discord(message)
    sent = send_telegram(message) or sent
    if not sent:
        print("No envié webhook porque no encontré secrets configurados. Esto es esperado en modo local.")


if __name__ == "__main__":
    main()
