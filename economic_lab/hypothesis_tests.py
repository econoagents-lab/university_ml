from __future__ import annotations

from pathlib import Path
import json
import pandas as pd


def load_project_month_mart(path: str | Path) -> pd.DataFrame:
    """
    Yo cargo el mart mensual por proyecto para probar hipótesis económicas antes de enviar evidencia al RAG.
    """
    path = Path(path)
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def safe_corr(df: pd.DataFrame, x: str, y: str) -> float:
    """
    Yo calculo una correlación simple solo cuando ambas columnas existen y tienen variación suficiente.
    """
    if x not in df.columns or y not in df.columns:
        return float("nan")
    if df[x].nunique(dropna=True) < 2 or df[y].nunique(dropna=True) < 2:
        return float("nan")
    return float(df[[x, y]].corr(numeric_only=True).iloc[0, 1])


def evaluate_hypotheses(project_month_path: str | Path, output_dir: str | Path = "reports/economic_lab") -> dict:
    """
    Yo genero un resumen de hipótesis como evidencia previa al RAG.
    No intento demostrar causalidad; produzco señales exploratorias defendibles.
    """
    df = load_project_month_mart(project_month_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "rows": int(len(df)),
        "hypotheses": []
    }

    checks = [
        ("H01", "dias_tuberia_promedio", "caida_rate", "positivo", "Tubería envejecida vs caída"),
        ("H02", "dias_hasta_cuota_inicial_promedio", "conversion_sep_minuta", "negativo", "Demora cuota inicial vs conversión"),
        ("H03", "brecha_precio_m2", "caida_rate", "positivo", "Brecha precio mercado vs caída"),
        ("H04", "asesores_activos", "conversion_sep_minuta", "positivo", "Cobertura comercial vs conversión"),
    ]

    for hid, x, y, expected, label in checks:
        corr = safe_corr(df, x, y)
        if pd.isna(corr):
            interpretation = "No tengo datos suficientes para evaluar esta hipótesis."
        elif expected == "positivo" and corr > 0:
            interpretation = "La señal observada va en la dirección esperada."
        elif expected == "negativo" and corr < 0:
            interpretation = "La señal observada va en la dirección esperada."
        else:
            interpretation = "La señal observada no confirma la dirección esperada; debo revisar segmentación o más datos."
        results["hypotheses"].append({
            "id": hid,
            "label": label,
            "x": x,
            "y": y,
            "correlation": None if pd.isna(corr) else round(corr, 4),
            "expected_sign": expected,
            "interpretation": interpretation,
        })

    (output_dir / "hypothesis_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    rows = ["# Resultados de hipótesis económicas", "", "Yo uso esta tabla como antesala del RAG: primero formulo hipótesis, luego busco evidencia.", ""]
    rows.append("| ID | Hipótesis | Variable X | Variable Y | Correlación | Lectura |")
    rows.append("|---|---|---|---|---:|---|")
    for item in results["hypotheses"]:
        rows.append(f"| {item['id']} | {item['label']} | {item['x']} | {item['y']} | {item['correlation']} | {item['interpretation']} |")
    (output_dir / "hypothesis_results.md").write_text("\n".join(rows), encoding="utf-8")
    return results


if __name__ == "__main__":
    evaluate_hypotheses("marts/output/mart_project_month.csv")
