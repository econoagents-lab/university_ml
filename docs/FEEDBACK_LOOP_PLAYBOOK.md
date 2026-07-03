# Playbook de Feedback Loop - Riesgo de Caída

## Principio

Ningún score termina en un número. Termina en una acción, un responsable y una medición del resultado.

## Flujo operativo

```text
ranking diario
→ asesor/jefe comercial revisa top riesgo
→ registra acción tomada
→ se mide resultado 7d / 30d
→ se compara score vs resultado real
→ se reentrena con feedback
```

## Acciones válidas MVP

- `contactado_cliente`
- `contactado_banco`
- `renegociacion_precio`
- `regularizo_cuota_inicial`
- `cambio_unidad`
- `escalado_gerencia`
- `sin_accion`

## Resultados válidos MVP

- `sigue_tuberia`
- `firmo_minuta`
- `cayo`
- `reprogramado`
- `sin_actualizacion`

## Reglas de gobierno

1. Registrar feedback sin modificar el score original.
2. Separar predicción de intervención.
3. Mantener fecha y responsable de cada acción.
4. No usar resultados futuros como feature del mismo snapshot.
5. Medir impacto por cohortes de intervención.
