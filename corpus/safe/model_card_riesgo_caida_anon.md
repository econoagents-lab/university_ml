# Model Card · Riesgo de caída inmobiliaria

## Objetivo

El modelo estima la probabilidad de que una separación activa caiga en un horizonte operativo definido. Su objetivo no es reemplazar al asesor, sino priorizar seguimiento comercial.

## Unidad de análisis

Una operación comercial activa asociada a una separación y una unidad inmobiliaria.

## Variables permitidas

- proyecto
- asesor anonimizado
- canal agrupado
- medio de captación
- dormitorios
- precio del departamento
- días en tubería
- tiene cuota inicial
- interacciones recientes
- descuento porcentual

## Columnas prohibidas

- fecha_caida
- motivo_caida
- fecha_anulacion
- estado final posterior
- cualquier variable que solo exista después del evento objetivo

## Decisión de negocio

Si una operación obtiene riesgo alto, el jefe comercial puede priorizar contacto, renegociación, revisión de crédito, seguimiento de cuota inicial o escalamiento.

## Limitaciones

El modelo debe monitorearse por drift. Si la distribución de proyectos, asesores o precios cambia demasiado, el ranking debe usarse con cautela.
