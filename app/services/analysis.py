"""
SALUDDATA STEM — Motor de análisis exploratorio.

============================================================
PROPÓSITO
============================================================
Este módulo transforma datos tabulares en información que puede
visualizarse y discutirse.

No pretende diagnosticar enfermedades. Trabaja con indicadores
agregados y públicos para estudiar tendencias.

============================================================
RUTA PEDAGÓGICA
============================================================

DATOS
  ↓
CALIDAD
  ↓
AGREGACIÓN
  ↓
SERIE TEMPORAL
  ↓
CAMBIOS Y ANOMALÍAS
  ↓
INTERPRETACIÓN

============================================================
CONCEPTOS
============================================================
Una serie temporal es una colección de observaciones ordenadas por
tiempo. Al agrupar registros mensuales podemos estudiar cómo cambia
un indicador de un periodo al siguiente.

Una anomalía estadística no significa necesariamente un problema
médico. Significa que una observación se comporta de forma inusual
respecto de una referencia estadística.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.services.data import prepare_health_data


def monthly_trend(
    df: pd.DataFrame,
    value_column: str = "TOTAL MUERTES",
) -> pd.DataFrame:
    """
    Construye una serie mensual agregada.

    ¿QUÉ HACE?
        Agrupa registros por año y mes.

    ¿CÓMO?
        1. Prepara las columnas.
        2. Conserva filas con año y mes válidos.
        3. Suma el indicador.
        4. Ordena cronológicamente.
        5. Crea una fecha representativa del mes.

    ¿POR QUÉ?
        Un conjunto de registros individuales es difícil de observar
        directamente. La agregación permite estudiar la evolución
        temporal.

    ¿QUÉ APRENDEMOS?
        - groupby
        - sum
        - series temporales
        - ordenamiento
        - creación de fechas

    ADVERTENCIA:
        Una suma mensual describe el conjunto de registros disponible.
        No debe interpretarse como una tasa poblacional si no se dispone
        del denominador apropiado.
    """
    data = prepare_health_data(df)

    required = {"ANO", "MES", value_column}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {sorted(missing)}")

    clean = data.dropna(subset=["ANO", "MES", value_column]).copy()

    grouped = (
        clean.groupby(["ANO", "MES"], as_index=False)[value_column]
        .sum()
        .rename(columns={value_column: "valor"})
    )

    grouped["fecha"] = pd.to_datetime(
        {
            "year": grouped["ANO"].astype(int),
            "month": grouped["MES"].astype(int),
            "day": 1,
        },
        errors="coerce",
    )

    return grouped.sort_values("fecha").reset_index(drop=True)


def monthly_change(series: pd.Series) -> pd.Series:
    """
    Calcula el cambio porcentual respecto al mes anterior.

    Fórmula conceptual:

        cambio % = (valor_actual - valor_anterior) / valor_anterior × 100

    El primer mes no tiene un mes anterior y por ello queda como NaN.

    PEDAGOGÍA:
    El cambio porcentual permite comparar variaciones relativas,
    pero puede ser inestable cuando el valor anterior es muy pequeño.
    """
    previous = series.shift(1)

    with np.errstate(divide="ignore", invalid="ignore"):
        change = (series - previous) / previous * 100

    return change.replace([np.inf, -np.inf], np.nan)


def zscore_anomalies(
    series: pd.Series,
    threshold: float = 2.0,
) -> pd.DataFrame:
    """
    Identifica observaciones inusuales usando un z-score.

    z = (x - media) / desviación estándar

    Un valor absoluto cercano a 2 indica una observación relativamente
    alejada de la media bajo esta regla heurística.

    IMPORTANTE:
    Este método es exploratorio. No demuestra causalidad ni implica
    significación clínica.
    """
    values = pd.to_numeric(series, errors="coerce")
    mean = values.mean()
    std = values.std()

    result = pd.DataFrame({"valor": values})

    if pd.isna(std) or std == 0:
        result["zscore"] = 0.0
        result["anomalia"] = False
        return result

    result["zscore"] = (values - mean) / std
    result["anomalia"] = result["zscore"].abs() >= threshold
    return result


def build_health_summary(data: dict[str, pd.DataFrame]) -> dict:
    """
    Construye un resumen pequeño para el dashboard.

    Mantener este resultado compacto reduce el trabajo del navegador y
    evita enviar grandes tablas mediante la API.
    """
    summary = {
        "datasets": [],
        "notes": [
            "Los resultados son exploratorios y educativos.",
            "Las alertas estadísticas no son diagnósticos.",
        ],
    }

    for name, df in data.items():
        item = {
            "dataset": name,
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
        }

        if "ANO" in df.columns:
            years = pd.to_numeric(df["ANO"], errors="coerce").dropna()
            if not years.empty:
                item["min_year"] = int(years.min())
                item["max_year"] = int(years.max())

        summary["datasets"].append(item)

    return summary
