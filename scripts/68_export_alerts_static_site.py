from __future__ import annotations

from pathlib import Path
import html

ROOT = Path(__file__).resolve().parents[1]
ALERTS = ROOT / "reports" / "alerts"
SITE = ROOT / "site" / "alerts"


def main() -> None:
    """Yo convierto reportes Markdown en una página HTML simple para GitHub Pages o Railway."""
    SITE.mkdir(parents=True, exist_ok=True)
    cards = []
    for path in sorted(ALERTS.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        cards.append(f"<section><h2>{html.escape(path.stem)}</h2><pre>{html.escape(text)}</pre></section>")
    html_doc = """<!doctype html><html><head><meta charset='utf-8'><title>MLU Alerts</title>
<style>body{font-family:Arial,sans-serif;margin:32px;max-width:1100px}pre{white-space:pre-wrap;background:#f6f8fa;padding:16px;border-radius:8px}section{margin-bottom:24px}</style>
</head><body><h1>Machine Learning University · Alerts</h1>__CARDS__</body></html>""".replace("__CARDS__", "\n".join(cards))
    (SITE / "index.html").write_text(html_doc, encoding="utf-8")
    print(f"Sitio exportado: {SITE / 'index.html'}")


if __name__ == "__main__":
    main()
