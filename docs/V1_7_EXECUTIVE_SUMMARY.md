# V1.7 Executive Summary · Decision Action Feedback Lab

La versión v1.7 convierte el ranking de riesgo en un sistema cerrado de acción y aprendizaje.

## Decisión económica

Priorizar operaciones de riesgo no sirve si la empresa no mide qué acción se tomó y qué resultado produjo. Esta versión crea la capa mínima para medir intervención comercial.

## Componentes

1. Cola segura de acciones.
2. Plantilla de asignación para el equipo comercial.
3. Ingesta de feedback operativo.
4. Evaluación de resultados 7d/30d.
5. Señal de recalibración/retraining.
6. Validación anti-PII.
7. API y dashboard de acción-feedback.

## Recomendación operativa

Usar Lenovo/self-hosted runner para CRM completo y Railway solo para payloads agregados. La carpeta `C:\Repos\freelance\ml_university_ready\data\raw\sperant` es válida como `MLU_PRIVATE_DATA_DIR` si ahí están tus parquets raw exportados.
