from __future__ import annotations

from pathlib import Path
import pandas as pd


def build_project_month_demo(output_dir: str | Path = "marts/output") -> pd.DataFrame:
    """
    Yo construyo un mart económico demo y seguro para el trabajo final UNI.
    Uso datos agregados anonimizados, no clientes ni credenciales.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    data = [
        {"periodo_mes": "2026-05", "proyecto": "Proyecto Alpha", "distrito": "Lima Moderna", "separaciones": 16, "minutas": 15, "caidas": 2, "tuberia": 6, "dias_tuberia_promedio": 31, "dias_hasta_cuota_inicial_promedio": 6, "precio_m2_proyecto": 7600, "precio_m2_mercado_distrito": 7200, "asesores_activos": 6, "valor_tuberia": 2381863},
        {"periodo_mes": "2026-05", "proyecto": "Proyecto Beta", "distrito": "Lima Moderna", "separaciones": 11, "minutas": 9, "caidas": 1, "tuberia": 3, "dias_tuberia_promedio": 24, "dias_hasta_cuota_inicial_promedio": 7, "precio_m2_proyecto": 7100, "precio_m2_mercado_distrito": 7000, "asesores_activos": 5, "valor_tuberia": 1191792},
        {"periodo_mes": "2026-05", "proyecto": "Proyecto Gamma", "distrito": "Lima Norte", "separaciones": 5, "minutas": 3, "caidas": 0, "tuberia": 3, "dias_tuberia_promedio": 38, "dias_hasta_cuota_inicial_promedio": 11, "precio_m2_proyecto": 6900, "precio_m2_mercado_distrito": 6500, "asesores_activos": 4, "valor_tuberia": 2046712},
        {"periodo_mes": "2026-05", "proyecto": "Proyecto Delta", "distrito": "Lima Centro", "separaciones": 5, "minutas": 3, "caidas": 3, "tuberia": 0, "dias_tuberia_promedio": 18, "dias_hasta_cuota_inicial_promedio": 10, "precio_m2_proyecto": 6800, "precio_m2_mercado_distrito": 6400, "asesores_activos": 3, "valor_tuberia": 0},
        {"periodo_mes": "2026-05", "proyecto": "Proyecto Epsilon", "distrito": "Lima Moderna", "separaciones": 5, "minutas": 4, "caidas": 0, "tuberia": 1, "dias_tuberia_promedio": 12, "dias_hasta_cuota_inicial_promedio": 5, "precio_m2_proyecto": 7300, "precio_m2_mercado_distrito": 7200, "asesores_activos": 3, "valor_tuberia": 668768},
    ]
    df = pd.DataFrame(data)
    df["conversion_sep_minuta"] = df["minutas"] / df["separaciones"].replace(0, pd.NA)
    df["caida_rate"] = df["caidas"] / df["separaciones"].replace(0, pd.NA)
    df["brecha_precio_m2"] = df["precio_m2_proyecto"] - df["precio_m2_mercado_distrito"]
    df["valor_en_riesgo"] = df["caida_rate"].fillna(0) * df["valor_tuberia"].fillna(0)
    df.to_csv(output_dir / "mart_project_month.csv", index=False)
    try:
        df.to_parquet(output_dir / "mart_project_month.parquet", index=False)
    except Exception:
        pass
    return df


def build_market_demo(output_dir: str | Path = "data/market/gold") -> pd.DataFrame:
    """
    Yo construyo un mart de mercado demo para comparar pricing interno contra contexto externo.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame([
        {"periodo_mes": "2026-05", "distrito": "Lima Moderna", "precio_m2_mercado": 7200, "oferta_activa": 1250, "velocidad_venta_proxy": 0.082},
        {"periodo_mes": "2026-05", "distrito": "Lima Norte", "precio_m2_mercado": 6500, "oferta_activa": 820, "velocidad_venta_proxy": 0.061},
        {"periodo_mes": "2026-05", "distrito": "Lima Centro", "precio_m2_mercado": 6400, "oferta_activa": 540, "velocidad_venta_proxy": 0.056},
    ])
    df.to_csv(output_dir / "mart_market_district_month.csv", index=False)
    return df


if __name__ == "__main__":
    build_project_month_demo()
    build_market_demo()
    print("OK: yo generé marts demo seguros para UNI.")
