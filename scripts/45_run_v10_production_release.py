from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def export_feedback_sql() -> dict:
    sql = ROOT / "sql" / "production_feedback_store_schema.sql"
    out = ROOT / "reports" / "production" / "feedback_store_sql_export.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    text = sql.read_text(encoding="utf-8") if sql.exists() else "-- sql not found"
    out.write_text("# Feedback Store SQL Export\n\n```sql\n" + text + "\n```\n", encoding="utf-8")
    return {"output": str(out), "sql_exists": sql.exists()}


def main():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT) + (os.pathsep + env.get("PYTHONPATH", "") if env.get("PYTHONPATH") else "")
    print("RUN scripts/41_run_v09_decision_dashboard_pipeline.py", flush=True)
    completed = subprocess.run(
        [sys.executable, "scripts/41_run_v09_decision_dashboard_pipeline.py"],
        cwd=ROOT,
        env=env,
        text=True,
        timeout=180,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)

    print("RUN export feedback SQL", flush=True)
    print(export_feedback_sql(), flush=True)

    from src.mlu.production import build_release_manifest, build_production_readiness

    print("RUN build release manifest", flush=True)
    manifest = build_release_manifest()
    print({"release": manifest["version"]}, flush=True)

    print("RUN production readiness", flush=True)
    readiness = build_production_readiness()
    print({"readiness": readiness["status"], "checks": f"{readiness['checks_ok']}/{readiness['checks_total']}"}, flush=True)

    print({"status": "ok", "release": "v1.0_production_release"}, flush=True)


if __name__ == "__main__":
    main()
