# Quickstart v1.8

```powershell
cd machine_learning_university_v1_8_experimentation_causal_impact_lab
python scripts/99_run_v18_experimentation_causal_impact_lab.py
pytest -q tests/test_experimentation_causal_impact_lab.py
```

Con ruta privada CRM:

```powershell
.\run_experimentation_causal_impact_lab.ps1 -PrivateDataDir "C:\Repos\freelance\ml_university_ready\data\raw\sperant" -RunTests -OpenReport
```

Abre:

```text
reports/experiments/EXPERIMENTATION_CAUSAL_IMPACT_LAB.md
```
## Ejecutar v1.9

```powershell
python scripts/104_run_v19_experiment_power_policy_engine.py
pytest -q tests/test_experiment_power_policy_engine.py
```

O:

```powershell
.\run_experiment_power_policy_engine.ps1 -RunTests -OpenReport
```
