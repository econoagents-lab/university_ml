# Diccionario inicial de fuentes Sperant/Redshift
Este documento fue generado a partir de los esquemas locales disponibles. No incluye filas, clientes, correos, teléfonos ni credenciales.
## clientes.parquet
- Filas observadas localmente: `135815`
- Columnas: `56`

| Columna | Tipo |
|---|---|
| `fecha_creacion` | `timestamp[ms]` |
| `nombres` | `large_string` |
| `apellidos` | `large_string` |
| `tipo_documento` | `large_string` |
| `documento` | `large_string` |
| `genero` | `large_string` |
| `estado_civil` | `large_string` |
| `email` | `large_string` |
| `telefono` | `large_string` |
| `celulares` | `large_string` |
| `agrupacion_medio_captacion` | `large_string` |
| `medio_captacion` | `large_string` |
| `canal_entrada` | `large_string` |
| `nivel_interes` | `large_string` |
| `fecha_nacimiento` | `large_string` |
| `nacionalidad` | `large_string` |
| `pais` | `large_string` |
| `departamento` | `large_string` |
| `provincia` | `large_string` |
| `distrito` | `large_string` |
| `direccion` | `large_string` |
| `apto` | `large_string` |
| `observacion` | `large_string` |
| `ocupacion` | `large_string` |
| `documento_conyuge` | `large_string` |
| `usuario_creador` | `large_string` |
| `username` | `large_string` |
| `estado` | `large_string` |
| `ultimo_proyecto` | `large_string` |
| `total_unidades_asignadas` | `double` |
| `ultimo_vendedor` | `large_string` |
| `total_interacciones` | `double` |
| `fecha_ultima_interaccion` | `timestamp[ms]` |
| `proyectos_relacionados` | `large_string` |
| `id` | `int64` |
| `codigo_externo_cliente` | `large_string` |
| `rango_edad` | `large_string` |
| `origen` | `large_string` |
| `ultimo_tipo_interaccion` | `large_string` |
| `fecha_actualizacion` | `timestamp[ms]` |
| `autorizacion_uso_datos` | `bool` |
| `autorizacion_publicidad` | `bool` |
| `geo_latitud` | `large_string` |
| `geo_longitud` | `large_string` |
| `geolocalizacion` | `large_string` |
| `cliente_riesgo` | `large_string` |
| `agrupacion_canal_entrada` | `large_string` |
| `tipo_persona` | `large_string` |
| `denominacion` | `large_string` |
| `tipo_financiamiento` | `large_string` |
| `desistido` | `large_string` |
| `razon_desistimiento` | `large_string` |
| `hora_creacion` | `large_string` |
| `fecha_primera_interaccion_manual` | `timestamp[us]` |
| `prioridad` | `large_string` |
| `uuid` | `large_string` |

## datos_extras.parquet
- Filas observadas localmente: `20401`
- Columnas: `7`

| Columna | Tipo |
|---|---|
| `codigo` | `large_string` |
| `nombre` | `large_string` |
| `valor` | `double` |
| `entidad` | `large_string` |
| `id` | `int64` |
| `tipo` | `large_string` |
| `fecha_actualizacion` | `timestamp[ms]` |

## fact_caidas.parquet
- Filas observadas localmente: `0`
- Columnas: `84`

| Columna | Tipo |
|---|---|
| `codigo_proyecto` | `large_string` |
| `nombre_proyecto` | `large_string` |
| `tipo_unidad_principal` | `large_string` |
| `codigo_unidad` | `large_string` |
| `total_unidades` | `double` |
| `codigo_unidades_asignadas` | `large_string` |
| `nombres_cliente` | `large_string` |
| `apellidos_cliente` | `large_string` |
| `documento_cliente` | `large_string` |
| `origen_proforma` | `large_string` |
| `fecha_proforma` | `timestamp[ms]` |
| `codigo_proforma` | `large_string` |
| `numero_contrato` | `large_string` |
| `fecha_contrato` | `null` |
| `modalidad_contrato` | `large_string` |
| `moneda` | `large_string` |
| `tipo_cambio` | `null` |
| `tipo_financiamiento` | `large_string` |
| `banco` | `large_string` |
| `situacion_legal` | `large_string` |
| `documento_representante` | `null` |
| `nombres_usuario` | `large_string` |
| `username` | `large_string` |
| `precio_base_proforma` | `double` |
| `descuento_venta` | `null` |
| `precio_venta` | `double` |
| `aprobador_descuento` | `large_string` |
| `nombre` | `large_string` |
| `premios` | `null` |
| `fecha_inicio` | `timestamp[ms]` |
| `fecha_fin` | `timestamp[ms]` |
| `fecha_expiracion` | `timestamp[ms]` |
| `fecha_impresion_contrato` | `null` |
| `nombre_flujo` | `large_string` |
| `estado` | `large_string` |
| `completado` | `large_string` |
| `total_pagado` | `double` |
| `total_pendiente` | `double` |
| `fecha_analisis` | `timestamp[ms]` |
| `fecha_nif` | `null` |
| `estado_nif` | `large_string` |
| `utm_source` | `null` |
| `utm_medium` | `null` |
| `utm_campaign` | `null` |
| `utm_term` | `null` |
| `utm_content` | `null` |
| `documento_conyuge` | `large_string` |
| `documento_copropietarios` | `large_string` |
| `flujo_anulacion` | `large_string` |
| `fecha_anulacion` | `null` |
| `codigo_externo_venta` | `null` |
| `id` | `int64` |
| `tipo` | `large_string` |
| `fecha_actualizacion` | `timestamp[ms]` |
| `codigo_externo_minuta` | `null` |
| `flujo_error` | `null` |
| `momento_caida` | `large_string` |
| `tipo_cronograma` | `large_string` |
| `estado_contrato` | `large_string` |
| `devolucion` | `null` |
| `fecha_devolucion` | `null` |
| `excedente` | `double` |
| `observacion_devolucion` | `large_string` |
| `motivo_caida` | `null` |
| `nombres_usuario_aprobador` | `large_string` |
| `username_aprobador` | `large_string` |
| `cliente_id` | `int64` |
| `usuario_creador` | `large_string` |
| `username_creador` | `large_string` |
| `usuario_separacion` | `large_string` |
| `codigo_externo_entrega` | `null` |
| `fecha_minuta` | `null` |
| `proforma_id` | `int64` |
| `penalidad` | `null` |
| `proceso_anulacion` | `large_string` |
| `codigo_externo_anulacion_venta` | `null` |
| `terminado` | `null` |
| `paso_actual` | `large_string` |
| `estado_personalizado` | `null` |
| `fecha_caida` | `timestamp[ms]` |
| `nombre_unidad` | `large_string` |
| `fecha_firma` | `timestamp[ms]` |
| `cliente_medio_captacion` | `large_string` |
| `cliente_estado` | `large_string` |

## fact_conversion_leads.parquet
- Filas observadas localmente: `149999`
- Columnas: `26`

| Columna | Tipo |
|---|---|
| `fecha_asignacion` | `timestamp[us]` |
| `asesor` | `large_string` |
| `cliente` | `large_string` |
| `documento_cliente` | `large_string` |
| `celular` | `large_string` |
| `email` | `large_string` |
| `proyecto` | `large_string` |
| `nivel_de_interés` | `large_string` |
| `atendido_por_asesor` | `large_string` |
| `semana_asign` | `large_string` |
| `documento_cliente_norm` | `large_string` |
| `lead_id` | `large_string` |
| `documento` | `large_string` |
| `canal_entrada` | `large_string` |
| `medio_captacion` | `large_string` |
| `agrupacion_medio_captacion` | `large_string` |
| `email_cliente` | `large_string` |
| `celulares` | `large_string` |
| `estado` | `large_string` |
| `tiene_cliente` | `int64` |
| `n_separaciones` | `int64` |
| `n_firmas` | `int64` |
| `n_caidas` | `int64` |
| `tiene_separacion` | `int64` |
| `tiene_firma` | `int64` |
| `tiene_caida` | `int64` |

## fact_firmas_minutas.parquet
- Filas observadas localmente: `0`
- Columnas: `87`

| Columna | Tipo |
|---|---|
| `codigo_proyecto` | `large_string` |
| `nombre_proyecto` | `large_string` |
| `tipo_unidad_principal` | `large_string` |
| `codigo_unidad` | `large_string` |
| `total_unidades` | `double` |
| `codigo_unidades_asignadas` | `large_string` |
| `nombres_cliente` | `large_string` |
| `apellidos_cliente` | `large_string` |
| `documento_cliente` | `large_string` |
| `origen_proforma` | `large_string` |
| `fecha_proforma` | `timestamp[ms]` |
| `codigo_proforma` | `large_string` |
| `numero_contrato` | `large_string` |
| `fecha_contrato` | `null` |
| `modalidad_contrato` | `large_string` |
| `moneda` | `large_string` |
| `tipo_cambio` | `null` |
| `tipo_financiamiento` | `large_string` |
| `banco` | `large_string` |
| `situacion_legal` | `large_string` |
| `documento_representante` | `null` |
| `nombres_usuario` | `large_string` |
| `username` | `large_string` |
| `precio_base_proforma` | `double` |
| `descuento_venta` | `null` |
| `precio_venta` | `double` |
| `aprobador_descuento` | `large_string` |
| `nombre` | `large_string` |
| `premios` | `null` |
| `fecha_inicio` | `timestamp[ms]` |
| `fecha_fin` | `timestamp[ms]` |
| `fecha_expiracion` | `timestamp[ms]` |
| `fecha_impresion_contrato` | `null` |
| `nombre_flujo` | `large_string` |
| `estado` | `large_string` |
| `completado` | `large_string` |
| `total_pagado` | `double` |
| `total_pendiente` | `double` |
| `fecha_analisis` | `timestamp[ms]` |
| `fecha_nif` | `null` |
| `estado_nif` | `large_string` |
| `utm_source` | `null` |
| `utm_medium` | `null` |
| `utm_campaign` | `null` |
| `utm_term` | `null` |
| `utm_content` | `null` |
| `documento_conyuge` | `large_string` |
| `documento_copropietarios` | `large_string` |
| `flujo_anulacion` | `large_string` |
| `fecha_anulacion` | `null` |
| `codigo_externo_venta` | `null` |
| `id` | `int64` |
| `tipo` | `large_string` |
| `fecha_actualizacion` | `timestamp[ms]` |
| `codigo_externo_minuta` | `null` |
| `flujo_error` | `null` |
| `momento_caida` | `large_string` |
| `tipo_cronograma` | `large_string` |
| `estado_contrato` | `large_string` |
| `devolucion` | `null` |
| `fecha_devolucion` | `null` |
| `excedente` | `double` |
| `observacion_devolucion` | `large_string` |
| `motivo_caida` | `null` |
| `nombres_usuario_aprobador` | `large_string` |
| `username_aprobador` | `large_string` |
| `cliente_id` | `int64` |
| `usuario_creador` | `large_string` |
| `username_creador` | `large_string` |
| `usuario_separacion` | `large_string` |
| `codigo_externo_entrega` | `null` |
| `fecha_minuta` | `null` |
| `proforma_id` | `int64` |
| `penalidad` | `null` |
| `proceso_anulacion` | `large_string` |
| `codigo_externo_anulacion_venta` | `null` |
| `terminado` | `null` |
| `paso_actual` | `large_string` |
| `estado_personalizado` | `null` |
| `fecha_firma` | `timestamp[ms]` |
| `firmado` | `large_string` |
| `canal_entrada` | `large_string` |
| `medio_captacion` | `large_string` |
| `email` | `large_string` |
| `celulares` | `large_string` |
| `nombre_unidad` | `large_string` |
| `unidad_total_habitaciones` | `null` |

## fact_leads.parquet
- Filas observadas localmente: `149999`
- Columnas: `12`

| Columna | Tipo |
|---|---|
| `fecha_asignacion` | `timestamp[us]` |
| `asesor` | `large_string` |
| `cliente` | `large_string` |
| `documento_cliente` | `large_string` |
| `celular` | `large_string` |
| `email` | `large_string` |
| `proyecto` | `large_string` |
| `nivel_de_interés` | `large_string` |
| `atendido_por_asesor` | `large_string` |
| `semana_asign` | `large_string` |
| `documento_cliente_norm` | `large_string` |
| `lead_id` | `large_string` |

## fact_leads_enriched.parquet
- Filas observadas localmente: `149999`
- Columnas: `20`

| Columna | Tipo |
|---|---|
| `fecha_asignacion` | `timestamp[us]` |
| `asesor` | `large_string` |
| `cliente` | `large_string` |
| `documento_cliente` | `large_string` |
| `celular` | `large_string` |
| `email` | `large_string` |
| `proyecto` | `large_string` |
| `nivel_de_interés` | `large_string` |
| `atendido_por_asesor` | `large_string` |
| `semana_asign` | `large_string` |
| `documento_cliente_norm` | `large_string` |
| `lead_id` | `large_string` |
| `documento` | `large_string` |
| `canal_entrada` | `large_string` |
| `medio_captacion` | `large_string` |
| `agrupacion_medio_captacion` | `large_string` |
| `email_cliente` | `large_string` |
| `celulares` | `large_string` |
| `estado` | `large_string` |
| `tiene_cliente` | `int64` |

## fact_separacion_cuota_inicial.parquet
- Filas observadas localmente: `0`
- Columnas: `10`

| Columna | Tipo |
|---|---|
| `codigo` | `large_string` |
| `codigo_proforma` | `large_string` |
| `documento_cliente` | `large_string` |
| `codigo_unidad` | `large_string` |
| `codigo_proyecto` | `large_string` |
| `nombres_usuario` | `large_string` |
| `tipo_unidad_principal` | `large_string` |
| `estado` | `large_string` |
| `codigo_unidades_asignadas` | `large_string` |
| `monto_pagado_cuota_inicial` | `null` |

## fact_separaciones.parquet
- Filas observadas localmente: `0`
- Columnas: `94`

| Columna | Tipo |
|---|---|
| `codigo_proyecto` | `large_string` |
| `nombre_proyecto` | `large_string` |
| `tipo_unidad_principal` | `large_string` |
| `codigo_unidad` | `large_string` |
| `total_unidades` | `double` |
| `codigo_unidades_asignadas` | `large_string` |
| `nombres_cliente` | `large_string` |
| `apellidos_cliente` | `large_string` |
| `documento_cliente` | `large_string` |
| `origen_proforma` | `large_string` |
| `fecha_proforma` | `timestamp[ms]` |
| `codigo_proforma` | `large_string` |
| `numero_contrato` | `large_string` |
| `fecha_contrato` | `null` |
| `modalidad_contrato` | `large_string` |
| `moneda` | `large_string` |
| `tipo_cambio` | `null` |
| `tipo_financiamiento` | `large_string` |
| `banco` | `large_string` |
| `situacion_legal` | `large_string` |
| `documento_representante` | `null` |
| `nombres_usuario` | `large_string` |
| `username` | `large_string` |
| `precio_base_proforma` | `double` |
| `descuento_venta` | `null` |
| `precio_venta` | `double` |
| `aprobador_descuento` | `large_string` |
| `nombre` | `large_string` |
| `premios` | `null` |
| `fecha_inicio` | `timestamp[ms]` |
| `fecha_fin` | `timestamp[ms]` |
| `fecha_expiracion` | `timestamp[ms]` |
| `fecha_impresion_contrato` | `null` |
| `nombre_flujo` | `large_string` |
| `estado` | `large_string` |
| `completado` | `large_string` |
| `total_pagado` | `double` |
| `total_pendiente` | `double` |
| `fecha_analisis` | `timestamp[ms]` |
| `fecha_nif` | `null` |
| `estado_nif` | `large_string` |
| `utm_source` | `null` |
| `utm_medium` | `null` |
| `utm_campaign` | `null` |
| `utm_term` | `null` |
| `utm_content` | `null` |
| `documento_conyuge` | `large_string` |
| `documento_copropietarios` | `large_string` |
| `flujo_anulacion` | `large_string` |
| `fecha_anulacion` | `null` |
| `codigo_externo_venta` | `null` |
| `id` | `int64` |
| `tipo` | `large_string` |
| `fecha_actualizacion` | `timestamp[ms]` |
| `codigo_externo_minuta` | `null` |
| `flujo_error` | `null` |
| `momento_caida` | `large_string` |
| `tipo_cronograma` | `large_string` |
| `estado_contrato` | `large_string` |
| `devolucion` | `null` |
| `fecha_devolucion` | `null` |
| `excedente` | `double` |
| `observacion_devolucion` | `large_string` |
| `motivo_caida` | `null` |
| `nombres_usuario_aprobador` | `large_string` |
| `username_aprobador` | `large_string` |
| `cliente_id` | `int64` |
| `usuario_creador` | `large_string` |
| `username_creador` | `large_string` |
| `usuario_separacion` | `large_string` |
| `codigo_externo_entrega` | `null` |
| `fecha_minuta` | `null` |
| `proforma_id` | `int64` |
| `penalidad` | `null` |
| `proceso_anulacion` | `large_string` |
| `codigo_externo_anulacion_venta` | `null` |
| `terminado` | `null` |
| `paso_actual` | `large_string` |
| `estado_personalizado` | `null` |
| `fecha_separacion` | `timestamp[ms]` |
| `fecha_caida` | `timestamp[ms]` |
| `diferencia_dias_separacion_caida` | `int64` |
| `fecha_firma` | `timestamp[ms]` |
| `medio_captacion` | `large_string` |
| `agrupacion_medio_captacion` | `large_string` |
| `canal_entrada` | `large_string` |
| `celulares` | `large_string` |
| `email` | `large_string` |
| `rango_edad` | `null` |
| `genero` | `large_string` |
| `distrito` | `large_string` |
| `ocupacion` | `large_string` |
| `nombre_unidad` | `large_string` |
| `unidad_total_habitaciones` | `null` |

## mart_table_profile.parquet
- Filas observadas localmente: `6`
- Columnas: `5`

| Columna | Tipo |
|---|---|
| `table_name` | `large_string` |
| `rows` | `int64` |
| `columns` | `int64` |
| `null_cells` | `int64` |
| `duplicate_rows` | `int64` |

## procesos.parquet
- Filas observadas localmente: `4609`
- Columnas: `79`

| Columna | Tipo |
|---|---|
| `codigo_proyecto` | `large_string` |
| `nombre_proyecto` | `large_string` |
| `tipo_unidad_principal` | `large_string` |
| `codigo_unidad` | `large_string` |
| `total_unidades` | `double` |
| `codigo_unidades_asignadas` | `large_string` |
| `nombres_cliente` | `large_string` |
| `apellidos_cliente` | `large_string` |
| `documento_cliente` | `large_string` |
| `origen_proforma` | `large_string` |
| `fecha_proforma` | `timestamp[ms]` |
| `codigo_proforma` | `large_string` |
| `numero_contrato` | `large_string` |
| `fecha_contrato` | `large_string` |
| `modalidad_contrato` | `large_string` |
| `moneda` | `large_string` |
| `tipo_cambio` | `large_string` |
| `tipo_financiamiento` | `large_string` |
| `banco` | `large_string` |
| `situacion_legal` | `large_string` |
| `documento_representante` | `large_string` |
| `nombres_usuario` | `large_string` |
| `username` | `large_string` |
| `precio_base_proforma` | `double` |
| `descuento_venta` | `large_string` |
| `precio_venta` | `double` |
| `aprobador_descuento` | `large_string` |
| `nombre` | `large_string` |
| `premios` | `large_string` |
| `fecha_inicio` | `timestamp[ms]` |
| `fecha_fin` | `timestamp[ms]` |
| `fecha_expiracion` | `timestamp[ms]` |
| `fecha_impresion_contrato` | `large_string` |
| `nombre_flujo` | `large_string` |
| `estado` | `large_string` |
| `completado` | `large_string` |
| `total_pagado` | `double` |
| `total_pendiente` | `double` |
| `fecha_analisis` | `timestamp[ms]` |
| `fecha_nif` | `large_string` |
| `estado_nif` | `large_string` |
| `utm_source` | `large_string` |
| `utm_medium` | `large_string` |
| `utm_campaign` | `large_string` |
| `utm_term` | `large_string` |
| `utm_content` | `large_string` |
| `documento_conyuge` | `large_string` |
| `documento_copropietarios` | `large_string` |
| `flujo_anulacion` | `large_string` |
| `fecha_anulacion` | `large_string` |
| `codigo_externo_venta` | `large_string` |
| `id` | `int64` |
| `tipo` | `large_string` |
| `fecha_actualizacion` | `timestamp[ms]` |
| `codigo_externo_minuta` | `large_string` |
| `flujo_error` | `large_string` |
| `momento_caida` | `large_string` |
| `tipo_cronograma` | `large_string` |
| `estado_contrato` | `large_string` |
| `devolucion` | `large_string` |
| `fecha_devolucion` | `large_string` |
| `excedente` | `double` |
| `observacion_devolucion` | `large_string` |
| `motivo_caida` | `large_string` |
| `nombres_usuario_aprobador` | `large_string` |
| `username_aprobador` | `large_string` |
| `cliente_id` | `int64` |
| `usuario_creador` | `large_string` |
| `username_creador` | `large_string` |
| `usuario_separacion` | `large_string` |
| `codigo_externo_entrega` | `large_string` |
| `fecha_minuta` | `large_string` |
| `proforma_id` | `int64` |
| `penalidad` | `large_string` |
| `proceso_anulacion` | `large_string` |
| `codigo_externo_anulacion_venta` | `large_string` |
| `terminado` | `large_string` |
| `paso_actual` | `large_string` |
| `estado_personalizado` | `large_string` |

## product_stock_pricing.parquet
- Filas observadas localmente: `217`
- Columnas: `11`

| Columna | Tipo |
|---|---|
| `product_name` | `large_string` |
| `title` | `large_string` |
| `domain` | `large_string` |
| `grain` | `large_string` |
| `rows` | `int64` |
| `nombre_proyecto` | `large_string` |
| `tipo_unidad` | `large_string` |
| `estado_comercial` | `large_string` |
| `total_unidades` | `int64` |
| `precio_m2_promedio` | `double` |
| `precio_base_promedio` | `double` |

## proforma_unidad.parquet
- Filas observadas localmente: `40577`
- Columnas: `28`

| Columna | Tipo |
|---|---|
| `id` | `int64` |
| `codigo_proyecto` | `large_string` |
| `nombre_proyecto` | `large_string` |
| `codigo_unidad` | `large_string` |
| `nombre_unidad` | `large_string` |
| `codigo_proforma` | `large_string` |
| `tipo_unidad` | `large_string` |
| `precio_venta` | `double` |
| `asignacion` | `large_string` |
| `estado` | `large_string` |
| `fecha_creacion` | `timestamp[ms]` |
| `usuario_creador` | `large_string` |
| `tipo_financiamiento` | `large_string` |
| `documento_cliente` | `large_string` |
| `afecto_igv` | `large_string` |
| `fecha_actualizacion` | `timestamp[ms]` |
| `nota_proforma` | `large_string` |
| `nombre_plantilla` | `large_string` |
| `moneda` | `large_string` |
| `banco` | `large_string` |
| `username_creador` | `large_string` |
| `lista_metraje` | `large_string` |
| `area_techada` | `large_string` |
| `area_libre` | `large_string` |
| `fecha_expiracion` | `timestamp[us]` |
| `uuid` | `large_string` |
| `corredor` | `large_string` |
| `cliente_id` | `int64` |

## proyectos.parquet
- Filas observadas localmente: `18`
- Columnas: `27`

| Columna | Tipo |
|---|---|
| `id` | `int64` |
| `codigo` | `large_string` |
| `nombre` | `large_string` |
| `direccion` | `large_string` |
| `fecha_estimacion` | `timestamp[ms]` |
| `fecha_real` | `large_string` |
| `latitud` | `double` |
| `longitud` | `double` |
| `pais` | `large_string` |
| `departamento` | `large_string` |
| `provincia` | `large_string` |
| `distrito` | `large_string` |
| `usuario_creador` | `large_string` |
| `username` | `large_string` |
| `tipo_proyecto` | `large_string` |
| `estado_construccion` | `large_string` |
| `total_unidades` | `double` |
| `unidades_vendidas` | `int64` |
| `moneda` | `large_string` |
| `codigo_externo` | `large_string` |
| `tasa_interes_mensual` | `large_string` |
| `banco_promotor` | `large_string` |
| `fecha_inicio_venta` | `timestamp[ms]` |
| `fecha_actualizacion` | `timestamp[ms]` |
| `razon_social` | `large_string` |
| `direccion_razon_social` | `large_string` |
| `ruc_razon_social` | `large_string` |

## unidades.parquet
- Filas observadas localmente: `3237`
- Columnas: `41`

| Columna | Tipo |
|---|---|
| `codigo` | `large_string` |
| `nombre` | `large_string` |
| `codigo_proyecto` | `large_string` |
| `nombre_proyecto` | `large_string` |
| `codigo_subdivision` | `large_string` |
| `nombre_subdivision` | `large_string` |
| `tipo_unidad` | `large_string` |
| `piso` | `large_string` |
| `estado_construccion` | `large_string` |
| `nombre_tipologia` | `large_string` |
| `total_habitaciones` | `large_string` |
| `total_banos` | `double` |
| `area_libre` | `large_string` |
| `area_techada` | `large_string` |
| `area_total` | `double` |
| `estado_comercial` | `large_string` |
| `estado_personalizado` | `large_string` |
| `codigo_proforma` | `large_string` |
| `precio_lista` | `double` |
| `precio_base_proforma` | `double` |
| `descuento_venta` | `large_string` |
| `precio_venta` | `double` |
| `precio_m2` | `double` |
| `fecha_reserva` | `large_string` |
| `fecha_separacion` | `timestamp[ms]` |
| `fecha_venta` | `timestamp[ms]` |
| `fecha_entrega` | `large_string` |
| `fecha_inicio_independizacion` | `large_string` |
| `fecha_fin_independizacion` | `large_string` |
| `modalidad_contrato` | `large_string` |
| `codigo_externo` | `large_string` |
| `fecha_precio_actualizado` | `large_string` |
| `moneda_precio_lista` | `large_string` |
| `moneda_venta` | `large_string` |
| `vcto_garantia_estructural` | `large_string` |
| `vcto_garantia_acabados` | `large_string` |
| `vcto_garantia_comercial` | `large_string` |
| `id` | `int64` |
| `padre_id` | `large_string` |
| `fecha_actualizacion` | `timestamp[ms]` |
| `fecha_estimada_entrega` | `large_string` |

