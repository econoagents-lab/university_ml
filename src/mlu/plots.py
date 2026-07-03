from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay, PrecisionRecallDisplay


def save_histogram(df: pd.DataFrame, column: str, output_path: Path, title: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df[column].dropna(), bins=30)
    ax.set_title(title)
    ax.set_xlabel(column)
    ax.set_ylabel("Frecuencia")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def save_bar_counts(df: pd.DataFrame, column: str, output_path: Path, title: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    counts = df[column].value_counts().sort_values()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(counts.index.astype(str), counts.values)
    ax.set_title(title)
    ax.set_xlabel("Conteo")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
