from __future__ import annotations

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

import json
from pathlib import Path

from src.mlu.figures import build_congress_figure_pack


def main() -> None:
    manifest = build_congress_figure_pack()
    Path("reports/congress").mkdir(parents=True, exist_ok=True)
    md = "# Congress Figure Pack - Riesgo de Caída\n\n"
    md += "Este paquete visual sustenta el modelo como sistema MLOps CRM-first, no como notebook aislado.\n\n"
    for fig in manifest["figures"]:
        md += f"- `{fig}`\n"
    (Path("reports/congress") / "CONGRESS_FIGURE_PACK.md").write_text(md, encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
