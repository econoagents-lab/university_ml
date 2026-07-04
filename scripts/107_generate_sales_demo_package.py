from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mlu.productized_commercial_intelligence_os import build_productized_os_manifest, validate_productized_os, build_markdown_reports

if __name__ == "__main__":
    manifest = build_productized_os_manifest()
    validation = validate_productized_os()
    build_markdown_reports(manifest, validation)
    print("sales_demo_package_generated")
