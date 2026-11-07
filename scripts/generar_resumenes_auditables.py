"""Generate auditable JSON summaries from the preserved raw CSV sources.

For monthly datasets, the rolling z-score uses a trailing 12-observation
window INCLUDING the observation being assessed (ddof=0), matching the
current stored analytics snapshots. Because the focal observation is part
of its own reference window, this is descriptive/exploratory and should not
be interpreted as a prospective alerting method.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ANALYTICS = DATA / "analytics"

SOURCES = {
    "cardiovascular": {
        "file": "osb_cronicas_mpcardiocerebrovasculares.csv",
        "encoding": "cp850",
        "frequency": "monthly",
        "value_mode": "records",
    },
    "enfermedades_cronicas": {
        "file": "mortalidad-prematura-por-enfermedades-cronicas-general.csv",
        "encoding": "cp850",
        "frequency": "monthly",
        "value_mode": "records",
    },
    "mortalidad": {
        "file": "osb_demografia-causasmortalidadin.csv",
        "encoding": "utf-8-sig",
        "frequency": "annual",
        "value_mode": "deaths",
    },
}


def load_source(name: str, config: dict) -> pd.DataFrame:
    path = DATA / config["file"]
    df = pd.read_csv(path, encoding=config["encoding"], sep=";", low_memory=False)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def rolling_zscore_anomalies(series: pd.Series, window: int, threshold: float = 2.0) -> list[dict]:
    """Reproduce the stored rolling z-score summaries, with current month in window."""
    values = pd.to_numeric(series, errors="coerce")
    mean = values.rolling(window=window, min_periods=window).mean()
    std = values.rolling(window=window, min_periods=window).std(ddof=0)
    z = (values - mean) / std.replace(0, pd.NA)
    flagged = z.abs() >= threshold
    out = []
    for idx in values.index[flagged.fillna(False)]:
        out.append({
            "period": str(idx),
            "value": int(values.loc[idx]),
            "z_score": float(z.loc[idx]),
            "direction": "above_reference" if z.loc[idx] > 0 else "below_reference",
        })
    return out


def summarize(name: str, config: dict) -> dict:
    df = load_source(name, config)
    result = {
        "dataset": name,
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "missing_values_total": int(df.isna().sum().sum()),
        "exact_duplicate_rows_flagged": int(df.duplicated().sum()),
        "duplicate_rows_removed": 0,
        "frequency": config["frequency"],
        "source_file": config["file"],
    }
    if config["frequency"] == "monthly":
        year = pd.to_numeric(df["ANO"], errors="coerce")
        month = pd.to_numeric(df["MES"], errors="coerce")
        periods = pd.DataFrame({"year": year, "month": month}).dropna().drop_duplicates()
        series = (
            pd.DataFrame({"year": year, "month": month})
            .dropna()
            .groupby(["year", "month"])
            .size()
            .sort_index()
        )
        series.index = [f"{int(y):04d}-{int(m):02d}" for y,m in series.index]
        result["periods"] = int(len(periods))
        result["first_period"] = str(series.index[0]) if len(series) else None
        result["last_period"] = str(series.index[-1]) if len(series) else None
        result["rolling_zscore"] = {
            "window": 12,
            "threshold": 2.0,
            "ddof": 0,
            "includes_focal_observation": True,
            "anomalies": rolling_zscore_anomalies(series, window=12, threshold=2.0),
        }
    else:
        year_col = "ANO" if "ANO" in df.columns else "\ufeffANO"
        year = pd.to_numeric(df[year_col], errors="coerce")
        deaths = pd.to_numeric(df["TOTAL MUERTES"], errors="coerce").fillna(0)
        series = pd.DataFrame({"year": year, "value": deaths}).dropna().groupby("year")["value"].sum().sort_index()
        result["periods"] = int(series.size)
        result["first_period"] = int(series.index.min()) if series.size else None
        result["last_period"] = int(series.index.max()) if series.size else None
        result["rolling_zscore"] = {
            "window": 5,
            "threshold": 2.0,
            "ddof": 0,
            "includes_focal_observation": True,
            "anomalies": rolling_zscore_anomalies(series, window=5, threshold=2.0),
        }
    if name == "enfermedades_cronicas":
        counts = df["CIE10_AGRUPADA"].value_counts(dropna=False)
        result["main_category_column"] = "CIE10_AGRUPADA"
        result["category_counts"] = {str(k): int(v) for k,v in counts.items()}
        result["category_percentages"] = {str(k): round(float(v)/len(df)*100, 4) for k,v in counts.items()}
        result["dataset_name_decision"] = "enfermedades_cronicas"
        result["display_name"] = "Enfermedades crónicas"
        result["source_catalogue_title"] = (
            "Mortalidad prematura por enfermedades crónicas RESPIRATORIAS BAJAS "
            "en Bogotá D.C. (30 a 70 años)"
        )
        result["source_catalogue_page"] = (
            "https://datosabiertos.bogota.gov.co/dataset/"
            "mortalidad-prematura-por-enfermedades-cronicas-en-bogota"
        )
        result["source_resource_url"] = (
            "https://datosabiertos.bogota.gov.co/dataset/"
            "9fc1f14b-540b-4adc-93b1-ecd22780d6d2/resource/"
            "f33d3941-9030-4899-9420-42ef8757607b/download/"
            "mortalidad-prematura-por-enfermedades-cronicas-general.csv"
        )
        result["source_age_range_catalogue"] = "30 a 70 años"
        result["note"] = (
            "The catalogue title and downloadable CSV category distribution are not fully aligned. "
            "The project keeps the original title and filename for provenance, uses Chronic diseases "
            "as the internal label, and retains all rows and categories."
        )
    return result


def main() -> None:
    ANALYTICS.mkdir(parents=True, exist_ok=True)
    combined = {"project": "SaludData STEM", "datasets": {}}
    for name, config in SOURCES.items():
        summary = summarize(name, config)
        (ANALYTICS / f"{name}_resumen.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        combined["datasets"][name] = {
            "rows": summary["rows"],
            "columns": summary["columns"],
            "frequency": summary["frequency"],
            "periods": summary["periods"],
            "anomalies": len(summary["rolling_zscore"]["anomalies"]),
        }
        print(f"{name}: {summary['rows']:,} rows; {summary['periods']} periods; {len(summary['rolling_zscore']['anomalies'])} exploratory deviations")
    (ANALYTICS / "resumen.json").write_text(
        json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
