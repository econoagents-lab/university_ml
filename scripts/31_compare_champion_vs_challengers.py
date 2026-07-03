from __future__ import annotations

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from pathlib import Path

from src.mlu.comparison import compare_registered_models


def main() -> None:
    out_dir = Path("reports/registry")
    out_dir.mkdir(parents=True, exist_ok=True)
    df = compare_registered_models()
    df.to_csv(out_dir / "champion_vs_challengers.csv", index=False)
    df.to_parquet(out_dir / "champion_vs_challengers.parquet", index=False)
    md = "# Champion vs Challengers\n\n"
    if df.empty:
        md += "No hay modelos registrados todavía.\n"
    else:
        md += df.to_markdown(index=False) + "\n"
        best = df.iloc[0]
        md += f"\n## Lectura ejecutiva\n\nMejor candidato por promotion_score: `{best['model_id']}`.\n"
    (out_dir / "champion_vs_challenger_report.md").write_text(md, encoding="utf-8")
    print(df.to_json(orient="records", indent=2, force_ascii=False))


if __name__ == "__main__":
    main()
