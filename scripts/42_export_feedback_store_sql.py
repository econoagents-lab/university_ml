from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "sql" / "production_feedback_store_schema.sql"
OUT = ROOT / "reports" / "production" / "feedback_store_sql_export.md"


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    text = SQL.read_text(encoding="utf-8") if SQL.exists() else "-- sql not found"
    body = "# Feedback Store SQL Export\n\n```sql\n" + text + "\n```\n"
    OUT.write_text(body, encoding="utf-8")
    print({"output": str(OUT), "sql_exists": SQL.exists()})


if __name__ == "__main__":
    main()
