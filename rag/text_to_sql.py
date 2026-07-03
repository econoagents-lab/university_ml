from __future__ import annotations

from pathlib import Path
import re
import pandas as pd


def infer_sql_from_question(question: str, table_name: str = "mart_project_month") -> str:
    """
    Yo traduzco preguntas de negocio controladas a SQL seguro sobre marts económicos.
    No ejecuto SQL libre inventado por un LLM.
    """
    q = question.lower()
    if "caida" in q or "caída" in q:
        return f"SELECT proyecto, caida_rate, caidas, separaciones FROM {table_name} ORDER BY caida_rate DESC LIMIT 5"
    if "convers" in q or "minuta" in q:
        return f"SELECT proyecto, conversion_sep_minuta, minutas, separaciones FROM {table_name} ORDER BY conversion_sep_minuta DESC LIMIT 5"
    if "precio" in q or "mercado" in q or "brecha" in q:
        return f"SELECT proyecto, distrito, precio_m2_proyecto, precio_m2_mercado_distrito, brecha_precio_m2 FROM {table_name} ORDER BY brecha_precio_m2 DESC LIMIT 5"
    if "tuber" in q or "pipeline" in q:
        return f"SELECT proyecto, tuberia, dias_tuberia_promedio, valor_tuberia FROM {table_name} ORDER BY valor_tuberia DESC LIMIT 5"
    return f"SELECT proyecto, separaciones, minutas, caidas, tuberia FROM {table_name} ORDER BY separaciones DESC LIMIT 5"


def run_sql_question(question: str, mart_path: str | Path = "marts/output/mart_project_month.csv") -> dict:
    """
    Yo ejecuto una consulta SQL segura sobre el mart económico.
    """
    mart_path = Path(mart_path)
    df = pd.read_parquet(mart_path) if mart_path.suffix == ".parquet" else pd.read_csv(mart_path)
    sql = infer_sql_from_question(question)
    try:
        import duckdb
        result = duckdb.sql(sql, connection=duckdb.connect(database=":memory:").register("mart_project_month", df)).df()
    except Exception:
        # Yo uso pandas como fallback para mantener reproducible el notebook.
        if "caida" in question.lower() or "caída" in question.lower():
            result = df.sort_values("caida_rate", ascending=False)[["proyecto", "caida_rate", "caidas", "separaciones"]].head(5)
        elif "convers" in question.lower() or "minuta" in question.lower():
            result = df.sort_values("conversion_sep_minuta", ascending=False)[["proyecto", "conversion_sep_minuta", "minutas", "separaciones"]].head(5)
        elif "precio" in question.lower() or "mercado" in question.lower() or "brecha" in question.lower():
            result = df.sort_values("brecha_precio_m2", ascending=False)[["proyecto", "distrito", "precio_m2_proyecto", "precio_m2_mercado_distrito", "brecha_precio_m2"]].head(5)
        else:
            result = df[["proyecto", "separaciones", "minutas", "caidas", "tuberia"]].head(5)
    return {"sql": sql, "rows": result.to_dict(orient="records")}
