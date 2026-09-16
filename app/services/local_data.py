from __future__ import annotations

"""
======================================================================
SALUDDATA STEM - SERVICIO DE DATOS LOCALES
======================================================================

Este modulo centraliza el acceso a los datos procesados.

El dashboard no descarga datos desde Bogota.

Lee exclusivamente:

    data/processed/*.parquet

y utiliza:

    data/analytics/*.parquet

para las visualizaciones.

Esto reduce dependencia de red y tiempo de procesamiento.
======================================================================
"""

from pathlib import Path
import json

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

PROCESSED = (
    ROOT
    / "data"
    / "processed"
)


SOURCES = {
    "cardiovascular":
        "Mortalidad prematura cardiocerebrovascular",

    "respiratorio":
        "Mortalidad prematura respiratoria",

    "mortalidad":
        "Mortalidad general",
}


# ---------------------------------------------------------------------
# CARGAR DATASET
# ---------------------------------------------------------------------
def load(nombre: str) -> pd.DataFrame:

    ruta = (
        PROCESSED
        / f"{nombre}.parquet"
    )

    if not ruta.exists():
        return pd.DataFrame()

    return pd.read_parquet(
        ruta
    )


# ---------------------------------------------------------------------
# METADATOS
# ---------------------------------------------------------------------
def metadata(nombre: str) -> dict:
    """
    Lee los metadatos generados durante la importacion.
    """

    ruta = (
        PROCESSED
        / f"{nombre}.json"
    )

    if not ruta.exists():
        return {}

    try:

        return json.loads(
            ruta.read_text(
                encoding="utf-8"
            )
        )

    except Exception:

        return {}


# ---------------------------------------------------------------------
# DATOS PARA DASHBOARD
# ---------------------------------------------------------------------
def get_dashboard_data() -> dict:

    from app.services.analytics import (
        obtener_analitica_dashboard
    )

    analitica = (
        obtener_analitica_dashboard()
    )

    tarjetas = {
        nombre: len(
            load(nombre)
        )
        for nombre in SOURCES
    }

    return {
        "cards": tarjetas,
        "analytics": analitica,
        "metadata": {
            nombre:
                metadata(nombre)
            for nombre in SOURCES
        },
    }


# ---------------------------------------------------------------------
# RESUMEN API
# ---------------------------------------------------------------------
def get_api_summary() -> dict:

    return {

        nombre: {
            "records": len(
                load(nombre)
            ),

            "metadata":
                metadata(nombre),
        }

        for nombre in SOURCES
    }