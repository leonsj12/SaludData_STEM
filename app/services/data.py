from __future__ import annotations

import io
from typing import Any

import pandas as pd
import requests


CKAN_API = (
    "https://datosabiertos.bogota.gov.co/api/3/action/resource_show"
)


RESOURCE_IDS = {
    "cardiovascular": (
        "f93bb5af-c4c6-4301-b602-4cbed283134a"
    ),
    "respiratoria": (
        "f33d3941-9030-4899-9420-42ef8757607b"
    ),
    "mortalidad": (
        "b12e3b26-2b37-4e6b-b819-3c890ce6394c"
    ),
}


_CACHE: dict[str, pd.DataFrame] = {}


# ============================================================
# REPARACIONES CONTROLADAS DE TEXTO
# ============================================================

_MOJIBAKE_REPLACEMENTS = {
    "Antonio NariÃ±o": "Antonio Nariño",
    "FontibÃ³n": "Fontibón",
    "a¤os": "años",
    "Usaqu‚n": "Usaquén",
    "San Crist¢bal": "San Cristóbal",
    "Engativ ": "Engativá",
    "M rtires": "Mártires",
    "Los M rtires": "Los Mártires",
    "Ciudad Bol var": "Ciudad Bolívar",
    "Ciudad Bolávar": "Ciudad Bolívar",
    "Ciudad Bol¡var": "Ciudad Bolívar",
    "INFORMACIàN": "INFORMACIÓN",
    "SIN INFORMACIàN": "SIN INFORMACIÓN",
    "00 - Bogot": "00 - Bogotá",
}


def _repair_mojibake(value: Any) -> Any:
    """
    Corrige únicamente secuencias de texto conocidas
    provenientes de la fuente original.
    """

    if pd.isna(value):
        return value

    text = str(value)

    for bad, good in _MOJIBAKE_REPLACEMENTS.items():
        text = text.replace(bad, good)

    return text.strip()


# ============================================================
# DESCARGA DESDE CKAN
# ============================================================

def _download_resource(resource_id: str) -> bytes:
    """
    Consulta CKAN para obtener la URL real del recurso
    y posteriormente descarga el archivo.
    """

    response = requests.get(
        CKAN_API,
        params={"id": resource_id},
        timeout=60,
    )

    response.raise_for_status()

    payload = response.json()

    if not payload.get("success"):
        raise RuntimeError(
            "CKAN no pudo consultar el recurso solicitado."
        )

    url = payload.get("result", {}).get("url")

    if not url:
        raise RuntimeError(
            "El recurso CKAN no contiene una URL válida."
        )

    file_response = requests.get(
        url,
        timeout=120,
    )

    file_response.raise_for_status()

    return file_response.content


# ============================================================
# LECTURA CSV
# ============================================================

def _read_csv(content: bytes) -> pd.DataFrame:
    """
    Lee los CSV del portal utilizando el separador real
    de las fuentes y corrige problemas conocidos de codificación.
    """

    encodings = (
        "cp1252",
        "latin-1",
    )

    last_error = None

    for encoding in encodings:

        try:

            df = pd.read_csv(
                io.BytesIO(content),
                encoding=encoding,
                sep=";",
                low_memory=True,
            )

            return df

        except UnicodeDecodeError as exc:

            last_error = exc

    raise RuntimeError(
        "No fue posible decodificar el archivo CSV. "
        f"Último error: {last_error}"
    )


# ============================================================
# CARGA PÚBLICA
# ============================================================

def load_dataset(
    fuente: str = "cardiovascular",
) -> pd.DataFrame:
    """
    Carga una fuente desde CKAN.

    Devuelve una copia para evitar que las transformaciones
    posteriores modifiquen el caché interno.
    """

    fuente = str(fuente).lower().strip()

    if fuente not in RESOURCE_IDS:

        raise ValueError(
            f"Fuente no válida: {fuente}. "
            f"Opciones disponibles: "
            f"{', '.join(RESOURCE_IDS.keys())}"
        )

    if fuente in _CACHE:

        return _CACHE[fuente].copy()

    content = _download_resource(
        RESOURCE_IDS[fuente]
    )

    raw_df = _read_csv(content)

    if raw_df.empty:

        raise RuntimeError(
            f"La fuente '{fuente}' fue descargada "
            "pero no contiene registros."
        )

    _CACHE[fuente] = raw_df

    return raw_df.copy()


# ============================================================
# LIMPIEZA DE CACHÉ
# ============================================================

def clear_cache() -> None:
    """
    Vacía el caché de fuentes descargadas.
    """

    _CACHE.clear()