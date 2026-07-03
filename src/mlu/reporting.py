from __future__ import annotations

from pathlib import Path
import json
from datetime import datetime


def write_markdown_report(path: Path, title: str, sections: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", "", f"Generado: {datetime.now().isoformat(timespec='seconds')}", ""]
    for section, content in sections.items():
        lines.extend([f"## {section}", "", str(content), ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
