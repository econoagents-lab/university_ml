# Siguiente input — prellenado desde historial reciente

Copia este bloque, corrige lo que no sea cierto y devuélvelo para congelar la versión oficial.

```text
Quiero congelar las reglas oficiales para Machine Learning University v0.4.

1. Reglas oficiales de procesos:
- Separación válida = codigo_proforma no nulo + nombre_flujo contiene 'separ' + fecha_inicio no nula. Usar estado='Activo' solo para scoring actual; para entrenamiento histórico permitir Activo/Inactivo si la separación existió antes del snapshot.
- Venta/minuta válida = codigo_proforma no nulo + nombre_flujo contiene 'proceso de venta' o 'minuta'. Fecha oficial tentativa = fecha_fin si existe; fallback fecha_inicio o fecha_contrato.
- Caída válida = fecha_anulacion no nula OR flujo_anulacion='Anulación' OR nombre_flujo contiene 'Anulación' OR momento_caida en ('proceso','venta'). Fecha oficial tentativa = fecha_anulacion; fallback fecha_fin/fecha_inicio.
- Excluir = operaciones sin codigo_proforma, sin fecha_inicio, sin precio de unidad/departamento, tipos de unidad no departamento para el primer modelo. Revisar si excluir cambios de departamento/proyecto.

2. Definición oficial de caída:
Operación separada que registra anulación/caída después de la fecha de snapshot y dentro del horizonte elegido.

3. Horizonte de predicción elegido:
30 días para MVP. Luego comparar 15/45/60 días.

4. Unidad de análisis elegida:
codigo_proforma + codigo_unidad + fecha_snapshot.

5. Tipos de unidad y foco inicial:
Foco inicial: departamentos. Separar estacionamientos, depósitos, locales y otros para modelos/controles posteriores.

6. Columnas disponibles antes del snapshot:
proyecto, asesor, medio_captacion, canal_agrupado, dormitorios, precio_departamento, dias_en_tuberia, tiene_cuota_inicial, cambios_unidad, interacciones_ult_7d, descuento_pct.

7. Umbrales de decisión:
Bajo < 0.40 = seguimiento estándar.
Medio 0.40–0.69 = contacto priorizado en 24 horas.
Alto >= 0.70 = escalar hoy a jefe comercial.

8. Costos económicos aproximados:
Por ahora usar valor_en_riesgo = probabilidad_caida * precio_departamento. Falso negativo cuesta más que falso positivo.

9. Dónde guardar feedback loop:
Pendiente. Recomendación: data/feedback/riesgo_caida_feedback.parquet para MVP; luego Postgres/Supabase.

10. Despliegue objetivo:
Local primero en laptop/Windows + FastAPI. Luego Railway si se requiere URL.
```

## Puntos que debes corregir si están mal

- Fecha oficial de venta/minuta.
- Tratamiento de `estado='Activo'` en entrenamiento histórico.
- Tratamiento de cambios de departamento/proyecto.
- Umbrales de acción real según capacidad del equipo.
- Costos reales.
- Feedback loop oficial.
