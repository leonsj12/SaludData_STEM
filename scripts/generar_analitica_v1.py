from __future__ import annotations

"""
======================================================================
SALUDDATA STEM - MOTOR ANALITICO V1
======================================================================

Proposito
---------
Este modulo transforma los datos procesados de SaludData STEM en
pequenas tablas analiticas optimizadas para el dashboard de Flask.

Flujo STEM
----------
DATOS
  |
  v
DATOS PROCESADOS
  |
  v
AGREGACION
  |
  +--> Serie temporal
  |
  +--> Localidad
  |
  +--> Sexo
  |
  +--> Grupo de edad
  |
  +--> Causa / categoria
  |
  v
ARCHIVOS ANALITICOS
  |
  v
DASHBOARD

Principio pedagogico
--------------------
Cada bloque responde:

1. Que hace?
2. Como lo hace?
3. Por que lo hacemos asi?
4. Que concepto STEM estamos aprendiendo?

Importante
----------
Este proyecto tiene finalidad educativa y de investigacion
exploratoria. Los resultados son descriptivos y estadisticos.

No constituye:
- diagnostico medico;
- prediccion clinica;
- recomendacion sanitaria individual;
- sistema de alerta clinica.

La aplicacion analiza datos agregados y abiertos.
======================================================================
"""

from pathlib import Path

import pandas as pd


# ======================================================================
# 1. RUTAS DEL PROYECTO
# ======================================================================
#
# Que hace?
# Define donde estan los datos procesados y donde guardaremos
# los resultados del Motor Analitico V1.
#
# Como lo hace?
# Path(__file__) obtiene la ubicacion de este archivo.
# parents[1] representa la raiz del proyecto SaludData_STEM.
#
# Por que?
# Evita escribir rutas absolutas como:
# C:\Users\Eduardo Leon\...
#
# Esto permite que el proyecto pueda ejecutarse tambien en GitHub,
# otra computadora o un servidor.
#
# Concepto STEM:
# reproducibilidad y portabilidad del software.
# ======================================================================

ROOT = Path(__file__).resolve().parents[1]

PROCESSED = ROOT / "data" / "processed"

ANALYTICS = ROOT / "data" / "analytics"


# ======================================================================
# 2. CONFIGURACION DE LOS DATASETS
# ======================================================================
#
# Aqui definimos como se llaman las columnas importantes de cada fuente.
#
# Es especialmente importante respetar los nombres reales de los
# archivos procesados.
#
# En los datasets cardiovascular y respiratorio las columnas reales
# son:
#
# LOCALIDAD
# SEXO
# EDAD_QUINQUENAL
# CIE10_AGRUPADA
#
# Mortalidad general utiliza:
#
# LOCALIDAD
# SEXO
# GRUPO DE EDAD
# DESCRIPCION LISTA 105
#
# Concepto STEM:
# modelado de datos y configuracion declarativa.
# ======================================================================

DATASETS = {
    "cardiovascular": {
        "locality": "LOCALIDAD",
        "sex": "SEXO",
        "age_group": "EDAD_QUINQUENAL",
        "cause": "CIE10_AGRUPADA",
    },
    "respiratorio": {
        "locality": "LOCALIDAD",
        "sex": "SEXO",
        "age_group": "EDAD_QUINQUENAL",
        "cause": "CIE10_AGRUPADA",
    },
    "mortalidad": {
        "locality": "LOCALIDAD",
        "sex": "SEXO",
        "age_group": "GRUPO DE EDAD",
        "cause": "DESCRIPCION LISTA 105",
    },
}


# ======================================================================
# 3. LIMPIEZA BASICA DE TEXTO
# ======================================================================

def limpiar_texto(series: pd.Series) -> pd.Series:
    """
    Normaliza valores de texto.

    Que hace?
    ----------
    Elimina espacios innecesarios y convierte cadenas vacias
    en valores faltantes.

    Como lo hace?
    -------------
    Utiliza pandas StringDtype y operaciones vectorizadas.

    Por que?
    --------
    Los datos provenientes de diferentes fuentes pueden contener
    pequenas inconsistencias de escritura.

    Concepto STEM:
    ----------
    preparacion y calidad de datos.
    """

    return (
        series.astype("string")
        .str.strip()
        .replace(
            {
                "": pd.NA,
                "nan": pd.NA,
                "None": pd.NA,
            }
        )
    )


# ======================================================================
# 4. CONVERSION DEL VALOR DE MORTALIDAD
# ======================================================================

def valor_mortalidad(df: pd.DataFrame) -> pd.Series:
    """
    Obtiene el numero de muertes registrado en el dataset general.

    Que hace?
    ----------
    Utiliza TOTAL MUERTES como valor cuantitativo.

    Como lo hace?
    -------------
    Convierte la columna a texto primero para poder normalizar
    posibles separadores numericos.

    Por que?
    --------
    En mortalidad general una fila puede representar una categoria
    con un valor agregado de muertes.

    Por eso NO debemos contar simplemente las filas.

    Concepto STEM:
    ----------
    diferencia entre numero de registros y variable de interes.
    """

    if "TOTAL MUERTES" not in df.columns:
        return pd.Series(1.0, index=df.index)

    value = (
        df["TOTAL MUERTES"]
        .astype("string")
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    return pd.to_numeric(
        value,
        errors="coerce"
    ).fillna(0.0)


# ======================================================================
# 5. CARGAR PARQUET
# ======================================================================

def cargar(name: str) -> pd.DataFrame:
    """
    Carga un dataset procesado.

    Que hace?
    ----------
    Busca:

    data/processed/<dataset>.parquet

    Como?
    -----
    Utiliza pandas.read_parquet().

    Por que?
    --------
    Parquet es mas eficiente que CSV para procesamiento analitico.

    Concepto STEM:
    ----------
    almacenamiento columnar y procesamiento eficiente.
    """

    path = PROCESSED / f"{name}.parquet"

    if not path.exists():
        raise FileNotFoundError(
            f"No existe el archivo procesado: {path}\n"
            "Ejecute primero importar_datos.py"
        )

    return pd.read_parquet(path)


# ======================================================================
# 6. SERIE TEMPORAL
# ======================================================================

def serie_temporal(
    name: str,
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Construye una serie temporal agregada.

    Para cardiovascular y respiratorio:
        ANO + MES

    Para mortalidad:
        ANO

    Importante:
    cardiovascular y respiratorio se presentan como conteo de
    registros agregados, no se etiquetan automaticamente como
    numero de muertes.

    Mortalidad utiliza TOTAL MUERTES.
    """

    # --------------------------------------------------------------
    # MORTALIDAD GENERAL
    # --------------------------------------------------------------

    if name == "mortalidad":

        year = pd.to_numeric(
            df["ANO"],
            errors="coerce"
        )

        value = valor_mortalidad(df)

        out = pd.DataFrame(
            {
                "year": year,
                "value": value,
            }
        ).dropna(
            subset=["year"]
        )

        out["year"] = out["year"].astype(int)

        return (
            out
            .groupby(
                "year",
                as_index=False
            )["value"]
            .sum()
            .sort_values("year")
        )

    # --------------------------------------------------------------
    # CARDIOVASCULAR / RESPIRATORIO
    # --------------------------------------------------------------

    year = pd.to_numeric(
        df["ANO"],
        errors="coerce"
    )

    month = pd.to_numeric(
        df["MES"],
        errors="coerce"
    )

    work = pd.DataFrame(
        {
            "year": year,
            "month": month,
            "value": 1.0,
        }
    ).dropna()

    # Solo meses validos.

    work = work[
        work["month"].between(1, 12)
    ]

    out = (
        work
        .groupby(
            ["year", "month"],
            as_index=False
        )["value"]
        .sum()
    )

    out["year"] = out["year"].astype(int)

    out["month"] = out["month"].astype(int)

    # Creamos una fecha real para facilitar graficos
    # y analisis de series temporales.

    out["date"] = pd.to_datetime(
        dict(
            year=out["year"],
            month=out["month"],
            day=1,
        )
    )

    return out.sort_values("date")


# ======================================================================
# 7. ANALISIS POR DIMENSION
# ======================================================================

def dimension(
    name: str,
    df: pd.DataFrame,
    dim: str
) -> pd.DataFrame:
    """
    Genera una tabla agregada por una dimension.

    Dimensiones disponibles:

    - locality
    - sex
    - age_group
    - cause

    Ejemplo:

        localidad -> numero de registros

    Para mortalidad:
        localidad -> suma de TOTAL MUERTES

    Concepto STEM:
    ----------
    agrupacion y agregacion de datos.
    """

    col = DATASETS[name][dim]

    if col not in df.columns:
        return pd.DataFrame(
            columns=[dim, "value"]
        )

    x = df[[col]].copy()

    x[dim] = limpiar_texto(
        x[col]
    )

    x = x.dropna(
        subset=[dim]
    )

    # --------------------------------------------------------------
    # VALOR ANALITICO
    # --------------------------------------------------------------

    if name == "mortalidad":

        x["value"] = valor_mortalidad(
            df.loc[x.index]
        )

    else:

        # En cardiovascular y respiratorio contamos registros.
        x["value"] = 1.0

    # --------------------------------------------------------------
    # AGRUPACION
    # --------------------------------------------------------------

    out = (
        x
        .groupby(
            dim,
            as_index=False
        )["value"]
        .sum()
    )

    return (
        out
        .sort_values(
            "value",
            ascending=False
        )
        .reset_index(drop=True)
    )


# ======================================================================
# 8. EJECUCION PRINCIPAL
# ======================================================================

def main() -> None:
    """
    Ejecuta todo el Motor Analitico V1.

    El resultado sera una coleccion de archivos pequenos
    y optimizados dentro de:

        data/analytics/

    Estos archivos seran utilizados posteriormente por Flask.
    """

    ANALYTICS.mkdir(
        parents=True,
        exist_ok=True
    )

    print()
    print("=" * 70)
    print("SALUDDATA STEM - MOTOR ANALITICO V1")
    print("=" * 70)

    print(f"Entrada : {PROCESSED}")
    print(f"Salida  : {ANALYTICS}")

    # --------------------------------------------------------------
    # PROCESAR CADA DATASET
    # --------------------------------------------------------------

    for name in DATASETS:

        print()
        print("=" * 70)
        print(f"DATASET: {name.upper()}")
        print("=" * 70)

        # ----------------------------------------------------------
        # CARGA
        # ----------------------------------------------------------

        df = cargar(name)

        print(
            f"Filas cargadas: {len(df):,}"
        )

        print(
            f"Columnas: {len(df.columns)}"
        )

        # ----------------------------------------------------------
        # SERIE TEMPORAL
        # ----------------------------------------------------------

        ts = serie_temporal(
            name,
            df
        )

        if name == "mortalidad":

            ts_name = (
                "mortalidad_annual.parquet"
            )

        else:

            ts_name = (
                f"{name}_monthly.parquet"
            )

        ts_path = ANALYTICS / ts_name

        ts.to_parquet(
            ts_path,
            index=False
        )

        print(
            f"Serie temporal: "
            f"{len(ts):,} filas"
        )

        print(
            f"Archivo: {ts_path.name}"
        )

        # ----------------------------------------------------------
        # DIMENSIONES
        # ----------------------------------------------------------

        for dim in [
            "locality",
            "sex",
            "age_group",
            "cause",
        ]:

            out = dimension(
                name,
                df,
                dim
            )

            path = (
                ANALYTICS
                / f"{name}_{dim}.parquet"
            )

            out.to_parquet(
                path,
                index=False
            )

            print(
                f"{dim:12s}: "
                f"{len(out):,} categorias "
                f"-> {path.name}"
            )

    # --------------------------------------------------------------
    # FINAL
    # --------------------------------------------------------------

    print()
    print("=" * 70)
    print("MOTOR ANALITICO V1 TERMINADO CORRECTAMENTE")
    print("=" * 70)
    print()
    print(
        "Los resultados fueron almacenados en:"
    )
    print(
        ANALYTICS
    )
    print()


# ======================================================================
# 9. PUNTO DE ENTRADA
# ======================================================================

if __name__ == "__main__":
    main()