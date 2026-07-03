-- Concepto SQL del gold table: riesgo de caída.
-- El script productivo está en Python porque debe crear snapshots temporales sin leakage.
-- Esta query sirve como mapa mental para Analytics Engineering.

WITH procesos_base AS (
    SELECT
        codigo_proforma,
        codigo_unidad,
        nombre_proyecto,
        nombres_usuario AS asesor,
        origen_proforma AS medio_captacion,
        tipo_unidad_principal,
        precio_venta,
        descuento_venta,
        total_pagado,
        nombre_flujo,
        fecha_inicio,
        fecha_anulacion
    FROM {{ schema }}.procesos
),
separaciones AS (
    SELECT *
    FROM procesos_base
    WHERE LOWER(nombre_flujo) LIKE '%separ%'
),
caidas AS (
    SELECT
        codigo_proforma,
        codigo_unidad,
        MIN(COALESCE(fecha_anulacion, fecha_inicio)) AS fecha_caida
    FROM procesos_base
    WHERE LOWER(nombre_flujo) LIKE '%anul%'
       OR fecha_anulacion IS NOT NULL
    GROUP BY 1, 2
)
SELECT
    s.codigo_proforma,
    s.codigo_unidad,
    s.nombre_proyecto,
    s.asesor,
    s.medio_captacion,
    s.fecha_inicio AS fecha_separacion,
    c.fecha_caida
FROM separaciones s
LEFT JOIN caidas c
    ON s.codigo_proforma = c.codigo_proforma
   AND s.codigo_unidad = c.codigo_unidad;
