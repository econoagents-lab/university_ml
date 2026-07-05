from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from api.main import app
from src.mlu.dashboard_generator import generate_dashboards_from_catalog


def main() -> None:
    """
    Yo valido que los links generados del catálogo abran en Railway/FastAPI y no devuelvan Not Found.
    """
    generate_dashboards_from_catalog()
    client = TestClient(app)
    paths = [
        "/dashboard/catalog",
        "/dashboard/reports/generated_dashboards/executive/ceo_brief.html",
        "/dashboard/executive/ceo_brief.html",
        "/dashboard/reports/generated_dashboards/commercial/funnel_global.html",
    ]
    failures: list[str] = []
    for path in paths:
        response = client.get(path)
        print(path, response.status_code)
        if response.status_code != 200:
            failures.append(f"{path} -> {response.status_code}: {response.text[:120]}")
    if failures:
        raise SystemExit("\n".join(failures))


if __name__ == "__main__":
    main()
