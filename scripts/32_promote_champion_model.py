from __future__ import annotations

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

import json
import sys
from pathlib import Path

from src.mlu.comparison import select_best_challenger
from src.mlu.registry import promote_champion, registry_metadata


def main() -> None:
    model_id = sys.argv[1] if len(sys.argv) > 1 else None
    if not model_id:
        best = select_best_challenger()
        if not best:
            raise SystemExit("No hay challenger elegible para promoción.")
        model_id = best["model_id"]
    result = promote_champion(model_id, reason="v0.8_policy_or_manual_promotion")
    Path("reports/registry").mkdir(parents=True, exist_ok=True)
    Path("reports/registry/promotion_result.json").write_text(json.dumps(registry_metadata(), indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
