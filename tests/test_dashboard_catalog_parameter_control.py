from pathlib import Path

from src.mlu.dashboard_control import (
    CATALOG_PATH,
    DASHBOARD_PARAMS_PATH,
    INPUTS_TO_CONFIRM_PATH,
    CONTROL_PANEL_PATH,
    generate_control_panel,
    generate_inputs_to_confirm,
    load_dashboard_catalog,
    load_dashboard_params,
    load_privacy_policy,
    validate_dashboard_catalog,
    validate_recommended_decisions,
)


def test_dashboard_catalog_has_sixty_dashboards():
    catalog = load_dashboard_catalog()
    dashboards = catalog.get("dashboards", [])
    assert len(dashboards) >= 60
    assert {"id", "name", "owner", "audience", "economic_question", "output_path", "params_ref"}.issubset(dashboards[0].keys())


def test_dashboard_catalog_validation_is_ok():
    report = validate_dashboard_catalog()
    assert report["status"] == "ok"
    assert report["total_dashboards"] >= 60
    assert report["errors"] == []


def test_recommended_public_decisions_are_encoded():
    decision_report = validate_recommended_decisions()
    assert decision_report["status"] == "ok"
    checks = decision_report["checks"]
    assert checks["project_names_public"]
    assert checks["advisors_public_anonymized"]
    assert checks["channels_public_visible"]
    assert checks["aggregated_value_at_risk_public"]
    assert checks["top_operations_public_blocked"]
    assert checks["pii_public_blocked"]
    assert checks["railway_aggregated_only"]
    assert checks["lenovo_private_crm"]
    assert checks["github_aggregated_artifacts"]


def test_public_privacy_parameters_block_sensitive_fields():
    params = load_dashboard_params()
    privacy = load_privacy_policy()
    public_params = params["public_dashboard"]
    assert public_params["include_row_level_operations"] is False
    assert public_params["anonymize_advisors"] is True
    assert public_params["data_mode"] == "crm"
    forbidden = {x.lower() for x in privacy["forbidden_public_fields"]}
    assert "cliente" in forbidden
    assert "dni" in forbidden
    assert "email" in forbidden
    assert "telefono" in forbidden or "teléfono" in forbidden
    assert "credenciales" in forbidden


def test_control_panel_and_inputs_to_confirm_are_generated():
    panel = generate_control_panel()
    inputs = generate_inputs_to_confirm()
    assert panel.exists()
    assert inputs.exists()
    text = inputs.read_text(encoding="utf-8")
    assert "Donde cambiar" in text
    assert "MLU_DISABLE_SAMPLE_FALLBACK" in text
    assert "config/privacy_policy.yml" in text
    assert "Railway data strategy" in text


def test_config_files_exist():
    assert CATALOG_PATH.exists()
    assert DASHBOARD_PARAMS_PATH.exists()
    assert Path("config/model_params.yml").exists()
    assert Path("config/privacy_policy.yml").exists()
