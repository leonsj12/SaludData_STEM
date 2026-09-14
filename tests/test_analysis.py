import pandas as pd
from app.services.analysis import trend_table, detect_anomalies


def test_trend_table():
    df = pd.DataFrame({"year": [2020, 2020, 2021], "value": [3, 2, 4]})
    out = trend_table(df)
    assert out.to_dict("records") == [{"year": 2020, "value": 5}, {"year": 2021, "value": 4}]


def test_anomaly_has_expected_columns():
    df = pd.DataFrame({"year": range(2015, 2025), "value": [10, 11, 9, 10, 11, 10, 12, 50, 11, 10]})
    out = detect_anomalies(df)
    assert "anomaly" in out.columns
