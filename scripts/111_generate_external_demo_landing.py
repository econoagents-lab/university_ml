from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlu.client_ready_branding_and_deployment import build_client_ready_manifest, LANDING_HTML

if __name__ == "__main__":
    manifest = build_client_ready_manifest()
    print({"landing": str(LANDING_HTML), "status": manifest.get("release_name")})
