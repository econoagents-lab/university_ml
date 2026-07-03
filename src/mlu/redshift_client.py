from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
from dotenv import load_dotenv


_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class RedshiftConfig:
    host: str
    port: int
    database: str
    user: str
    password: str
    schema: str

    @classmethod
    def from_env(cls, env_path: str | Path | None = None) -> "RedshiftConfig":
        load_dotenv(env_path)
        required = [
            "REDSHIFT_HOST",
            "REDSHIFT_PORT",
            "REDSHIFT_DATABASE",
            "REDSHIFT_USER",
            "REDSHIFT_PASSWORD",
            "REDSHIFT_SCHEMA",
        ]
        missing = [key for key in required if not os.getenv(key)]
        if missing:
            raise RuntimeError(
                "Faltan variables de entorno para Redshift: " + ", ".join(missing)
            )
        return cls(
            host=os.environ["REDSHIFT_HOST"],
            port=int(os.environ["REDSHIFT_PORT"]),
            database=os.environ["REDSHIFT_DATABASE"],
            user=os.environ["REDSHIFT_USER"],
            password=os.environ["REDSHIFT_PASSWORD"],
            schema=os.environ["REDSHIFT_SCHEMA"],
        )


def _safe_identifier(value: str) -> str:
    if not _IDENTIFIER_RE.match(value):
        raise ValueError(f"Identificador SQL inseguro o inválido: {value!r}")
    return value


def get_connection(config: RedshiftConfig):
    """Crea conexión Redshift solo cuando el usuario ejecuta el extractor.

    redshift_connector queda como dependencia explícita, pero se importa aquí para que
    los notebooks y tests funcionen aunque el alumno todavía no haya configurado credenciales.
    """
    try:
        import redshift_connector
    except ImportError as exc:
        raise ImportError(
            "Instala redshift_connector con: pip install redshift-connector"
        ) from exc

    return redshift_connector.connect(
        host=config.host,
        port=config.port,
        database=config.database,
        user=config.user,
        password=config.password,
    )


def extract_table_to_parquet(
    table: str,
    output_dir: Path,
    config: RedshiftConfig | None = None,
    limit: int | None = None,
) -> Path:
    config = config or RedshiftConfig.from_env()
    schema = _safe_identifier(config.schema)
    table = _safe_identifier(table.strip())

    query = f"SELECT * FROM {schema}.{table}"
    if limit is not None and limit > 0:
        query += f" LIMIT {int(limit)}"

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{table}.parquet"

    with get_connection(config) as conn:
        df = pd.read_sql(query, conn)
    df.to_parquet(out_path, index=False)
    return out_path


def extract_many_tables(
    tables: Iterable[str],
    output_dir: Path,
    config: RedshiftConfig | None = None,
    limit: int | None = None,
) -> list[Path]:
    config = config or RedshiftConfig.from_env()
    outputs: list[Path] = []
    for table in tables:
        table = table.strip()
        if not table:
            continue
        outputs.append(extract_table_to_parquet(table, output_dir, config=config, limit=limit))
    return outputs
