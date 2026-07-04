from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pathlib import Path
import json
from src.mlu.config import PROJECT_ROOT
from src.mlu.multi_tenant_client_packaging import read_yaml, CONFIG_PATH

if __name__ == '__main__':
    cfg = read_yaml(CONFIG_PATH)
    out_dir = PROJECT_ROOT / 'reports' / 'client_tenants' / 'payload_templates'
    out_dir.mkdir(parents=True, exist_ok=True)
    allowed = cfg.get('defaults', {}).get('allowed_public_payload_fields', [])
    for tenant in cfg.get('tenants', []):
        payload = {key: None for key in allowed}
        payload['tenant_id'] = tenant.get('tenant_id')
        payload['data_mode'] = 'crm_aggregated'
        path = out_dir / f"{tenant.get('tenant_id')}_payload_template.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        print(path)
