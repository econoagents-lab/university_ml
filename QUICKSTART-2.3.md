# Quickstart v2.3

```powershell
cd machine_learning_university_v2_3_client_proposal_and_contract_automation
python scripts/120_run_v23_client_proposal_and_contract_automation.py
pytest -q
uvicorn api.main:app --reload
```

Abrir:

```text
reports/client_proposals/proposal_index.html
http://127.0.0.1:8000/proposals/clients
http://127.0.0.1:8000/proposal/client/cliente_alpha
```

Variables opcionales:

```powershell
$env:MLU_PROPOSAL_CURRENCY="USD"
$env:MLU_PROPOSAL_DISCOUNT_PCT="0"
```
