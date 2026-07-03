# Playbook anti-leakage

El sistema separa raw, auditoría, target y model-ready.

## Regla central

Una columna que revela el futuro puede existir para auditoría o construcción del target, pero no puede entrar al modelo ni al scoring.

## Ejemplo

`fecha_caida` puede usarse para definir si una operación cayó dentro del horizonte de evaluación. Sin embargo, debe eliminarse antes de construir la matriz X.

## Decisión técnica

Si una columna prohibida entra a la matriz de features, el pipeline debe fallar. No se debe silenciar el error.
