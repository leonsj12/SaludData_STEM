from __future__ import annotations

"""
SALUDDATA STEM
Servicio de exploración interactiva de datos - V3

Este módulo permite consultar los datasets procesados de SaludData STEM
mediante filtros interactivos.

Flujo:

    Parquet
       ?
    Carga local
       ?
    Filtros
       ?
    Agregación
       ?
    JSON
       ?
    Dashboard

El módulo trabaja con los archivos Parquet existentes y no modifica
los datos originales.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd


# ============================================================
# 1. RUTA PRINCIPAL DEL PROYECTO
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

PROCESSED = ROOT / "data" / "processed"


# ============================================================
# 2. CONFIGURACIÓN DE LOS DATASETS
# ============================================================

DATASETS = {
    "cardiovascular": {
        "file": "cardiovascular.parquet",
        "locality": "LOCALIDAD",
        "sex": "SEXO",
        "age_group": "EDAD_QUINQUENAL",
        "cause": "CIE10_AGRUPADA",
        "value_mode": "records",
    },

    "respiratorio": {
        "file": "respiratorio.parquet",
        "locality": "LOCALIDAD",
        "sex": "SEXO",
        "age_group": "EDAD_QUINQUENAL",
        "cause": "CIE10_AGRUPADA",
        "value_mode": "records",
    },

    "mortalidad": {
        "file": "mortalidad.parquet",
        "locality": "LOCALIDAD",
        "sex": "SEXO",
        "age_group": "GRUPO DE EDAD",
        "cause": "DESCRIPCION LISTA 105",
        "value_mode": "mortality",
    },
}


# ============================================================
# 3. CARGA DE DATASET
# ============================================================

@lru_cache(maxsize=3)
def cargar_dataset(nombre: str) -> pd.DataFrame:
    """
    Carga un dataset Parquet.

    @lru_cache permite conservar temporalmente los tres datasets
    en memoria para evitar lecturas repetidas del disco.
    """

    if nombre not in DATASETS:
        raise ValueError(
            f"Dataset no soportado: {nombre}"
        )

    configuracion = DATASETS[nombre]

    ruta = PROCESSED / configuracion["file"]

    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {ruta}"
        )

    df = pd.read_parquet(ruta)

    # Normalizamos los nombres de columnas.
    df.columns = [
        str(columna).strip()
        for columna in df.columns
    ]

    return df


# ============================================================
# 4. LIMPIEZA DE VALORES
# ============================================================

def limpiar_valor(valor: Any) -> Any:
    """
    Convierte valores especiales de pandas/numpy en valores
    compatibles con JSON.
    """

    if pd.isna(valor):
        return None

    if isinstance(valor, pd.Timestamp):
        return valor.strftime("%Y-%m-%d")

    if hasattr(valor, "item"):

        try:
            return valor.item()

        except Exception:
            pass

    return valor


# ============================================================
# 5. DATAFRAME ? LISTA DE DICCIONARIOS
# ============================================================

def dataframe_a_records(
    df: pd.DataFrame,
) -> list[dict]:

    """
    Convierte un DataFrame a una estructura compatible
    con respuestas JSON.
    """

    if df.empty:
        return []

    registros = []

    for registro in df.to_dict("records"):

        registros.append(
            {
                str(clave): limpiar_valor(valor)
                for clave, valor in registro.items()
            }
        )

    return registros


# ============================================================
# 6. OPCIONES DISPONIBLES PARA LOS FILTROS
# ============================================================

def obtener_opciones(nombre: str) -> dict:

    """
    Obtiene las categorías disponibles en un dataset.

    Estas opciones serán utilizadas posteriormente para
    construir los controles del dashboard.
    """

    df = cargar_dataset(nombre)

    configuracion = DATASETS[nombre]

    opciones = {
        "years": [],
        "sex": [],
        "locality": [],
        "age_group": [],
        "cause": [],
    }

    # --------------------------------------------------------
    # AÑOS
    # --------------------------------------------------------

    if "ANO" in df.columns:

        years = (
            pd.to_numeric(
                df["ANO"],
                errors="coerce",
            )
            .dropna()
            .astype(int)
            .drop_duplicates()
            .sort_values()
            .tolist()
        )

        opciones["years"] = years

    # --------------------------------------------------------
    # SEXO
    # --------------------------------------------------------

    columna = configuracion["sex"]

    if columna in df.columns:

        opciones["sex"] = sorted(
            {
                str(valor).strip()
                for valor in df[columna].dropna()
            }
        )

    # --------------------------------------------------------
    # LOCALIDAD
    # --------------------------------------------------------

    columna = configuracion["locality"]

    if columna in df.columns:

        opciones["locality"] = sorted(
            {
                str(valor).strip()
                for valor in df[columna].dropna()
            }
        )

    # --------------------------------------------------------
    # GRUPO DE EDAD
    # --------------------------------------------------------

    columna = configuracion["age_group"]

    if columna in df.columns:

        opciones["age_group"] = sorted(
            {
                str(valor).strip()
                for valor in df[columna].dropna()
            }
        )

    # --------------------------------------------------------
    # CAUSA / CATEGORÍA
    # --------------------------------------------------------

    columna = configuracion["cause"]

    if columna in df.columns:

        opciones["cause"] = sorted(
            {
                str(valor).strip()
                for valor in df[columna].dropna()
            }
        )

    return opciones


# ============================================================
# 7. APLICACIÓN DE FILTROS
# ============================================================

def aplicar_filtros(
    nombre: str,
    year: int | None = None,
    sex: str | None = None,
    locality: str | None = None,
    age_group: str | None = None,
    cause: str | None = None,
) -> pd.DataFrame:

    """
    Aplica los filtros recibidos.

    Cada filtro es opcional.
    """

    df = cargar_dataset(nombre).copy()

    configuracion = DATASETS[nombre]

    # --------------------------------------------------------
    # AÑO
    # --------------------------------------------------------

    if year is not None and "ANO" in df.columns:

        df = df[
            pd.to_numeric(
                df["ANO"],
                errors="coerce",
            )
            == int(year)
        ]

    # --------------------------------------------------------
    # SEXO
    # --------------------------------------------------------

    if sex:

        columna = configuracion["sex"]

        if columna in df.columns:

            df = df[
                df[columna]
                .astype(str)
                .str.strip()
                == str(sex).strip()
            ]

    # --------------------------------------------------------
    # LOCALIDAD
    # --------------------------------------------------------

    if locality:

        columna = configuracion["locality"]

        if columna in df.columns:

            df = df[
                df[columna]
                .astype(str)
                .str.strip()
                == str(locality).strip()
            ]

    # --------------------------------------------------------
    # EDAD
    # --------------------------------------------------------

    if age_group:

        columna = configuracion["age_group"]

        if columna in df.columns:

            df = df[
                df[columna]
                .astype(str)
                .str.strip()
                == str(age_group).strip()
            ]

    # --------------------------------------------------------
    # CAUSA
    # --------------------------------------------------------

    if cause:

        columna = configuracion["cause"]

        if columna in df.columns:

            df = df[
                df[columna]
                .astype(str)
                .str.strip()
                == str(cause).strip()
            ]

    return df


# ============================================================
# 8. CÁLCULO DEL VALOR PRINCIPAL
# ============================================================

def calcular_valor(
    df: pd.DataFrame,
    nombre: str,
) -> float:

    """
    Calcula el valor principal de la consulta.

    Para cardiovascular y respiratorio:

        valor = número de registros

    Para mortalidad:

        valor = suma de TOTAL MUERTES
    """

    if df.empty:
        return 0.0

    configuracion = DATASETS[nombre]

    if configuracion["value_mode"] == "mortality":

        if "TOTAL MUERTES" in df.columns:

            valores = pd.to_numeric(
                df["TOTAL MUERTES"],
                errors="coerce",
            ).fillna(0)

            return float(valores.sum())

    return float(len(df))


# ============================================================
# 9. SERIE TEMPORAL
# ============================================================

def serie_temporal_filtrada(
    df: pd.DataFrame,
    nombre: str,
) -> list[dict]:

    """
    Construye una serie temporal a partir del resultado filtrado.
    """

    if df.empty:
        return []

    # --------------------------------------------------------
    # MORTALIDAD
    # --------------------------------------------------------

    if nombre == "mortalidad":

        trabajo = df.copy()

        trabajo["YEAR"] = pd.to_numeric(
            trabajo["ANO"],
            errors="coerce",
        )

        trabajo = trabajo.dropna(
            subset=["YEAR"]
        )

        if "TOTAL MUERTES" in trabajo.columns:

            trabajo["VALUE"] = pd.to_numeric(
                trabajo["TOTAL MUERTES"],
                errors="coerce",
            ).fillna(0)

            resultado = (
                trabajo
                .groupby(
                    "YEAR",
                    as_index=False,
                )["VALUE"]
                .sum()
                .sort_values("YEAR")
            )

        else:

            resultado = (
                trabajo
                .groupby("YEAR")
                .size()
                .reset_index(name="VALUE")
                .sort_values("YEAR")
            )

        return [
            {
                "year": int(row["YEAR"]),
                "label": str(int(row["YEAR"])),
                "value": float(row["VALUE"]),
            }
            for _, row in resultado.iterrows()
        ]

    # --------------------------------------------------------
    # CARDIOVASCULAR / RESPIRATORIO
    # --------------------------------------------------------

    trabajo = df.copy()

    trabajo["YEAR"] = pd.to_numeric(
        trabajo["ANO"],
        errors="coerce",
    )

    trabajo["MONTH"] = pd.to_numeric(
        trabajo["MES"],
        errors="coerce",
    )

    trabajo = trabajo.dropna(
        subset=["YEAR", "MONTH"]
    )

    trabajo["YEAR"] = trabajo["YEAR"].astype(int)
    trabajo["MONTH"] = trabajo["MONTH"].astype(int)

    # Cada fila representa un registro analítico.
    trabajo["VALUE"] = 1.0

    resultado = (
        trabajo
        .groupby(
            ["YEAR", "MONTH"],
            as_index=False,
        )["VALUE"]
        .sum()
        .sort_values(
            ["YEAR", "MONTH"]
        )
    )

    resultado["LABEL"] = (
        resultado["YEAR"].astype(str)
        + "-"
        + resultado["MONTH"]
        .astype(str)
        .str.zfill(2)
    )

    return [
        {
            "year": int(row["YEAR"]),
            "month": int(row["MONTH"]),
            "label": row["LABEL"],
            "value": float(row["VALUE"]),
        }
        for _, row in resultado.iterrows()
    ]


# ============================================================
# 10. DISTRIBUCIÓN POR DIMENSIÓN
# ============================================================

def distribucion_dimension(
    df: pd.DataFrame,
    columna: str,
    nombre: str,
    limite: int = 20,
) -> list[dict]:

    """
    Calcula la distribución de una dimensión.

    Ejemplos:

        localidad ? registros
        sexo ? registros
        edad ? registros
        causa ? registros

    En mortalidad se utiliza TOTAL MUERTES.
    """

    if df.empty:
        return []

    if columna not in df.columns:
        return []

    trabajo = df.copy()

    trabajo["_dimension"] = (
        trabajo[columna]
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # VALOR ANALÍTICO
    # --------------------------------------------------------

    if nombre == "mortalidad":

        if "TOTAL MUERTES" in trabajo.columns:

            trabajo["_value"] = pd.to_numeric(
                trabajo["TOTAL MUERTES"],
                errors="coerce",
            ).fillna(0)

        else:

            trabajo["_value"] = 1.0

    else:

        trabajo["_value"] = 1.0

    # --------------------------------------------------------
    # AGRUPACIÓN
    # --------------------------------------------------------

    resultado = (
        trabajo
        .groupby(
            "_dimension",
            as_index=False,
        )["_value"]
        .sum()
        .sort_values(
            "_value",
            ascending=False,
        )
        .head(limite)
    )

    return [
        {
            "category": str(row["_dimension"]),
            "value": float(row["_value"]),
        }
        for _, row in resultado.iterrows()
    ]


# ============================================================
# 11. EXPLORACIÓN COMPLETA
# ============================================================

def explorar(
    nombre: str,
    year: int | None = None,
    sex: str | None = None,
    locality: str | None = None,
    age_group: str | None = None,
    cause: str | None = None,
) -> dict:

    """
    Ejecuta una consulta completa sobre el dataset.

    Devuelve todos los elementos necesarios para alimentar
    el dashboard interactivo.
    """

    if nombre not in DATASETS:

        raise ValueError(
            f"Dataset no soportado: {nombre}"
        )

    df = aplicar_filtros(
        nombre=nombre,
        year=year,
        sex=sex,
        locality=locality,
        age_group=age_group,
        cause=cause,
    )

    configuracion = DATASETS[nombre]

    resultado = {

        "dataset": nombre,

        "filters": {
            "year": year,
            "sex": sex,
            "locality": locality,
            "age_group": age_group,
            "cause": cause,
        },

        "records": int(len(df)),

        "value": calcular_valor(
            df,
            nombre,
        ),

        "temporal": serie_temporal_filtrada(
            df,
            nombre,
        ),

        "locality": distribucion_dimension(
            df,
            configuracion["locality"],
            nombre,
        ),

        "sex": distribucion_dimension(
            df,
            configuracion["sex"],
            nombre,
        ),

        "age_group": distribucion_dimension(
            df,
            configuracion["age_group"],
            nombre,
        ),

        "cause": distribucion_dimension(
            df,
            configuracion["cause"],
            nombre,
        ),
    }

    return resultado


# ============================================================
# 12. PRUEBA DEL MÓDULO
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("SALUDDATA STEM - EXPLORADOR V3")
    print("=" * 70)

    for nombre in DATASETS:

        print()
        print(f"Dataset: {nombre}")

        df = cargar_dataset(nombre)

        print(
            f"Filas disponibles: {len(df):,}"
        )

        opciones = obtener_opciones(nombre)

        print(
            f"Años: {len(opciones['years'])}"
        )

        print(
            f"Sexos: {len(opciones['sex'])}"
        )

        print(
            f"Localidades: {len(opciones['locality'])}"
        )

        print(
            f"Grupos de edad: {len(opciones['age_group'])}"
        )

        print(
            f"Causas: {len(opciones['cause'])}"
        )

    print()
    print("=" * 70)
    print("Explorador V3 cargado correctamente.")
    print("=" * 70)