from __future__ import annotations

from pathlib import Path
import json
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

SQL_PATH = Path("sql/feedback_store_supabase_schema.sql")
DOC_PATH = Path("docs/SUPABASE_FEEDBACK_STORE.md")

SQL = """
-- Machine Learning University v0.7 - Feedback Store Schema
-- Compatible con PostgreSQL / Supabase.

create table if not exists ml_prediction_log (
    prediction_id bigserial primary key,
    created_at timestamptz default now(),
    model_version text not null,
    codigo_proforma text,
    codigo_unidad text,
    fecha_score date not null,
    riesgo_caida numeric,
    nivel_riesgo text,
    ranking_prioridad integer,
    valor_esperado_en_riesgo numeric,
    payload jsonb
);

create table if not exists ml_feedback_log (
    feedback_id bigserial primary key,
    created_at timestamptz default now(),
    codigo_proforma text,
    codigo_unidad text,
    fecha_score date,
    accion_tomada text,
    fecha_accion date,
    resultado_7d text,
    resultado_30d text,
    caida_real_30d boolean,
    comentario text
);

create table if not exists ml_experiment_assignments (
    assignment_id bigserial primary key,
    created_at timestamptz default now(),
    experiment_name text not null,
    experiment_version text not null,
    codigo_proforma text,
    codigo_unidad text,
    experiment_group text not null,
    is_eligible boolean default true,
    random_value numeric
);

create table if not exists ml_monitoring_runs (
    monitoring_run_id bigserial primary key,
    created_at timestamptz default now(),
    model_version text,
    global_status text,
    feature_drift jsonb,
    prediction_drift jsonb,
    calibration jsonb,
    notes text
);
""".strip() + "\n"


def main() -> None:
    SQL_PATH.parent.mkdir(parents=True, exist_ok=True)
    SQL_PATH.write_text(SQL, encoding="utf-8")
    print(json.dumps({"sql_path": str(SQL_PATH), "doc_path": str(DOC_PATH)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
