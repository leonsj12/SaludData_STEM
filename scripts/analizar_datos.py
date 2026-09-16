from __future__ import annotations

"""
======================================================================
SALUDDATA STEM - MOTOR ANALITICO V1
======================================================================

OBJETIVO
--------
Este modulo transforma los archivos Parquet procesados en pequenos
archivos analiticos optimizados.

La idea es evitar que Flask tenga que recorrer los CSV originales
cada vez que una persona abre el dashboard.

FLUJO DEL PROCESO
-----------------
CSV original
    |
    v
Importacion y limpieza
    |
    v
data/processed/*.parquet
    |
    v
Motor Analitico V1
    |
    +--> Serie temporal
    +--> Localidad
    +--> Sexo
    +--> Grupo de edad
    +--> Causa / categoria
    |
    v
data/analytics/*.parquet
    |
    v
Dashboard Flask

PRINCIPIO STEM
--------------
DATOS -> CALIDAD -> TRANSFORMACION -> AGREGACION -> ANALISIS

IMPORTANTE
-----------
Este proyecto es educativo y de analisis de datos.

No realiza diagnosticos clinicos.
No determina si una persona esta enferma.
No debe interpretarse como una herramienta medica.

Para cardiovascular y respiratorio utilizamos "registros" o
"valores agregados", porque no debemos asumir que cada fila representa
una muerte individual.

Para mortalidad general utilizamos la variable TOTAL MUERTES.
======================================================================
"""

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------
# 1. RUTAS DEL PROYECTO
# ---------------------------------------------------------------------
# Path(__file__) representa este archivo:
#
# SaludData_STEM/
#     scripts/
#         generar_analitica_v1.py
#
# parents[1] nos lleva a la raiz:
#
# SaludData_STEM/
# ---------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

PROCESSED = ROOT / "data" / "processed"
ANALYTICS = ROOT / "data" / "analytics"


# ---------------------------------------------------------------------
# 2. CONFIGURACION DE LOS DATASETS
# ---------------------------------------------------------------------
# Los datasets cardiovascular y respiratorio utilizan columnas
# diferentes a mortalidad general.
#
# Por eso definimos aqui que columna corresponde a cada dimension.
# ---------------------------------------------------------------------

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


# ---------------------------------------------------------------------
# 3. LIMPIEZA DE ETIQUETAS
# ---------------------------------------------------------------------
def limpiar_texto(series: pd.Series) -> pd.Series:
    """
    Normaliza una columna categorica.

    ¿QUE HACE?
    ----------
    Convierte los valores a texto y elimina espacios innecesarios.

    ¿POR QUE?
    ---------
    En datos reales podemos encontrar valores como:

        "Usaquen"
        " Usaquen"
        "Usaquen "

    Estadisticamente pueden representar la misma categoria, pero
    informaticamente son diferentes cadenas.

    Esta funcion reduce ese problema.
    """

    return (
        series.astype("string")
        .str.strip()
        .replace(
            {
                "": pd.NA,
                "nan": pd.NA,
                "None": pd.NA,
                "<NA>": pd.NA,
            }
        )
    )


# ---------------------------------------------------------------------
# 4. CONVERSION DE TOTAL MUERTES
# ---------------------------------------------------------------------
def valor_mortalidad(df: pd.DataFrame) -> pd.Series:
    """
    Convierte TOTAL MUERTES a valores numericos.

    Este procedimiento solamente se utiliza para el dataset de
    mortalidad general.

    No debemos sumar o contar directamente texto cuando queremos
    representar cantidades numericas.
    """

    if "TOTAL MUERTES" not in df.columns:
        return pd.Series(1.0, index=df.index)

    valores = (
        df["TOTAL MUERTES"]
        .astype("string")
        .str.strip()
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    return pd.to_numeric(
        valores,
        errors="coerce"
    ).fillna(0.0)


# ---------------------------------------------------------------------
# 5. CARGAR PARQUET
# ---------------------------------------------------------------------
def cargar_dataset(nombre: str) -> pd.DataFrame:
    """
    Carga un dataset procesado.

    El dashboard NO debe depender de internet para realizar este paso.

    Los datos ya fueron descargados/importados previamente.
    """

    ruta = PROCESSED / f"{nombre}.parquet"

    if not ruta.exists():
        raise FileNotFoundError(
            f"No existe el archivo procesado: {ruta}\n"
            "Ejecute primero: python -m scripts.importar_datos"
        )

    return pd.read_parquet(ruta)


# ---------------------------------------------------------------------
# 6. SERIE TEMPORAL
# ---------------------------------------------------------------------
def crear_serie_temporal(
    nombre: str,
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Crea una serie temporal agregada.

    CARDIOVASCULAR / RESPIRATORIO
    ------------------------------
    Se agregan registros por:

        año + mes

    MORTALIDAD
    ----------
    Se agregan:

        TOTAL MUERTES por año

    Esto permite que el dashboard trabaje con archivos pequeños
    en lugar de recorrer cientos de miles de filas.
    """

    # ---------------------------------------------------------------
    # MORTALIDAD GENERAL
    # ---------------------------------------------------------------
    if nombre == "mortalidad":

        if "ANO" not in df.columns:
            raise ValueError(
                "El dataset de mortalidad no contiene la columna ANO."
            )

        anio = pd.to_numeric(
            df["ANO"],
            errors="coerce"
        )

        valor = valor_mortalidad(df)

        trabajo = pd.DataFrame(
            {
                "year": anio,
                "value": valor,
            }
        )

        trabajo = trabajo.dropna(
            subset=["year"]
        )

        trabajo["year"] = trabajo["year"].astype(int)

        resultado = (
            trabajo
            .groupby("year", as_index=False)["value"]
            .sum()
            .sort_values("year")
        )

        resultado["value"] = resultado["value"].round(2)

        return resultado.reset_index(drop=True)

    # ---------------------------------------------------------------
    # CARDIOVASCULAR / RESPIRATORIO
    # ---------------------------------------------------------------

    if "ANO" not in df.columns:
        raise ValueError(
            f"{nombre} no contiene la columna ANO."
        )

    if "MES" not in df.columns:
        raise ValueError(
            f"{nombre} no contiene la columna MES."
        )

    anio = pd.to_numeric(
        df["ANO"],
        errors="coerce"
    )

    mes = pd.to_numeric(
        df["MES"],
        errors="coerce"
    )

    trabajo = pd.DataFrame(
        {
            "year": anio,
            "month": mes,
            "value": 1.0,
        }
    )

    trabajo = trabajo.dropna(
        subset=["year", "month"]
    )

    trabajo = trabajo[
        trabajo["month"].between(1, 12)
    ]

    trabajo["year"] = trabajo["year"].astype(int)
    trabajo["month"] = trabajo["month"].astype(int)

    resultado = (
        trabajo
        .groupby(
            ["year", "month"],
            as_index=False
        )["value"]
        .sum()
    )

    # ---------------------------------------------------------------
    # Creamos una fecha real para facilitar graficas y ordenamiento.
    # ---------------------------------------------------------------

    resultado["date"] = pd.to_datetime(
        dict(
            year=resultado["year"],
            month=resultado["month"],
            day=1
        ),
        errors="coerce"
    )

    resultado = resultado.sort_values(
        "date"
    )

    resultado["value"] = resultado["value"].round(2)

    return resultado.reset_index(drop=True)


# ---------------------------------------------------------------------
# 7. ANALISIS POR DIMENSION
# ---------------------------------------------------------------------
def analizar_dimension(
    nombre: str,
    df: pd.DataFrame,
    dimension: str
) -> pd.DataFrame:
    """
    Calcula una distribucion agregada.

    Dimensiones disponibles:

        locality
        sex
        age_group
        cause

    Para cardiovascular y respiratorio:
        value = cantidad de registros.

    Para mortalidad:
        value = suma de TOTAL MUERTES.
    """

    columna = DATASETS[nombre][dimension]

    if columna not in df.columns:
        print(
            f"  ADVERTENCIA: no existe la columna "
            f"'{columna}' para {dimension}."
        )

        return pd.DataFrame(
            columns=[
                dimension,
                "value"
            ]
        )

    trabajo = df[[columna]].copy()

    trabajo[dimension] = limpiar_texto(
        trabajo[columna]
    )

    trabajo = trabajo.dropna(
        subset=[dimension]
    )

    # ---------------------------------------------------------------
    # METRICA
    # ---------------------------------------------------------------

    if nombre == "mortalidad":
        trabajo["value"] = valor_mortalidad(
            df.loc[trabajo.index]
        )
    else:
        trabajo["value"] = 1.0

    # ---------------------------------------------------------------
    # AGRUPACION
    # ---------------------------------------------------------------

    resultado = (
        trabajo
        .groupby(
            dimension,
            as_index=False
        )["value"]
        .sum()
    )

    resultado = resultado.sort_values(
        "value",
        ascending=False
    )

    resultado["value"] = resultado["value"].round(2)

    return resultado.reset_index(
        drop=True
    )


# ---------------------------------------------------------------------
# 8. GUARDAR PARQUET
# ---------------------------------------------------------------------
def guardar_parquet(
    df: pd.DataFrame,
    ruta: Path
) -> None:
    """
    Guarda un DataFrame como Parquet.

    Parquet permite trabajar de forma mas eficiente que CSV para
    archivos analiticos que seran consumidos repetidamente.
    """

    ruta.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_parquet(
        ruta,
        index=False
    )


# ---------------------------------------------------------------------
# 9. PROCESAMIENTO DE UN DATASET
# ---------------------------------------------------------------------
def procesar_dataset(
    nombre: str
) -> None:

    print("\n" + "=" * 70)
    print(
        f"DATASET: {nombre.upper()}"
    )
    print("=" * 70)

    # ---------------------------------------------------------------
    # Cargar
    # ---------------------------------------------------------------

    df = cargar_dataset(nombre)

    print(
        f"Filas fuente: {len(df):,}"
    )

    print(
        f"Columnas fuente: {len(df.columns)}"
    )

    # ---------------------------------------------------------------
    # Serie temporal
    # ---------------------------------------------------------------

    serie = crear_serie_temporal(
        nombre,
        df
    )

    sufijo = (
        "annual"
        if nombre == "mortalidad"
        else "monthly"
    )

    ruta_temporal = (
        ANALYTICS
        / f"{nombre}_{sufijo}.parquet"
    )

    guardar_parquet(
        serie,
        ruta_temporal
    )

    print(
        f"Serie temporal: "
        f"{len(serie):,} filas"
    )

    print(
        f"  -> {ruta_temporal.name}"
    )

    # ---------------------------------------------------------------
    # Dimensiones
    # ---------------------------------------------------------------

    dimensiones = [
        "locality",
        "sex",
        "age_group",
        "cause",
    ]

    for dimension in dimensiones:

        resultado = analizar_dimension(
            nombre,
            df,
            dimension
        )

        ruta = (
            ANALYTICS
            / f"{nombre}_{dimension}.parquet"
        )

        guardar_parquet(
            resultado,
            ruta
        )

        print(
            f"{dimension:12s}: "
            f"{len(resultado):,} categorias"
        )

        print(
            f"{'':12s}  -> {ruta.name}"
        )


# ---------------------------------------------------------------------
# 10. FUNCION PRINCIPAL
# ---------------------------------------------------------------------
def main() -> None:
    """
    Punto de entrada del Motor Analitico V1.
    """

    ANALYTICS.mkdir(
        parents=True,
        exist_ok=True
    )

    print()
    print("=" * 70)
    print("SALUDDATA STEM - MOTOR ANALITICO V1")
    print("=" * 70)
    print(
        f"Entrada: {PROCESSED}"
    )
    print(
        f"Salida : {ANALYTICS}"
    )

    errores = []

    for nombre in DATASETS:

        try:

            procesar_dataset(
                nombre
            )

        except Exception as error:

            errores.append(
                (
                    nombre,
                    str(error)
                )
            )

            print()
            print(
                f"ERROR EN {nombre.upper()}:"
            )

            print(
                str(error)
            )

    # ---------------------------------------------------------------
    # RESUMEN
    # ---------------------------------------------------------------

    print()
    print("=" * 70)
    print("RESUMEN MOTOR ANALITICO V1")
    print("=" * 70)

    if errores:

        print(
            "El proceso termino con errores:"
        )

        for nombre, error in errores:
            print(
                f"- {nombre}: {error}"
            )

        raise RuntimeError(
            "Uno o mas datasets no pudieron procesarse."
        )

    print(
        "Todos los datasets fueron procesados correctamente."
    )

    print()
    print(
        "Archivos disponibles en:"
    )

    print(
        ANALYTICS
    )

    print()
    print(
        "Proceso terminado correctamente."
    )


# ---------------------------------------------------------------------
# 11. EJECUCION DIRECTA
# ---------------------------------------------------------------------

if __name__ == "__main__":
    main()