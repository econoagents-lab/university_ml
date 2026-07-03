from __future__ import annotations

from pathlib import Path
import csv
import re
from .document import RagDocument
from .guardrails import mask_pii


def _read_pdf(path: Path) -> str:
    """
    Yo intento leer PDFs con pypdf. Si no está disponible, devuelvo texto mínimo para no romper el Run all.
    """
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        return f"[PDF no leído automáticamente: {path.name}. Motivo: {exc}]"


def _read_csv(path: Path, max_rows: int = 50) -> str:
    """
    Yo convierto un CSV pequeño en texto para que pueda entrar al corpus RAG.
    """
    rows = []
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= max_rows:
                break
            rows.append("; ".join(f"{k}: {v}" for k, v in row.items()))
    return "\n".join(rows)


def load_document(path: str | Path) -> RagDocument:
    """
    Yo cargo un documento multiformato y lo convierto en un documento RAG seguro.
    """
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in {".md", ".txt"}:
        text = path.read_text(encoding="utf-8", errors="ignore")
    elif suffix == ".pdf":
        text = _read_pdf(path)
    elif suffix == ".csv":
        text = _read_csv(path)
    else:
        text = path.read_text(encoding="utf-8", errors="ignore")

    title_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else path.stem.replace("_", " ").title()
    return RagDocument(
        doc_id=path.stem,
        text=mask_pii(text),
        source_path=str(path),
        title=title,
        metadata={"suffix": suffix, "file_name": path.name},
    )


def load_corpus(corpus_dir: str | Path) -> list[RagDocument]:
    """
    Yo cargo el corpus propio del proyecto desde una carpeta segura.
    """
    corpus_dir = Path(corpus_dir)
    paths = []
    for pattern in ("*.md", "*.txt", "*.csv", "*.pdf"):
        paths.extend(corpus_dir.rglob(pattern))
    return [load_document(path) for path in sorted(paths)]
