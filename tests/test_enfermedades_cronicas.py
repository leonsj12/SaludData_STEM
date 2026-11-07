"""Tests for the chronic-disease dataset naming and category preservation."""
from pathlib import Path

import pandas as pd

from app.services.explorer import DATASETS

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "mortalidad-prematura-por-enfermedades-cronicas-general.csv"


def test_chronic_dataset_is_the_canonical_runtime_identifier():
    assert "enfermedades_cronicas" in DATASETS
    assert "respiratorio" not in DATASETS
    assert DATASETS["enfermedades_cronicas"]["file"] == "enfermedades_cronicas.parquet"


def test_source_rows_and_all_chronic_categories_are_preserved():
    df = pd.read_csv(SOURCE, encoding="cp850", sep=";", low_memory=False)
    assert len(df) == 164_840
    counts = df["CIE10_AGRUPADA"].value_counts(dropna=False).to_dict()
    assert counts["Enfermedades Cardiocerebrovasculares"] == 74_560
    assert counts["Neoplasias"] == 69_886
    assert counts["Diabetes"] == 12_148
    assert counts["Enfermedades Crónicas Respiratorias Bajas"] == 8_024
    assert counts["Sin Información"] == 222
    assert sum(counts.values()) == len(df)


def test_source_file_name_is_preserved_in_dataset_metadata():
    import json
    metadata = json.loads((ROOT / "data" / "metadata" / "enfermedades_cronicas.json").read_text(encoding="utf-8"))
    assert metadata["dataset"] == "enfermedades_cronicas"
    assert metadata["archivo_original"] == "mortalidad-prematura-por-enfermedades-cronicas-general.csv"
    assert metadata["filas"] == 164_840
    assert len(metadata["categorias_CIE10_AGRUPADA"]) == 5


def test_dashboard_uses_valid_canonical_dataset_configuration():
    template = ROOT / "app" / "templates" / "dashboard.html"
    text = template.read_text(encoding="utf-8")
    assert 'data-dataset="enfermedades_cronicas"' in text
    assert "enfermedades_cronicas: {" in text
    assert "enfermedades_cronicas {" not in text
    assert 'title: "Enfermedades crónicas"' in text
