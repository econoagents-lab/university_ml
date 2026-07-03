-- Machine Learning University v1.0
-- Feedback store para PostgreSQL/Supabase.
-- Ejecutar en schema de preferencia: public o mlops.

create table if not exists feedback_riesgo_caida (
    feedback_id bigserial primary key,
    codigo_proforma text not null,
    codigo_unidad text,
    fecha_score date,
    riesgo_caida numeric(8,6),
    nivel_riesgo text,
    ranking_prioridad integer,
    responsable text,
    accion_tomada text,
    fecha_accion date,
    resultado_7d text,
    resultado_30d text,
    caida_real_30d text,
    comentario text,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

create index if not exists idx_feedback_riesgo_caida_proforma on feedback_riesgo_caida(codigo_proforma);
create index if not exists idx_feedback_riesgo_caida_responsable on feedback_riesgo_caida(responsable);
create index if not exists idx_feedback_riesgo_caida_fecha_score on feedback_riesgo_caida(fecha_score);

create table if not exists decision_queue_riesgo_caida_snapshot (
    snapshot_id bigserial primary key,
    generated_at timestamptz default now(),
    codigo_proforma text,
    codigo_unidad text,
    proyecto text,
    asesor text,
    riesgo_caida numeric(8,6),
    prioridad_operativa text,
    valor_esperado_en_riesgo numeric(14,2),
    ranking_decision integer,
    accion_operativa text,
    sla_horas integer,
    fecha_limite_accion timestamp
);
