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
