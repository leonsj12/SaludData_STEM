from flask import Blueprint, render_template, request

from app.services.data import load_dataset
from app.services.analysis import (
    prepare_health_data,
    monthly_trend,
    data_quality_summary,
    detect_anomalies_monthly,
    seasonality_summary,
    evaluate_forecast_models,
)

main_bp = Blueprint("main", __name__)

SOURCES = {
    "mortalidad": {
        "resource_id": "b12e3b26-2b37-4e6b-b819-3c890ce6394c",
        "label": "Mortalidad en Bogotá D.C.",
        "url": "https://datosabiertos.bogota.gov.co/dataset/mortalidad-en-bogota-d-c",
        "mode": "general",
    },
    "cardiovascular": {
        "resource_id": "f93bb5af-c4c6-4301-b602-4cbed283134a",
        "label": "Mortalidad prematura por enfermedad cardiocerebrovascular (30–70 años)",
        "url": "https://datosabiertos.bogota.gov.co/dataset/mortalidad-prematura-por-enfermedad-cardiocerebrovascular-en-bogota",
        "mode": "specific",
    },
    "respiratorio": {
        "resource_id": "f33d3941-9030-4899-9420-42ef8757607b",
        "label": "Mortalidad prematura por enfermedades crónicas respiratorias bajas (30–70 años)",
        "url": "https://datosabiertos.bogota.gov.co/dataset/mortalidad-prematura-por-enfermedades-cronicas-en-bogota",
        "mode": "specific",
    },
}


def _json(df):
    if df is None or df.empty:
        return "[]"
    return df.to_json(orient="records", date_format="iso", force_ascii=False)


def _dashboard_context(source_key):
    source = SOURCES[source_key]
    raw = load_dataset(source["resource_id"])
    df = prepare_health_data(raw, source["mode"])

    years = sorted(df["year"].dropna().astype(int).unique().tolist())
    sex_values = sorted(df["sex"].dropna().astype(str).unique().tolist()) if "sex" in df else []
    loc_values = sorted(df["locality"].dropna().astype(str).unique().tolist()) if "locality" in df else []
    return source, df, years, sex_values, loc_values


def _chart_data(df):
    monthly = monthly_trend(df)
    quality = data_quality_summary(df)
    anomalies = detect_anomalies_monthly(monthly)
    seasonality = seasonality_summary(monthly)
    models = evaluate_forecast_models(monthly)

    annual = (
        df.groupby("year", as_index=False)["value"].sum().sort_values("year")
        if not df.empty else df.iloc[0:0].copy()
    )

    sex = (
        df.groupby("sex", as_index=False)["value"].sum().sort_values("value", ascending=False)
        if "sex" in df else df.iloc[0:0].copy()
    )
    if not sex.empty:
        sex = sex.rename(columns={"sex": "category"})

    locality = (
        df.groupby("locality", as_index=False)["value"].sum().sort_values("value", ascending=False).head(10)
        if "locality" in df else df.iloc[0:0].copy()
    )
    if not locality.empty:
        locality = locality.rename(columns={"locality": "category"})

    # Forecast value from the last available monthly model, when possible.
    forecast_value = None
    if isinstance(models, dict):
        forecast_value = models.get("forecast")

    return monthly, anomalies, seasonality, models, quality, annual, sex, locality, forecast_value


@main_bp.get("/")
def index():
    return render_template("index.html", sources=SOURCES)


@main_bp.get("/dashboard")
def dashboard():
    source_key = request.args.get("fuente", "cardiovascular")
    if source_key not in SOURCES:
        source_key = "cardiovascular"

    try:
        source, df, years, sex_values, loc_values = _dashboard_context(source_key)

        year_from = request.args.get("desde", type=int)
        year_to = request.args.get("hasta", type=int)
        selected_sex = request.args.getlist("sexo")
        selected_loc = request.args.getlist("localidad")

        filtered = df.copy()
        if year_from is not None:
            filtered = filtered[filtered["year"] >= year_from]
        if year_to is not None:
            filtered = filtered[filtered["year"] <= year_to]
        if selected_sex:
            filtered = filtered[filtered["sex"].isin(selected_sex)]
        if selected_loc:
            filtered = filtered[filtered["locality"].isin(selected_loc)]

        (
            monthly,
            anomalies,
            seasonality,
            models,
            quality,
            annual,
            sex,
            locality,
            forecast_value,
        ) = _chart_data(filtered)

        partial_years = quality.get("partial_years", [])
        complete_years = quality.get("complete_years", [])

        # Summary indicators.
        peak_row = monthly.loc[monthly["value"].idxmax()] if not monthly.empty else None
        latest_row = monthly.iloc[-1] if not monthly.empty else None
        monthly_average = float(monthly["value"].mean()) if not monthly.empty else 0.0
        peak_value = float(peak_row["value"]) if peak_row is not None else 0.0
        peak_date = peak_row["date"].strftime("%B %Y") if peak_row is not None else "—"
        latest_value = float(latest_row["value"]) if latest_row is not None else 0.0
        latest_date = latest_row["date"].strftime("%B %Y") if latest_row is not None else "—"

        return render_template(
            "dashboard.html",
            source=source,
            source_key=source_key,
            sources=SOURCES,
            years=years,
            sex_values=sex_values,
            loc_values=loc_values,
            selected_sex=selected_sex,
            selected_loc=selected_loc,
            year_from=year_from,
            year_to=year_to,
            records=len(filtered),
            year_count=filtered["year"].nunique(),
            locality_count=filtered["locality"].nunique() if "locality" in filtered else 0,
            quality=quality,
            complete_years=complete_years,
            partial_years=partial_years,
            trend_json=_json(monthly),
            anomaly_json=_json(anomalies),
            seasonality_json=_json(seasonality),
            annual_json=_json(annual),
            sex_json=_json(sex),
            locality_json=_json(locality),
            models=models,
            model=models,
            forecast_value=forecast_value,
            monthly_average=monthly_average,
            peak_value=peak_value,
            peak_date=peak_date,
            latest_value=latest_value,
            latest_date=latest_date,
        )

    except Exception as exc:
        return render_template("error.html", error=str(exc)), 500
