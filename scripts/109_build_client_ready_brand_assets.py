from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.client_ready_branding_and_deployment import build_brand_assets, read_yaml, CONFIG_PATH

if __name__ == "__main__":
    config = read_yaml(CONFIG_PATH)
    print(build_brand_assets(config))
