from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

PROJECTS = [
    "Proyecto Aurora", "Proyecto Bruma", "Proyecto Cobalto", "Proyecto Duna",
    "Proyecto Ébano", "Proyecto Faro", "Proyecto Granito", "Proyecto Horizonte",
]
ADVISORS = [
    "Asesor Norte", "Asesora Sur", "Asesor Este", "Asesora Oeste",
    "Asesor Centro", "Asesora Premium", "Asesor Digital",
]
MEDIA = ["sala de ventas", "facebook", "referido", "web", "feria", "portal inmobiliario", "whatsapp"]
CHANNEL_MAP = {
    "sala de ventas": "tradicional",
    "facebook": "digital",
    "referido": "tradicional",
    "web": "digital",
    "feria": "feria",
    "portal inmobiliario": "digital",
    "whatsapp": "digital",
}


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-x))


def generate_synthetic_real_estate_data(n_rows: int = 3000, seed: int = 42) -> pd.DataFrame:
    """Genera un dataset sintético seguro para aprender riesgo de caída.

    La data no intenta copiar clientes reales. Simula una operación inmobiliaria típica:
    separación, tubería, cuota inicial, cambios de unidad y caída a 30 días.
    """
    rng = np.random.default_rng(seed)

    proyecto = rng.choice(PROJECTS, size=n_rows, p=[0.18, 0.16, 0.14, 0.13, 0.12, 0.10, 0.09, 0.08])
    asesor = rng.choice(ADVISORS, size=n_rows)
    medio = rng.choice(MEDIA, size=n_rows, p=[0.25, 0.22, 0.14, 0.13, 0.10, 0.10, 0.06])
    canal = np.array([CHANNEL_MAP[m] for m in medio])

    dormitorios = rng.choice([1, 2, 3], size=n_rows, p=[0.28, 0.39, 0.33])
    base_price = 230000 + dormitorios * 115000
    project_premium = {p: i * 12000 for i, p in enumerate(PROJECTS)}
    precio = np.array([base_price[i] + project_premium[proyecto[i]] for i in range(n_rows)])
    precio = precio + rng.normal(0, 55000, size=n_rows)
    precio = np.clip(precio, 180000, 950000).round(0)

    dias_en_tuberia = rng.gamma(shape=2.2, scale=12.0, size=n_rows).round().astype(int)
    dias_en_tuberia = np.clip(dias_en_tuberia, 0, 180)
    tiene_cuota_inicial = rng.random(n_rows) < np.clip(0.78 - dias_en_tuberia / 350, 0.25, 0.88)
    cambios_unidad = rng.poisson(lam=0.22 + (dias_en_tuberia > 45) * 0.25, size=n_rows)
    cambios_unidad = np.clip(cambios_unidad, 0, 4)
    interacciones_ult_7d = rng.poisson(lam=np.clip(2.2 - dias_en_tuberia / 80, 0.15, 3.5), size=n_rows)
    descuento_pct = np.clip(rng.normal(0.025, 0.018, size=n_rows), 0, 0.10)

    logit = (
        -2.25
        + 0.024 * dias_en_tuberia
        + 0.95 * (~tiene_cuota_inicial)
        + 0.35 * (precio > 620000)
        + 0.35 * (canal == "digital")
        + 0.25 * (canal == "feria")
        + 0.45 * (cambios_unidad >= 1)
        - 0.25 * (interacciones_ult_7d >= 2)
        - 3.2 * descuento_pct
        + rng.normal(0, 0.65, size=n_rows)
    )
    proba_caida = sigmoid(logit)
    caida_30d = rng.random(n_rows) < proba_caida

    fecha_inicio = pd.Timestamp("2025-01-01")
    fecha_sep = fecha_inicio + pd.to_timedelta(rng.integers(0, 520, size=n_rows), unit="D")

    df = pd.DataFrame({
        "id_operacion": [f"OP-{i:06d}" for i in range(1, n_rows + 1)],
        "fecha_separacion": fecha_sep,
        "proyecto": proyecto,
        "asesor": asesor,
        "medio_captacion": medio,
        "canal_agrupado": canal,
        "tipo_unidad": "departamento",
        "dormitorios": dormitorios,
        "precio_departamento": precio,
        "dias_en_tuberia": dias_en_tuberia,
        "tiene_cuota_inicial": tiene_cuota_inicial,
        "cambios_unidad": cambios_unidad,
        "interacciones_ult_7d": interacciones_ult_7d,
        "descuento_pct": descuento_pct.round(4),
        "caida_30d": caida_30d.astype(int),
    })
    return df


def generate_new_cases() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "id_operacion": "NEW-0001",
            "fecha_separacion": "2026-06-01",
            "proyecto": "Proyecto Aurora",
            "asesor": "Asesor Norte",
            "medio_captacion": "facebook",
            "canal_agrupado": "digital",
            "tipo_unidad": "departamento",
            "dormitorios": 3,
            "precio_departamento": 620000,
            "dias_en_tuberia": 45,
            "tiene_cuota_inicial": False,
            "cambios_unidad": 1,
            "interacciones_ult_7d": 0,
            "descuento_pct": 0.03,
        },
        {
            "id_operacion": "NEW-0002",
            "fecha_separacion": "2026-06-02",
            "proyecto": "Proyecto Bruma",
            "asesor": "Asesora Sur",
            "medio_captacion": "sala de ventas",
            "canal_agrupado": "tradicional",
            "tipo_unidad": "departamento",
            "dormitorios": 2,
            "precio_departamento": 410000,
            "dias_en_tuberia": 8,
            "tiene_cuota_inicial": True,
            "cambios_unidad": 0,
            "interacciones_ult_7d": 3,
            "descuento_pct": 0.02,
        },
    ])


def save_sample_data(output_path: Path, new_cases_path: Path, n_rows: int = 3000, seed: int = 42) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    new_cases_path.parent.mkdir(parents=True, exist_ok=True)
    df = generate_synthetic_real_estate_data(n_rows=n_rows, seed=seed)
    df.to_csv(output_path, index=False)
    generate_new_cases().to_csv(new_cases_path, index=False)
