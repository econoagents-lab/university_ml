# Private Data Dir Guide

## Qué poner en `MLU_PRIVATE_DATA_DIR`

Debes poner la carpeta donde viven tus parquets CRM privados. Si tus tablas raw están aquí:

```text
C:\Repos\freelance\ml_university_ready\data\raw\sperant
```

entonces esa es la ruta correcta.

## Windows PowerShell

```powershell
$env:MLU_PRIVATE_DATA_DIR="C:\Repos\freelance\ml_university_ready\data\raw\sperant"
python scripts/88_run_v16_real_mart_expansion.py
python scripts/94_run_v17_decision_action_feedback_lab.py
```

## Runner v1.7

```powershell
.\run_decision_action_feedback_lab.ps1 -PrivateDataDir "C:\Repos\freelance\ml_university_ready\data\raw\sperant" -RunTests -OpenReport
```

## Regla

No subas esa carpeta a GitHub. Esa ruta es para tu laptop/runner privado. Railway debe recibir solo payloads agregados.
