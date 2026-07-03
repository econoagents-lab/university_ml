# Executive Reporting / Bitácora Runner

Copia `run_executive_reporting_bitacora.ps1` en la raíz de tu proyecto `machine_learning_university` y ejecútalo desde PowerShell.

## Uso rápido

```powershell
.\run_executive_reporting_bitacora.ps1 -Mode safe -InstallDeps
```

## Con Sperant / Redshift

```powershell
.\run_executive_reporting_bitacora.ps1 -Mode sperant -ExtractLimit 1000
```

## Ejecución completa

```powershell
.\run_executive_reporting_bitacora.ps1 -Mode full -RunTests $true
```

## Output

Genera:

```text
reports/executive_runs/<timestamp>/BITACORA_EJECUTIVA.md
reports/executive_runs/<timestamp>/run_manifest.json
reports/executive_runs/<timestamp>/logs/*.log
reports/executive_latest.md
```

## Seguridad

No imprime ni copia `.env`. Solo detecta si existe.
