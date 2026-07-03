from __future__ import annotations

import json
from pathlib import Path
from .config import STATE_PATH

REQUIRED_PREVIOUS = {
    "01": [],
    "02": ["01"],
    "03": ["02"],
    "04": ["03"],
    "05": ["04"],
    "06": ["05"],
    "07": ["06"],
    "08": ["07"],
}


def load_progress(path: Path = STATE_PATH) -> dict:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"completed_chapters": []}
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload
    return json.loads(path.read_text(encoding="utf-8"))


def mark_complete(chapter: str, path: Path = STATE_PATH) -> None:
    progress = load_progress(path)
    completed = set(progress.get("completed_chapters", []))
    completed.add(chapter)
    progress["completed_chapters"] = sorted(completed)
    path.write_text(json.dumps(progress, indent=2), encoding="utf-8")


def assert_unlocked(chapter: str, path: Path = STATE_PATH) -> None:
    progress = load_progress(path)
    completed = set(progress.get("completed_chapters", []))
    missing = [ch for ch in REQUIRED_PREVIOUS.get(chapter, []) if ch not in completed]
    if missing:
        raise SystemExit(
            f"Capítulo {chapter} bloqueado. Completa primero: {', '.join(missing)}. "
            "Para saltar el bloqueo usa .\\run.ps1 -Chapter XX -Force"
        )
