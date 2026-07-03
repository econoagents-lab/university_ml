from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from marts.build_demo_marts import build_project_month_demo
from economic_lab.hypothesis_tests import evaluate_hypotheses
from economic_lab.story_builder import build_table_to_text_corpus


def test_hypothesis_layer_generates_results(tmp_path):
    df = build_project_month_demo(output_dir=tmp_path)
    results = evaluate_hypotheses(tmp_path / "mart_project_month.csv", output_dir=tmp_path / "reports")
    assert results["rows"] == len(df)
    assert len(results["hypotheses"]) >= 4


def test_table_to_text_generates_markdown(tmp_path):
    build_project_month_demo(output_dir=tmp_path)
    out = build_table_to_text_corpus(tmp_path / "mart_project_month.csv", tmp_path / "stories.md")
    assert out.exists()
    assert "Historias table-to-text" in out.read_text(encoding="utf-8")
