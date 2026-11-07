"""
SALUDDATA STEM
IMPORTADOR LOCAL DE DATOS

Este script incorpora los CSV descargados desde Datos Abiertos
Bogota al sistema SaludData STEM.

Flujo:

data/*.csv
    |
    v
data/raw/*.csv
    |
    v
lectura robusta
    |
    v
validacion
    |
    v
data/processed/*.parquet
    |
    v
metadata

Los archivos CSV originales no se modifican.
"""

from pathlib import Path
import json
from datetime import datetime, timezone

import pandas as pd


# ============================================================
# RUTAS DEL PROYECTO
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
METADATA_DIR = DATA_DIR / "metadata"

for folder in [
    RAW_DIR,
    PROCESSED_DIR,
    METADATA_DIR,
]:
    folder.mkdir(
        parents=True,
        exist_ok=True,
    )


# ============================================================
# DATASETS
# ============================================================

DATASETS = {
    "cardiovascular": {
        "archivo": "osb_cronicas_mpcardiocerebrovasculares.csv",
        "descripcion": (
            "Mortalidad prematura por enfermedad "
            "cardiocerebrovascular en Bogota D.C."
        ),
    },

    "enfermedades_cronicas": {
        "archivo": (
            "mortalidad-prematura-por-"
            "enfermedades-cronicas-general.csv"
        ),
        "descripcion": (
            "Conjunto descargable con multiples categorias de enfermedades cronicas; "
            "el titulo original del catalogo se conserva en metadatos de procedencia."
        ),
    },

    "mortalidad": {
        "archivo": "osb_demografia-causasmortalidadin.csv",
        "descripcion": (
            "Mortalidad general en Bogota D.C."
        ),
    },
}


# ============================================================
# LECTURA ROBUSTA DE CSV
# ============================================================

def leer_csv_robusto(ruta):
    """
    Lee un CSV probando diferentes codificaciones.

    Se prueban:
        utf-8-sig
        cp850
        cp1252
        latin-1

    Tambien se detecta si el separador es:
        ;
    o:
        ,
    """

    codificaciones = [
        "utf-8-sig",
        "cp850",
        "cp1252",
        "latin-1",
    ]

    ultimo_error = None

    for encoding in codificaciones:

        try:

            with open(
                ruta,
                "r",
                encoding=encoding,
                errors="strict",
            ) as archivo:

                primera_linea = archivo.readline()

            if ";" in primera_linea:
                separador = ";"
            else:
                separador = ","

            df = pd.read_csv(
                ruta,
                encoding=encoding,
                sep=separador,
                low_memory=False,
            )

            if len(df.columns) <= 1:

                raise ValueError(
                    "El CSV fue interpretado como una sola columna."
                )

            return (
                df,
                encoding,
                separador,
            )

        except Exception as error:

            ultimo_error = error

    raise RuntimeError(
        "No fue posible leer el archivo "
        f"{ruta.name}. "
        f"Ultimo error: {ultimo_error}"
    )


# ============================================================
# PROCESAR DATASET
# ============================================================

def procesar_dataset(
    nombre,
    configuracion,
):

    archivo_origen = (
        DATA_DIR /
        configuracion["archivo"]
    )

    print()
    print("=" * 70)
    print(
        "DATASET: "
        f"{nombre.upper()}"
    )
    print("=" * 70)

    print(
        f"Archivo: {archivo_origen}"
    )

    # --------------------------------------------------------
    # Verificar archivo
    # --------------------------------------------------------

    if not archivo_origen.exists():

        raise FileNotFoundError(
            "No existe el archivo: "
            f"{archivo_origen}"
        )

    tamaño_mb = (
        archivo_origen.stat().st_size
        / (1024 * 1024)
    )

    print(
        f"Tamaño: {tamaño_mb:.2f} MB"
    )

    # --------------------------------------------------------
    # Leer CSV
    # --------------------------------------------------------

    print()
    print("[1] Leyendo CSV...")

    (
        df,
        encoding,
        separador,
    ) = leer_csv_robusto(
        archivo_origen
    )

    print(
        f"[OK] Encoding: {encoding}"
    )

    print(
        f"[OK] Separador: {repr(separador)}"
    )

    print(
        f"[OK] Filas: {len(df):,}"
    )

    print(
        f"[OK] Columnas: {len(df.columns)}"
    )

    # --------------------------------------------------------
    # Limpieza basica
    # --------------------------------------------------------

    print()
    print(
        "[2] Aplicando limpieza basica..."
    )

    df.columns = [
        str(col).strip()
        for col in df.columns
    ]

    df = df.dropna(
        how="all"
    )

    for columna in df.select_dtypes(
        include=["object"]
    ).columns:

        df[columna] = (
            df[columna]
            .astype(str)
            .str.strip()
        )

    print(
        "[OK] Filas despues de limpieza: "
        f"{len(df):,}"
    )

    # --------------------------------------------------------
    # Mostrar columnas
    # --------------------------------------------------------

    print()
    print(
        "[3] Columnas detectadas:"
    )

    for numero, columna in enumerate(
        df.columns,
        start=1,
    ):

        print(
            f"    {numero:02d}. {columna}"
        )

    # --------------------------------------------------------
    # Copiar RAW
    # --------------------------------------------------------

    print()
    print(
        "[4] Guardando copia RAW..."
    )

    raw_path = (
        RAW_DIR /
        f"{nombre}.csv"
    )

    raw_path.write_bytes(
        archivo_origen.read_bytes()
    )

    print(
        f"[OK] {raw_path}"
    )

    # --------------------------------------------------------
    # Crear Parquet
    # --------------------------------------------------------

    print()
    print(
        "[5] Generando Parquet..."
    )

    parquet_path = (
        PROCESSED_DIR /
        f"{nombre}.parquet"
    )

    df.to_parquet(
        parquet_path,
        index=False,
        engine="pyarrow",
    )

    print(
        f"[OK] {parquet_path}"
    )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata = {

        "dataset": nombre,

        "descripcion": (
            configuracion["descripcion"]
        ),

        "fuente": (
            "Datos Abiertos Bogota"
        ),

        "archivo_original": (
            configuracion["archivo"]
        ),

        "archivo_raw": (
            raw_path.name
        ),

        "archivo_processed": (
            parquet_path.name
        ),

        "fecha_importacion_utc": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),

        "filas": int(
            len(df)
        ),

        "columnas": int(
            len(df.columns)
        ),

        "encoding": encoding,

        "separador": separador,

        "columnas_detectadas": (
            list(df.columns)
        ),
        "unidad_analisis": (
            "registros"
        ),
    }

    # The chronic-disease source contains several disease categories.
    # Preserve every category and record its distribution in metadata.
    if nombre == "enfermedades_cronicas" and "CIE10_AGRUPADA" in df.columns:
        counts = df["CIE10_AGRUPADA"].value_counts(dropna=False)
        metadata["columna_categorica_principal"] = "CIE10_AGRUPADA"
        metadata["titulo_catalogo_original"] = (
            "Mortalidad prematura por enfermedades crónicas respiratorias bajas "
            "en Bogotá D.C. (30 a 70 años)"
        )
        metadata["pagina_catalogo_original"] = (
            "https://datosabiertos.bogota.gov.co/dataset/"
            "mortalidad-prematura-por-enfermedades-cronicas-en-bogota"
        )
        metadata["nota_discrepancia_catalogo_contenido"] = (
            "El título de catálogo se conserva para trazabilidad; el CSV descargable "
            "contiene múltiples categorías en CIE10_AGRUPADA, no solo respiratorias bajas."
        )
        metadata["categorias_CIE10_AGRUPADA"] = {
            str(k): int(v) for k, v in counts.items()
        }
        metadata["decision_metodologica"] = (
            "Se conserva el conjunto completo con todas sus categorías; "
            "no se interpreta como una fuente exclusivamente respiratoria."
        )
        metadata["nombre_visible"] = "Enfermedades crónicas"
        metadata["identificador_interno"] = "enfermedades_cronicas"
        metadata["recurso_original"] = (
            "https://datosabiertos.bogota.gov.co/dataset/"
            "9fc1f14b-540b-4adc-93b1-ecd22780d6d2/resource/"
            "f33d3941-9030-4899-9420-42ef8757607b/download/"
            "mortalidad-prematura-por-enfermedades-cronicas-general.csv"
        )
        metadata["rango_edad_catalogo"] = "30 a 70 años"
        metadata["unidad_analisis"] = (
            "registros agregados según las categorías de la fuente; "
            "no asumir una persona única por fila"
        )
        metadata["calidad"] = {
            "valores_faltantes_total": int(df.isna().sum().sum()),
            "duplicados_exactos_detectados": int(df.duplicated().sum()),
            "duplicados_eliminados": 0,
            "nota_duplicados": (
                "Los duplicados se informan, pero no se eliminan automáticamente; "
                "su tratamiento requiere una regla documentada."
            ),
        }
        metadata["porcentaje_categorias_CIE10_AGRUPADA"] = {
            str(k): round(float(v) / len(df) * 100, 4)
            for k, v in counts.items()
        }

    metadata_path = (
        METADATA_DIR /
        f"{nombre}.json"
    )

    with open(
        metadata_path,
        "w",
        encoding="utf-8",
    ) as archivo:

        json.dump(
            metadata,
            archivo,
            ensure_ascii=False,
            indent=2,
        )

    print(
        f"[OK] Metadata: {metadata_path}"
    )

    return {
        "filas": len(df),
        "columnas": len(df.columns),
        "encoding": encoding,
        "separador": separador,
    }


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    print()
    print("=" * 70)
    print(
        "SALUDDATA STEM - IMPORTACION LOCAL"
    )
    print("=" * 70)

    resultados = {}

    for nombre, configuracion in DATASETS.items():

        try:

            resultados[nombre] = (
                procesar_dataset(
                    nombre,
                    configuracion,
                )
            )

        except Exception as error:

            print()
            print(
                f"[ERROR] {nombre.upper()}"
            )

            print(
                str(error)
            )

            resultados[nombre] = None

    # --------------------------------------------------------
    # Resumen
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)

    for nombre, resultado in resultados.items():

        if resultado is None:

            print(
                f"{nombre:15} ERROR"
            )

        else:

            print(
                f"{nombre:15} "
                f"filas={resultado['filas']:>10,} "
                f"columnas={resultado['columnas']:>3}"
            )

    print()
    print(
        "Importacion finalizada."
    )


if __name__ == "__main__":
    main()