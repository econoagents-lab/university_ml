from __future__ import annotations

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

import json
from pathlib import Path

from src.mlu.registry import registry_metadata


def main() -> None:
    result = registry_metadata()
    out_dir = Path("reports/registry")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "model_registry_metadata.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    md = "# Model Registry Metadata\n\n"
    md += f"Estado: **{result['status']}**\n\n"
    md += f"Champion actual: `{result['current_champion']}`\n\n"
    md += f"Modelos registrados: {result['n_registered_models']}\n\n"
    md += f"Datasets registrados: {result['n_dataset_versions']}\n\n"
    md += "## Payload API\n\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```\n"
    (out_dir / "model_registry_metadata.md").write_text(md, encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
