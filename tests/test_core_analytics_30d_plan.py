from pathlib import Path
import csv

BASE = Path(__file__).resolve().parents[1]

def test_core_files_exist():
    required = [
        "config/core_analytics_params.yml",
        "tables/30_day_roadmap.csv",
        "tables/metric_contract_matrix.csv",
        "tables/analytics_improvement_backlog.csv",
        "CORE_ANALYTICS_30D_PLAN_v1.md",
    ]
    for path in required:
        assert (BASE / path).exists(), path

def test_forbidden_privacy_terms_declared():
    text = (BASE / "config/core_analytics_params.yml").read_text(encoding="utf-8").lower()
    for term in ["cliente", "documento", "email", "telefono", "credenciales"]:
        assert term in text

def test_roadmap_has_20_days():
    with open(BASE / "tables/30_day_roadmap.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 20
