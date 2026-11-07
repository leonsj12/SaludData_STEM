"""
SALUDDATA STEM — Procesamiento y normalización de datos.

============================================================
OBJETIVO PEDAGÓGICO
============================================================
Este módulo enseña una parte fundamental de la ciencia de datos:
los datos publicados por una institución no siempre llegan listos
para analizarlos.

Antes de calcular estadísticas debemos:

    1. Leer.
    2. Identificar la estructura.
    3. Comprobar el separador.
    4. Comprobar la codificación.
    5. Normalizar nombres.
    6. Convertir tipos.
    7. Validar.

============================================================
CONCEPTO ETL
============================================================
ETL significa:

    Extract  → extraer datos
    Transform → transformar datos
    Load     → cargar datos

En SaludData STEM la extracción se realiza en el proceso de actualización.
La aplicación Flask utiliza después las versiones locales transformadas.

============================================================
LECCIÓN IMPORTANTE
============================================================
CSV no significa que todos los archivos CSV tengan exactamente la misma
estructura. Un archivo puede utilizar ';' como separador y otro ','.

También pueden existir diferencias de codificación. Por eso el código
prueba varias codificaciones comunes en archivos publicados en Windows.

Este comportamiento no es un "truco": es una estrategia de robustez
frente a datos reales.
"""

from __future__ import annotations

from io import BytesIO
from typing import Iterable

import pandas as pd


ENCODINGS: tuple[str, ...] = (
    "utf-8-sig",
    "cp850",
    "cp1252",
    "latin-1",
)


def read_csv_robust(content: bytes) -> pd.DataFrame:
    """
    Lee un CSV intentando resolver dos problemas frecuentes: separador
    y codificación.

    ¿QUÉ HACE?
        Convierte bytes descargados en un DataFrame.

    ¿CÓMO?
        Primero intenta detectar el separador. Después prueba varias
        codificaciones.

    ¿POR QUÉ?
        Los datos abiertos pueden haber sido generados por herramientas
        diferentes. Una lectura rígida puede producir una sola columna
        cuando el archivo realmente contiene muchas.

    ¿QUÉ APRENDEMOS?
        - bytes vs texto
        - encoding
        - CSV
        - DataFrame
        - manejo de excepciones
    """
    last_error: Exception | None = None

    for encoding in ENCODINGS:
        try:
            text = content.decode(encoding)

            # La mayoría de los archivos tabulares de este proyecto
            # utiliza ';'. Contamos separadores para construir una
            # heurística sencilla y explicable.
            first_lines = "\n".join(text.splitlines()[:10])
            semicolons = first_lines.count(";")
            commas = first_lines.count(",")

            separator = ";" if semicolons > commas else ","

            return pd.read_csv(
                BytesIO(text.encode(encoding)),
                sep=separator,
                low_memory=False,
            )
        except (UnicodeDecodeError, pd.errors.ParserError) as exc:
            last_error = exc

    raise ValueError(
        "No fue posible interpretar el CSV con las codificaciones "
        f"probadas: {ENCODINGS}"
    ) from last_error


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza nombres de columnas sin destruir la estructura original.

    Las columnas se convierten a texto y se eliminan espacios externos.

    La normalización reduce errores cuando una fuente contiene nombres
    con espacios accidentales.
    """
    result = df.copy()
    result.columns = [str(col).strip() for col in result.columns]
    return result


def coerce_numeric(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    """
    Convierte columnas seleccionadas a números cuando existen.

    Los valores imposibles de convertir se convierten en NaN.

    PEDAGOGÍA:
    NaN significa "Not a Number" y permite representar información
    faltante sin inventar un valor.
    """
    result = df.copy()

    for column in columns:
        if column in result.columns:
            result[column] = pd.to_numeric(result[column], errors="coerce")

    return result


def prepare_health_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ejecuta una preparación básica reutilizable.

    FLUJO:

        DataFrame original
             ↓
        columnas normalizadas
             ↓
        ANO/MES numéricos cuando existen
             ↓
        DataFrame preparado

    La función no elimina registros automáticamente. En un proyecto
    científico es preferible hacer explícitas las reglas de limpieza
    para evitar decisiones silenciosas.
    """
    result = normalize_columns(df)

    result = coerce_numeric(result, ["ANO", "MES", "TOTAL MUERTES"])

    return result
