from __future__ import annotations

import io
import re
from typing import Any

import pandas as pd
import requests


CKAN_API = "https://datosabiertos.bogota.gov.co/api/3/action/resource_show"

RESOURCE_IDS = {
    "cardiovascular": "f93bb5af-c4c6-4301-b602-4cbed283134a",
    "respiratoria": "f33d3941-9030-4899-9420-42ef8757607b",
    "mortalidad": "b12e3b26-2b37-4e6b-b819-3c890ce6394c",
}

_CACHE: dict[str, pd.DataFrame] = {}


def _clean_text(value: Any) -> Any:
    if pd.isna(value):
        return value

    value = str(value).strip()
    value = re.sub(r"\s+", " ", value)

    return value


def _repair_text_encoding(df: pd.DataFrame) -> pd.DataFrame:
    """
    Intenta corregir textos con problemas comunes de codificación.
    """
    replacements = {
        "BogotÃ¡": "Bogotá",
        "BOGOTÃ": "BOGOTÁ",
        "MÃ©xico": "México",
        "Mujer": "Mujeres",
        "Hombre": "Hombres",
    }

    for column in df.select_dtypes(include=["object"]).columns:
        df[column] = df[column].map(
            lambda x: replacements.get(str(x), x)
            if pd.notna(x)
            else x
        )

    return df


def _normalize_locality(value: Any) -> Any:
    if pd.isna(value):
        return value

    value = str(value).strip().upper()

    value = value.replace("Á", "A")
    value = value.replace("É", "E")
    value = value.replace("Í", "I")
    value = value.replace("Ó", "O")
    value = value.replace("Ú", "U")

    return value


def _normalize_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    for column in df.select_dtypes(include=["object"]).columns:
        df[column] = df[column].map(_clean_text)

    if "LOCALIDAD" in df.columns:
        df["LOCALIDAD"] = df["LOCALIDAD"].map(_normalize_locality)

    return df


def _download_resource(resource_id: str) -> bytes:
    response = requests.get(
        CKAN_API,
        params={"id": resource_id},
        timeout=60,
    )
    response.raise_for_status()

    payload = response.json()

    if not payload.get("success"):
        raise RuntimeError("CKAN no pudo consultar el recurso.")

    result = payload["result"]
    url = result.get("url")

    if not url:
        raise RuntimeError("El recurso CKAN no tiene una URL válida.")

    file_response = requests.get(url, timeout=120)
    file_response.raise_for_status()

    return file_response.content


def _read_csv(content: bytes) -> pd.DataFrame:
    """
    Intenta leer el CSV usando las codificaciones más habituales
    en los datos abiertos de Bogotá.
    """
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return pd.read_csv(
                io.BytesIO(content),
                encoding=encoding,
                low_memory=False,
            )
        except UnicodeDecodeError:
            continue

    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        1,
        "No fue posible decodificar el archivo CSV.",
    )


def prepare_health_data(
    df: pd.DataFrame,
    fuente: str = "cardiovascular",
) -> pd.DataFrame:
    """
    Limpia y prepara un dataset de salud para el dashboard.
    """
    df = df.copy()

    df = _normalize_text_columns(df)
    df = _repair_text_encoding(df)

    # Convertir año a número cuando exista.
    if "ANO" in df.columns:
        df["ANO"] = pd.to_numeric(df["ANO"], errors="coerce")

    # Convertir mes a número cuando exista.
    if "MES" in df.columns:
        df["MES"] = pd.to_numeric(df["MES"], errors="coerce")

    # Edad.
    if "EDAD_FALLECIDO" in df.columns:
        df["EDAD_FALLECIDO"] = pd.to_numeric(
            df["EDAD_FALLECIDO"],
            errors="coerce",
        )

    # Crear fecha mensual solamente para fuentes que tienen MES.
    if "ANO" in df.columns and "MES" in df.columns:
        valid = (
            df["ANO"].notna()
            & df["MES"].notna()
            & df["MES"].between(1, 12)
        )

        df["date"] = pd.NaT

        df.loc[valid, "date"] = pd.to_datetime(
            {
                "year": df.loc[valid, "ANO"].astype(int),
                "month": df.loc[valid, "MES"].astype(int),
                "day": 1,
            },
            errors="coerce",
        )

        df["year"] = df["ANO"].astype("Int64")
        df["month"] = df["MES"].astype("Int64")

    elif "ANO" in df.columns:
        df["year"] = df["ANO"].astype("Int64")

    # Grupo de edad.
    if "EDAD_QUINQUENAL" in df.columns:
        df["age_group"] = df["EDAD_QUINQUENAL"].astype("string")
    elif "EDAD_FALLECIDO" in df.columns:
        bins = [-1, 4, 14, 24, 34, 44, 54, 64, 74, 84, 200]
        labels = [
            "0-4",
            "5-14",
            "15-24",
            "25-34",
            "35-44",
            "45-54",
            "55-64",
            "65-74",
            "75-84",
            "85+",
        ]

        df["age_group"] = pd.cut(
            df["EDAD_FALLECIDO"],
            bins=bins,
            labels=labels,
            right=True,
        ).astype("string")

    # Para mortalidad general conservamos todos los registros.
    # Para fuentes específicas mantenemos el alcance cardiovascular/
    # respiratorio del proyecto.
    if fuente in {"cardiovascular", "respiratoria"}:
        if "CIE10_AGRUPADA" in df.columns:
            text = (
                df["CIE10_AGRUPADA"]
                .fillna("")
                .astype(str)
                .str.lower()
            )

            pattern = (
                r"corazon|cardio|cerebro|circulator|respir|"
                r"pulmon|bronqu|asma|neumon|epoc"
            )

            filtered = df[text.str.contains(pattern, regex=True, na=False)]

            if len(filtered) > 0:
                df = filtered.copy()

    return df.reset_index(drop=True)


def load_dataset(fuente: str = "cardiovascular") -> pd.DataFrame:
    """
    Carga un dataset desde datos abiertos de Bogotá.

    Los resultados se almacenan temporalmente en memoria para evitar
    descargar repetidamente el mismo recurso durante una sesión de Flask.
    """
    fuente = str(fuente).lower().strip()

    if fuente not in RESOURCE_IDS:
        raise ValueError(
            f"Fuente no válida: {fuente}. "
            f"Opciones: {', '.join(RESOURCE_IDS)}"
        )

    if fuente in _CACHE:
        return _CACHE[fuente].copy()

    resource_id = RESOURCE_IDS[fuente]

    content = _download_resource(resource_id)
    raw_df = _read_csv(content)

    df = prepare_health_data(raw_df, fuente=fuente)

    _CACHE[fuente] = df.copy()

    return df