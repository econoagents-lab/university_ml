from pathlib import Path

from src.mlu.dashboard_generator import (
    GENERATED_DIR,
    INDEX_HTML_PATH,
    INDEX_MD_PATH,
    MANIFEST_PATH,
    dashboard_generator_metadata,
    generate_dashboards_from_catalog,
    validate_generated_dashboards,
)


def test_generate_dashboards_from_catalog_creates_at_least_sixty_dashboards():
    manifest = generate_dashboards_from_catalog()
    assert manifest["total_generated"] >= 60
    assert MANIFEST_PATH.exists()
    assert INDEX_MD_PATH.exists()
    assert INDEX_HTML_PATH.exists()


def test_generated_dashboard_validation_is_ok():
    generate_dashboards_from_catalog()
    report = validate_generated_dashboards()
    assert report["status"] == "ok"
    assert report["total_dashboards"] >= 60
    assert report["errors"] == []


def test_generated_dashboards_include_where_to_change_and_question():
    manifest = generate_dashboards_from_catalog()
    first = manifest["dashboards"][0]
    md_path = Path(first["markdown_path"])
    text = md_path.read_text(encoding="utf-8")
    assert "Pregunta económica" in text
    assert "Donde cambiar" in text
    assert "Acción recomendada" in text


def test_dashboard_generator_metadata_is_safe_and_complete():
    generate_dashboards_from_catalog()
    metadata = dashboard_generator_metadata()
    assert metadata["total_generated"] >= 60
    assert metadata["safe_aggregate_only"] is True
    assert "index.html" in metadata["index_html"]


def test_generated_public_index_exists():
    generate_dashboards_from_catalog()
    assert (GENERATED_DIR / "index.html").exists()
