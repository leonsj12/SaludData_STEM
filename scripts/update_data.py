"""
SALUDDATA STEM — Actualizador de datos oficiales.

============================================================
OBJETIVO PEDAGÓGICO
============================================================
Este script representa el proceso ETL:

    EXTRACT
       ↓
    TRANSFORM
       ↓
    LOAD

La aplicación web no debería depender de una descarga de Internet
cada vez que alguien abre el dashboard.

============================================================
EXTRACT
============================================================
Se solicitan los archivos publicados por la fuente oficial.

============================================================
TRANSFORM
============================================================
Se interpretan CSV, se normalizan columnas y se preparan los datos.

============================================================
LOAD
============================================================
Se guardan:

    data/raw/        copia local del archivo fuente
    data/processed/  Parquet optimizado

El archivo RAW sirve como referencia de reproducibilidad. El archivo
PROCESSED está pensado para ser consumido rápidamente por pandas.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

from app.services.data import prepare_health_data, read_csv_robust


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

# URLs oficiales de recursos de datos abiertos de Bogotá.
# Se mantienen centralizadas para facilitar futuras actualizaciones.
SOURCES = {
    "cardiovascular": "https://datosabiertos.bogota.gov.co/dataset/60772855-dc91-413d-bffa-ff08b054a29f/resource/f93bb5af-c4c6-4301-b602-4cbed283134a/download/",
    "respiratorio": "https://datosabiertos.bogota.gov.co/dataset/9fc1f14b-540b-4adc-93b1-ecd22780d6d2/resource/f33d3941-9030-4899-9420-42ef8757607b/download/mortalidad-prematura-por-enfermedades-cronicas-general.csv",
    "mortalidad": "https://datosabiertos.bogota.gov.co/dataset/60772855-dc91-413d-bffa-ff08b054a29f/resource/b12e3b26-2b37-4e6b-b819-3c890ce6394c/download/osb_demografia-causasmortalidadin.csv",
}


def download_bytes(url: str) -> bytes:
    """Descarga bytes y valida que la respuesta HTTP sea exitosa."""
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    return response.content


def update_one(name: str, url: str) -> dict:
    """
    Actualiza un dataset y genera un pequeño registro de metadatos.

    Los metadatos son una pieza importante de la ciencia reproducible:
    permiten saber qué fuente fue usada y cuándo se actualizó.
    """
    print(f"\n[1/3] Descargando: {name}")
    content = download_bytes(url)

    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)

    raw_path = RAW / f"{name}.csv"
    raw_path.write_bytes(content)

    print(f"[2/3] Transformando: {name}")
    df = prepare_health_data(read_csv_robust(content))

    parquet_path = PROCESSED / f"{name}.parquet"
    df.to_parquet(parquet_path, index=False)

    metadata = {
        "dataset": name,
        "source_url": url,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": [str(c) for c in df.columns],
    }

    metadata_path = PROCESSED / f"{name}.metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"[3/3] Guardado: {parquet_path}")
    return metadata


def main() -> None:
    """Ejecuta la actualización de todos los datasets configurados."""
    print("=" * 60)
    print("SALUDDATA STEM — ACTUALIZACIÓN DE DATOS")
    print("=" * 60)

    for name, url in SOURCES.items():
        try:
            update_one(name, url)
        except Exception as exc:
            # Una fuente que falle no debe ocultar el motivo del error.
            print(f"[ERROR] {name}: {exc}")

    print("\nProceso terminado.")
    print("Si hubo errores, revise la fuente indicada y vuelva a ejecutar.")


if __name__ == "__main__":
    main()
