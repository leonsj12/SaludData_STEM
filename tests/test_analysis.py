"""
Pruebas educativas del motor de análisis.

PEDAGOGÍA:
Una prueba automatizada verifica que una función produzca el resultado
esperado. Esto permite detectar regresiones cuando el proyecto crece.
"""

import pandas as pd

from app.services.analysis import monthly_change, monthly_trend, zscore_anomalies


def test_monthly_trend():
    df = pd.DataFrame({
        "ANO": [2025, 2025, 2025],
        "MES": [1, 1, 2],
        "TOTAL MUERTES": [10, 5, 20],
    })

    result = monthly_trend(df)

    assert len(result) == 2
    assert result.loc[0, "valor"] == 15
    assert result.loc[1, "valor"] == 20


def test_monthly_change():
    result = monthly_change(pd.Series([100, 110]))
    assert pd.isna(result.iloc[0])
    assert round(result.iloc[1], 2) == 10.0


def test_zscore_anomalies():
    result = zscore_anomalies(pd.Series([10, 10, 10, 30]))
    assert result["anomalia"].any()
