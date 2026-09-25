from __future__ import annotations

"""
======================================================================
SALUDDATA STEM - SERVICIO DE ANALITICA
======================================================================

Este modulo NO procesa los CSV originales.

Su funcion es leer los Parquet pequenos generados previamente por:

    scripts/generar_analitica_v1.py

Esto permite que Flask responda rapidamente.

Arquitectura:

    data/processed
          |
          v
    Motor Analitico V1
          |
          v
    data/analytics
          |
          v
    este modulo
          |
          v
    Flask / API / Dashboard

======================================================================
"""

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------
# RUTA PRINCIPAL
# ---------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

ANALYTICS = (
    ROOT
    / "data"
    / "analytics"
)


DATASETS = (
    "cardiovascular",
    "respiratorio",
    "mortalidad",
)


# ---------------------------------------------------------------------
# LECTURA DE ARCHIVOS ANALITICOS
# ---------------------------------------------------------------------
def leer_analitica(
    nombre: str,
    sufijo: str
) -> pd.DataFrame:
    """
    Lee un archivo Parquet analitico.

    Si el archivo no existe devuelve un DataFrame vacio.

    Esto permite que el dashboard no se caiga completamente cuando
    todavia no se ha generado una determinada analitica.
    """

    ruta = (
        ANALYTICS
        / f"{nombre}_{sufijo}.parquet"
    )

    if not ruta.exists():
        return pd.DataFrame()

    return pd.read_parquet(ruta)


# ---------------------------------------------------------------------
# CONVERSION SEGURA A JSON
# ---------------------------------------------------------------------
def dataframe_a_registros(
    df: pd.DataFrame
) -> list[dict]:
    """
    Convierte un DataFrame a una estructura compatible con JSON.

    Tambien transforma fechas pandas en texto.

    Esto es importante porque Flask utiliza JSON para enviar datos
    al navegador.
    """

    if df.empty:
        return []

    trabajo = df.copy()

    for columna in trabajo.columns:

        if pd.api.types.is_datetime64_any_dtype(
            trabajo[columna]
        ):

            trabajo[columna] = (
                trabajo[columna]
                .dt.strftime("%Y-%m-%d")
            )

    trabajo = trabajo.where(
        pd.notna(trabajo),
        None
    )

    return trabajo.to_dict(
        orient="records"
    )


# ---------------------------------------------------------------------
# SERIE TEMPORAL
# ---------------------------------------------------------------------
def obtener_temporal(
    nombre: str
) -> list[dict]:
    """
    Devuelve la serie temporal del dataset.
    """

    sufijo = (
        "annual"
        if nombre == "mortalidad"
        else "monthly"
    )

    df = leer_analitica(
        nombre,
        sufijo
    )

    if df.empty:
        return []

    # ---------------------------------------------------------------
    # Serie mensual
    # ---------------------------------------------------------------

    if "date" in df.columns:

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

        df["label"] = (
            df["date"]
            .dt.strftime("%Y-%m")
        )

    # ---------------------------------------------------------------
    # Serie anual
    # ---------------------------------------------------------------

    elif "year" in df.columns:

        df["year"] = pd.to_numeric(
            df["year"],
            errors="coerce"
        )

        df["label"] = (
            df["year"]
            .astype("Int64")
            .astype(str)
        )

    return dataframe_a_registros(
        df
    )


# ---------------------------------------------------------------------
# TOP DE UNA DIMENSION
# ---------------------------------------------------------------------
def obtener_dimension(
    nombre: str,
    dimension: str,
    limite: int = 10
) -> list[dict]:
    """
    Devuelve las principales categorias de una dimension.

    Ejemplo:

        obtener_dimension(
            "cardiovascular",
            "locality",
            10
        )
    """

    df = leer_analitica(
        nombre,
        dimension
    )

    if df.empty:
        return []

    df = df.head(
        limite
    )

    return dataframe_a_registros(
        df
    )


# ---------------------------------------------------------------------
# ANALITICA COMPLETA PARA DASHBOARD
# ---------------------------------------------------------------------
def obtener_analitica_dashboard() -> dict:
    """
    Construye la respuesta completa para el dashboard.

    La respuesta se organiza por dataset.

    Ejemplo conceptual:

    {
        "cardiovascular": {
            "temporal": [...],
            "locality": [...],
            "sex": [...],
            "age_group": [...],
            "cause": [...]
        }
    }
    """

    resultado = {}

    for nombre in DATASETS:

        resultado[nombre] = {

            "temporal":
                obtener_temporal(
                    nombre
                ),

            "locality":
                obtener_dimension(
                    nombre,
                    "locality",
                    10
                ),

            "sex":
                obtener_dimension(
                    nombre,
                    "sex",
                    10
                ),

            "age_group":
                obtener_dimension(
                    nombre,
                    "age_group",
                    10
                ),

            "cause":
                obtener_dimension(
                    nombre,
                    "cause",
                    10
                ),
        }

    return resultado
