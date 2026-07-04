import pandas as pd
from pathlib import Path

path = Path("data/processed/scoring/ranking_operaciones_riesgo_caida.parquet")

df = pd.read_parquet(path)

print("rows:", len(df))
print("columns:", list(df.columns))
print(df.head(10))