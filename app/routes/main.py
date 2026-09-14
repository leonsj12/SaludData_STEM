from __future__ import annotations

from flask import Blueprint, render_template, request
import pandas as pd

from app.services.data import load_dataset
from app.services.analysis import (
    prepare_health_data,
    trend_table,
    monthly_trend,
    data_quality_summary,
    detect_anomalies,
    detect_anomalies_monthly,
    seasonality_summary,
    evaluate_forecast_models,
    format_month_es,
)


main_bp = Blueprint("main", __name__)


# =====================================================================
# FUENTES
# =====================================================================

SOURCES = {
    "mortalidad": {
        "resource_id": "b12e3b26-2b37-4e6b-b819-3c890ce6394c",
        "label": "Mortalidad en Bogotá D.C.",
        "url": (
            "https://datosabiertos.bogota.gov.co/"
            "dataset/mortalidad-en-bogota-d-c"
        ),
        "mode": "general",
    },

    "cardiovascular": {
        "resource_id": "f93bb5af-c4c6-4301-b602-4cbed283134a",
        "label": (
            "Mortalidad prematura por enfermedad "
            "cardiocerebrovascular (30–70 años)"
        ),
        "url": (
            "https://datosabiertos.bogota.gov.co/"
            "dataset/mortalidad-prematura-por-enfermedad-"
            "cardiocerebrovascular-en-bogota"
        ),
        "mode": "specific",
    },

    "respiratoria": {
        "resource_id": "f33d3941-9030-4899-9420-42ef8757607b",
        "label": (
            "Mortalidad prematura por enfermedades "
            "crónicas respiratorias bajas (30–70 años)"
        ),
        "url": (
            "https://datosabiertos.bogota.gov.co/"
            "dataset/mortalidad-prematura-por-enfermedades-cronicas-en-bogota"
        ),
        "mode": "specific",
    },
}


# =====================================================================
# UTILIDADES
# =====================================================================

def _json(df, date_format="iso"):
    """
    Convierte un DataFrame a JSON para los gráficos.

    Devuelve una lista vacía cuando no existen datos.
    """

    if df is None or df.empty:
        return "[]"

    return df.to_json(
        orient="records",
        date_format=date_format,
        force_ascii=False,
    )


def _categorical_options(df, column):
    """
    Obtiene opciones únicas de una variable categórica.
    """

    if df is None or df.empty:
        return []

    if column not in df.columns:
        return []

    values = (
        df[column]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    return sorted(
        values,
        key=lambda value: value.lower(),
    )


def _year_options(df):
    """
    Obtiene los años disponibles en una fuente.
    """

    if df is None or df.empty:
        return []

    if "year" not in df.columns:
        return []

    return sorted(
        df["year"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )


def _temporal_completeness(monthly, annual):
    """
    Determina años completos y parciales.

    Para series mensuales:
        12 meses calendario observados = año completo.

    Para series anuales:
        cada año observado se considera completo porque
        no existe una dimensión mensual que permita
        determinar parcialidad.
    """

    complete_years = []
    partial_years = []

    # -------------------------------------------------------------
    # SERIES MENSUALES
    # -------------------------------------------------------------

    if monthly is not None and not monthly.empty:

        if "date" not in monthly.columns:
            return complete_years, partial_years

        dates = pd.to_datetime(
            monthly["date"],
            errors="coerce",
        ).dropna()

        if dates.empty:
            return complete_years, partial_years

        monthly_periods = (
            dates
            .dt.to_period("M")
            .drop_duplicates()
        )

        if monthly_periods.empty:
            return complete_years, partial_years

        months_by_year = (
            pd.Series(
                1,
                index=monthly_periods,
            )
            .groupby(
                lambda period: period.year
            )
            .sum()
        )

        for year, month_count in months_by_year.items():

            year = int(year)
            month_count = int(month_count)

            if month_count == 12:
                complete_years.append(year)

            elif month_count > 0:
                partial_years.append(year)

    # -------------------------------------------------------------
    # SERIES ANUALES
    # -------------------------------------------------------------

    elif annual is not None and not annual.empty:

        if "year" in annual.columns:

            complete_years = (
                annual["year"]
                .dropna()
                .astype(int)
                .unique()
                .tolist()
            )

    return (
        sorted(set(complete_years)),
        sorted(set(partial_years)),
    )


def _calculate_latest_delta(series):
    """
    Calcula la variación porcentual entre los dos últimos
    periodos observados.

    No calcula variación si el periodo anterior es cero.
    """

    if series is None or len(series) < 2:
        return None

    latest_value = float(
        series.iloc[-1]["value"]
    )

    previous_value = float(
        series.iloc[-2]["value"]
    )

    if previous_value == 0:
        return None

    return (
        (latest_value - previous_value)
        / previous_value
        * 100
    )


def _empty_aggregation(columns):
    """
    Crea un DataFrame vacío con columnas conocidas.
    """

    return pd.DataFrame(
        columns=columns
    )


def _build_filter_state(
    year_from,
    year_to,
    selected_sex,
    selected_loc,
):
    """
    Construye el estado metodológico de los filtros.

    Permite informar al usuario que los indicadores y modelos
    corresponden al subconjunto actualmente seleccionado.
    """

    filters_active = any(
        [
            year_from is not None,
            year_to is not None,
            bool(selected_sex),
            bool(selected_loc),
        ]
    )

    if not filters_active:
        return {
            "active": False,
            "summary": (
                "Los indicadores y análisis se calculan "
                "sobre el conjunto de datos disponible "
                "para la fuente seleccionada."
            ),
        }

    parts = []

    if year_from is not None and year_to is not None:
        parts.append(
            f"años {year_from}–{year_to}"
        )

    elif year_from is not None:
        parts.append(
            f"desde {year_from}"
        )

    elif year_to is not None:
        parts.append(
            f"hasta {year_to}"
        )

    if selected_sex:
        parts.append(
            "sexo: " + ", ".join(selected_sex)
        )

    if selected_loc:
        parts.append(
            "localidad: " + ", ".join(selected_loc)
        )

    filter_description = "; ".join(parts)

    return {
        "active": True,
        "summary": (
            "Los indicadores, series temporales, "
            "análisis estadísticos y modelos corresponden "
            "al subconjunto definido por los filtros "
            f"seleccionados ({filter_description})."
        ),
    }


# =====================================================================
# CONTEXTO DEL DATASET
# =====================================================================

def _dashboard_context(source_key):
    """
    Carga y prepara una fuente.

    La descarga pertenece a data.py.
    La transformación pertenece a analysis.py.
    """

    source = SOURCES[source_key]

    raw = load_dataset(source_key)

    df = prepare_health_data(
        raw,
        source["mode"],
    )

    return source, df


# =====================================================================
# INICIO
# =====================================================================

@main_bp.get("/")
def index():
    return render_template(
        "index.html",
        sources=SOURCES,
    )


# =====================================================================
# DASHBOARD
# =====================================================================

@main_bp.get("/dashboard")
def dashboard():

    # -------------------------------------------------------------
    # FUENTE
    # -------------------------------------------------------------

    source_key = request.args.get(
        "fuente",
        "cardiovascular",
    )

    if source_key not in SOURCES:
        source_key = "cardiovascular"

    try:

        source, df = _dashboard_context(
            source_key
        )

        # ---------------------------------------------------------
        # FILTROS RECIBIDOS
        # ---------------------------------------------------------

        year_from = request.args.get(
            "desde",
            type=int,
        )

        year_to = request.args.get(
            "hasta",
            type=int,
        )

        selected_sex = request.args.getlist(
            "sexo"
        )

        selected_loc = request.args.getlist(
            "localidad"
        )

        # ---------------------------------------------------------
        # ESTADO METODOLÓGICO DE LOS FILTROS
        # ---------------------------------------------------------

        filter_state = _build_filter_state(
            year_from=year_from,
            year_to=year_to,
            selected_sex=selected_sex,
            selected_loc=selected_loc,
        )

        # ---------------------------------------------------------
        # OPCIONES GENERALES DE LA FUENTE
        # ---------------------------------------------------------

        all_years = _year_options(df)

        sex_values = _categorical_options(
            df,
            "sex",
        )

        loc_values = _categorical_options(
            df,
            "locality",
        )

        # ---------------------------------------------------------
        # FILTRADO
        # ---------------------------------------------------------

        filtered = df.copy()

        if year_from is not None:
            filtered = filtered[
                filtered["year"] >= year_from
            ]

        if year_to is not None:
            filtered = filtered[
                filtered["year"] <= year_to
            ]

        if selected_sex and "sex" in filtered.columns:
            filtered = filtered[
                filtered["sex"]
                .astype(str)
                .isin(selected_sex)
            ]

        if selected_loc and "locality" in filtered.columns:
            filtered = filtered[
                filtered["locality"]
                .astype(str)
                .isin(selected_loc)
            ]

        # ---------------------------------------------------------
        # CALIDAD
        # ---------------------------------------------------------

        quality = data_quality_summary(
            filtered
        )

        # ---------------------------------------------------------
        # SERIES TEMPORALES
        # ---------------------------------------------------------

        annual = trend_table(
            filtered
        )

        # Las fuentes específicas contienen año y mes.
        # La mortalidad general es una fuente anual y no
        # debe forzarse a una estructura mensual.
        is_monthly = (
            "month" in filtered.columns
            and filtered["month"].notna().any()
        )

        if is_monthly:
            monthly = monthly_trend(
                filtered
            )
        else:
            monthly = pd.DataFrame()

        # ---------------------------------------------------------
        # COBERTURA TEMPORAL
        # ---------------------------------------------------------

        complete_years, partial_years = (
            _temporal_completeness(
                monthly,
                annual,
            )
        )

        # ---------------------------------------------------------
        # ANÁLISIS
        # ---------------------------------------------------------

        if is_monthly:

            anomalies = detect_anomalies_monthly(
                monthly
            )

            seasonality = seasonality_summary(
                monthly
            )

            series_for_model = monthly

        else:

            anomalies = detect_anomalies(
                annual
            )

            seasonality = pd.DataFrame()

            series_for_model = annual

        # ---------------------------------------------------------
        # MODELOS
        # ---------------------------------------------------------

        if (
            series_for_model is not None
            and not series_for_model.empty
        ):

            models = evaluate_forecast_models(
                series_for_model
            )

        else:

            models = {}

        # ---------------------------------------------------------
        # KPI PRINCIPALES
        # ---------------------------------------------------------

        if is_monthly:

            series = monthly

            peak = (
                series.loc[
                    series["value"].idxmax()
                ]
                if not series.empty
                else None
            )

            latest = (
                series.iloc[-1]
                if not series.empty
                else None
            )

            avg_value = (
                float(
                    series["value"].mean()
                )
                if not series.empty
                else 0.0
            )

            peak_value = (
                float(peak["value"])
                if peak is not None
                else 0.0
            )

            peak_label = (
                format_month_es(
                    peak["date"]
                )
                if peak is not None
                else "—"
            )

            latest_value = (
                float(latest["value"])
                if latest is not None
                else 0.0
            )

            latest_label = (
                format_month_es(
                    latest["date"]
                )
                if latest is not None
                else "—"
            )

            latest_delta = (
                _calculate_latest_delta(
                    series
                )
            )

            granularity = "monthly"
            granularity_label = "mensual"

        else:

            series = annual

            peak = (
                series.loc[
                    series["value"].idxmax()
                ]
                if not series.empty
                else None
            )

            latest = (
                series.iloc[-1]
                if not series.empty
                else None
            )

            avg_value = (
                float(
                    series["value"].mean()
                )
                if not series.empty
                else 0.0
            )

            peak_value = (
                float(peak["value"])
                if peak is not None
                else 0.0
            )

            peak_label = (
                str(
                    int(peak["year"])
                )
                if peak is not None
                else "—"
            )

            latest_value = (
                float(latest["value"])
                if latest is not None
                else 0.0
            )

            latest_label = (
                str(
                    int(latest["year"])
                )
                if latest is not None
                else "—"
            )

            latest_delta = (
                _calculate_latest_delta(
                    series
                )
            )

            granularity = "annual"
            granularity_label = "anual"

        # ---------------------------------------------------------
        # AGREGACIÓN POR SEXO
        # ---------------------------------------------------------

        if (
            "sex" in filtered.columns
            and not filtered.empty
        ):

            sex_df = (
                filtered
                .groupby(
                    "sex",
                    as_index=False,
                )["value"]
                .sum()
                .sort_values(
                    "value",
                    ascending=False,
                )
            )

        else:

            sex_df = _empty_aggregation(
                ["sex", "value"]
            )

        # ---------------------------------------------------------
        # AGREGACIÓN POR LOCALIDAD
        # ---------------------------------------------------------

        if (
            "locality" in filtered.columns
            and not filtered.empty
        ):

            loc_df = (
                filtered
                .groupby(
                    "locality",
                    as_index=False,
                )["value"]
                .sum()
                .sort_values(
                    "value",
                    ascending=False,
                )
                .head(10)
            )

        else:

            loc_df = _empty_aggregation(
                ["locality", "value"]
            )

        # ---------------------------------------------------------
        # AGREGACIÓN POR EDAD
        # ---------------------------------------------------------

        if (
            "age_group" in filtered.columns
            and not filtered.empty
        ):

            age_df = (
                filtered
                .groupby(
                    "age_group",
                    as_index=False,
                )["value"]
                .sum()
                .sort_values(
                    "value",
                    ascending=False,
                )
                .head(15)
            )

        else:

            age_df = _empty_aggregation(
                ["age_group", "value"]
            )

        # ---------------------------------------------------------
        # DATOS PARA GRÁFICOS
        # ---------------------------------------------------------

        trend_for_chart = (
            monthly
            if is_monthly
            else annual
        )

        # ---------------------------------------------------------
        # COBERTURA OBSERVADA
        # ---------------------------------------------------------

        observed_period = "—"

        filtered_years = _year_options(
            filtered
        )

        if filtered_years:
            observed_period = (
                f"{filtered_years[0]}–"
                f"{filtered_years[-1]}"
            )

        observed_months = (
            len(monthly)
            if is_monthly
            else 0
        )

        # ---------------------------------------------------------
        # RESPUESTA
        # ---------------------------------------------------------

        return render_template(

            "dashboard.html",

            # Fuente
            source=source,
            source_key=source_key,
            sources=SOURCES,

            # Opciones
            years=all_years,
            all_years=all_years,
            sex_values=sex_values,
            loc_values=loc_values,

            # Estado de filtros
            selected_sex=selected_sex,
            selected_loc=selected_loc,
            year_from=year_from,
            year_to=year_to,

            # Estado metodológico de filtros
            filters_active=filter_state["active"],
            filter_summary=filter_state["summary"],

            # Registros
            records=len(filtered),

            year_count=(
                filtered["year"].nunique()
                if "year" in filtered.columns
                else 0
            ),

            locality_count=(
                filtered["locality"].nunique()
                if "locality" in filtered.columns
                else 0
            ),

            # Cobertura observada
            observed_period=observed_period,
            observed_months=observed_months,

            # Calidad
            quality=quality,

            # Cobertura
            complete_years=complete_years,
            partial_years=partial_years,

            # Granularidad
            granularity=granularity,
            granularity_label=granularity_label,

            # Series
            trend_json=_json(
                trend_for_chart
            ),

            annual_json=_json(
                annual
            ),

            anomaly_json=_json(
                anomalies
            ),

            seasonality_json=_json(
                seasonality
            ),

            # Distribuciones
            sex_json=_json(
                sex_df,
                date_format=None,
            ),

            locality_json=_json(
                loc_df,
                date_format=None,
            ),

            age_json=_json(
                age_df,
                date_format=None,
            ),

            # Modelos
            models=models,
            model=models,

            # KPI
            avg_value=avg_value,
            peak_value=peak_value,
            peak_label=peak_label,

            latest_value=latest_value,
            latest_label=latest_label,
            latest_delta=latest_delta,

            selected_period_count=(
                len(
                    _year_options(
                        filtered
                    )
                )
            ),
        )

    except Exception as exc:

        return render_template(
            "error.html",
            error=str(exc),
        ), 500