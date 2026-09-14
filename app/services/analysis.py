from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# CONFIGURACIÓN
# ============================================================

MONTH_NAMES_ES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}


LOCALITY_CODES = {
    "00": "Bogotá",
    "01": "Usaquén",
    "02": "Chapinero",
    "03": "Santa Fe",
    "04": "San Cristóbal",
    "05": "Usme",
    "06": "Tunjuelito",
    "07": "Bosa",
    "08": "Kennedy",
    "09": "Fontibón",
    "10": "Engativá",
    "11": "Suba",
    "12": "Barrios Unidos",
    "13": "Teusaquillo",
    "14": "Los Mártires",
    "15": "Antonio Nariño",
    "16": "Puente Aranda",
    "17": "La Candelaria",
    "18": "Rafael Uribe Uribe",
    "19": "Ciudad Bolívar",
    "20": "Sumapaz",
    "99": "Sin Información",
}


MOJIBAKE_REPLACEMENTS = {
    "a¤os": "años",
    "aÃ±os": "años",
    "año": "año",
    "Usaqu‚n": "Usaquén",
    "UsaquÃ©n": "Usaquén",
    "San Crist¢bal": "San Cristóbal",
    "San CristÃ³bal": "San Cristóbal",
    "Engativ ": "Engativá",
    "EngativÃ¡": "Engativá",
    "M rtires": "Mártires",
    "MÃ¡rtires": "Mártires",
    "Los M rtires": "Los Mártires",
    "Los MÃ¡rtires": "Los Mártires",
    "Ciudad Bol var": "Ciudad Bolívar",
    "Ciudad BolÃ­var": "Ciudad Bolívar",
    "Ciudad Bolávar": "Ciudad Bolívar",
    "Ciudad Bol¡var": "Ciudad Bolívar",
    "INFORMACIàN": "INFORMACIÓN",
    "INFORMACIÃ“N": "INFORMACIÓN",
    "SIN INFORMACIàN": "SIN INFORMACIÓN",
    "SIN INFORMACIÃ“N": "SIN INFORMACIÓN",
    "00 - Bogot": "00 - Bogotá",
    "00 - BogotÃ¡": "00 - Bogotá",
    "15 - Antonio Nari¤o": "15 - Antonio Nariño",
    "15 - Antonio NariÃ±o": "15 - Antonio Nariño",
    "99 - Sin Informaci¢n": "99 - Sin Información",
    "99 - Sin InformaciÃ³n": "99 - Sin Información",
}


# ============================================================
# UTILIDADES DE TEXTO
# ============================================================

def _clean_text(value: Any) -> Any:
    """
    Limpia valores textuales sin convertir valores nulos
    en cadenas artificiales.
    """
    if pd.isna(value):
        return value

    text = str(value).strip()

    if not text:
        return np.nan

    return text


def _repair_text_encoding(value: Any) -> Any:
    """
    Corrige errores conocidos de codificación presentes
    en los archivos oficiales descargados.
    """
    value = _clean_text(value)

    if pd.isna(value):
        return value

    text = str(value)

    for bad, good in MOJIBAKE_REPLACEMENTS.items():
        text = text.replace(bad, good)

    return text.strip()


def _normalize_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza columnas de texto sin alterar columnas numéricas.
    """
    result = df.copy()

    text_columns = result.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:
        result[column] = result[column].map(
            _repair_text_encoding
        )

    return result


# ============================================================
# LOCALIDADES
# ============================================================

def _normalize_locality(value: Any) -> Any:
    """
    Normaliza localidades utilizando principalmente su código
    de dos dígitos. Esto evita depender de textos dañados por
    problemas de codificación.
    """
    if pd.isna(value):
        return np.nan

    text = str(value).strip()

    if not text:
        return np.nan

    # Extraer código inicial: "01 - Usaquén"
    code = text[:2]

    if code.isdigit() and code in LOCALITY_CODES:
        return LOCALITY_CODES[code]

    # Casos donde solamente llega el nombre
    repaired = _repair_text_encoding(text)

    if pd.isna(repaired):
        return np.nan

    repaired = str(repaired).strip()

    aliases = {
        "Usaqu‚n": "Usaquén",
        "Usaquén": "Usaquén",
        "Usaquen": "Usaquén",
        "San Crist¢bal": "San Cristóbal",
        "San Cristobal": "San Cristóbal",
        "Engativ": "Engativá",
        "Engativá": "Engativá",
        "Los Martires": "Los Mártires",
        "Los Mártires": "Los Mártires",
        "Ciudad Bolivar": "Ciudad Bolívar",
        "Ciudad Bolívar": "Ciudad Bolívar",
        "Antonio Narino": "Antonio Nariño",
        "Antonio Nariño": "Antonio Nariño",
        "Bogota": "Bogotá",
        "Bogotá": "Bogotá",
        "Sin Información": "Sin Información",
    }

    return aliases.get(repaired, repaired)


# ============================================================
# FECHAS
# ============================================================

def _safe_numeric(series: pd.Series) -> pd.Series:
    """
    Conversión numérica robusta.
    """
    return pd.to_numeric(
        series.astype(str).str.strip(),
        errors="coerce",
    )


def _build_month_date(
    year: pd.Series,
    month: pd.Series,
) -> pd.Series:
    """
    Construye fechas mensuales de forma segura.

    Nunca interpreta números como timestamps Unix.
    """
    year_numeric = _safe_numeric(year)
    month_numeric = _safe_numeric(month)

    valid = (
        year_numeric.between(1900, 2100)
        & month_numeric.between(1, 12)
    )

    result = pd.Series(
        pd.NaT,
        index=year.index,
        dtype="datetime64[ns]",
    )

    if valid.any():
        result.loc[valid] = pd.to_datetime(
            {
                "year": year_numeric.loc[valid].astype(int),
                "month": month_numeric.loc[valid].astype(int),
                "day": 1,
            },
            errors="coerce",
        )

    return result


# ============================================================
# PREPARACIÓN PRINCIPAL
# ============================================================

def prepare_health_data(
    df: pd.DataFrame,
    mode: str = "specific",
) -> pd.DataFrame:
    """
    Normaliza los conjuntos de mortalidad utilizados por
    SaludData STEM.

    mode:
        specific -> conjuntos cardiovasculares/respiratorios
        general  -> mortalidad general
    """

    if df is None or df.empty:
        return pd.DataFrame()

    result = df.copy()

    result = _normalize_text_columns(result)

    # --------------------------------------------------------
    # NORMALIZAR NOMBRES DE COLUMNAS
    # --------------------------------------------------------

    result.columns = [
        str(column).strip()
        for column in result.columns
    ]

    # --------------------------------------------------------
    # MODO ESPECÍFICO
    # --------------------------------------------------------

    if mode == "specific":

        mapping = {
            "ANO": "year",
            "AÑO": "year",
            "ï»¿ANO": "year",
            "\ufeffANO": "year",
            "MES": "month",
            "SEXO": "sex",
            "EDAD_QUINQUENAL": "age_group",
            "EDAD_FALLECIDO": "age",
            "LOCALIDAD": "locality",
            "CIE10_AGRUPADA": "cause_group",
            "CIE10_BASICA": "cause",
        }

        rename_map = {
            source: target
            for source, target in mapping.items()
            if source in result.columns
        }

        result = result.rename(columns=rename_map)

        required = [
            "year",
            "month",
        ]

        for column in required:
            if column not in result.columns:
                result[column] = np.nan

        result["year"] = _safe_numeric(
            result["year"]
        )

        result["month"] = _safe_numeric(
            result["month"]
        )

        # Cada registro representa una defunción.
        result["value"] = 1.0

        if "sex" in result.columns:
            result["sex"] = result["sex"].map(
                _repair_text_encoding
            )

        if "locality" in result.columns:
            result["locality"] = result["locality"].map(
                _normalize_locality
            )

        if "age_group" in result.columns:
            result["age_group"] = result["age_group"].map(
                _repair_text_encoding
            )

        if "cause_group" in result.columns:
            result["cause_group"] = result["cause_group"].map(
                _repair_text_encoding
            )

        if "cause" in result.columns:
            result["cause"] = result["cause"].map(
                _repair_text_encoding
            )

        result["date"] = _build_month_date(
            result["year"],
            result["month"],
        )

    # --------------------------------------------------------
    # MODO GENERAL
    # --------------------------------------------------------

    else:

        mapping = {
            "ANO": "year",
            "AÑO": "year",
            "ï»¿ANO": "year",
            "\ufeffANO": "year",
            "SEXO": "sex",
            "GRUPO DE EDAD": "age_group",
            "LOCALIDAD": "locality",
            "TOTAL MUERTES": "value",
            "DESCRIPCION LISTA 105": "cause",
        }

        rename_map = {
            source: target
            for source, target in mapping.items()
            if source in result.columns
        }

        result = result.rename(columns=rename_map)

        if "year" not in result.columns:
            result["year"] = np.nan

        result["year"] = _safe_numeric(
            result["year"]
        )

        if "value" not in result.columns:
            result["value"] = 1.0
        else:
            result["value"] = _safe_numeric(
                result["value"]
            )

        if "sex" in result.columns:
            result["sex"] = result["sex"].map(
                _repair_text_encoding
            )

        if "locality" in result.columns:
            result["locality"] = result["locality"].map(
                _normalize_locality
            )

        if "age_group" in result.columns:
            result["age_group"] = result["age_group"].map(
                _repair_text_encoding
            )

        if "cause" in result.columns:
            result["cause"] = result["cause"].map(
                _repair_text_encoding
            )

        # Algunos conjuntos generales no poseen MES.
        # No se fuerza una fecha mensual inexistente.
        if "month" in result.columns:

            result["month"] = _safe_numeric(
                result["month"]
            )

            result["date"] = _build_month_date(
                result["year"],
                result["month"],
            )

        else:

            result["date"] = pd.to_datetime(
                result["year"].astype("Int64").astype(str)
                + "-01-01",
                errors="coerce",
            )

    # --------------------------------------------------------
    # LIMPIEZA FINAL
    # --------------------------------------------------------

    result["year"] = _safe_numeric(
        result["year"]
    )

    if "month" in result.columns:
        result["month"] = _safe_numeric(
            result["month"]
        )

    result["value"] = _safe_numeric(
        result["value"]
    )

    # Solo se eliminan registros sin año válido.
    # No se imputan valores analíticos.
    result = result.loc[
        result["year"].between(1900, 2100)
    ].copy()

    result["year"] = result["year"].astype(int)

    if "month" in result.columns:
        result.loc[
            ~result["month"].between(1, 12),
            "month",
        ] = np.nan

    result = result.sort_values(
        ["date", "year"],
        kind="stable",
    ).reset_index(drop=True)

    return result
# ============================================================
# COMPLETITUD TEMPORAL
# ============================================================

def temporal_completeness(
    df: pd.DataFrame,
) -> dict[str, Any]:
    """
    Determina años completos y parciales.

    Un año completo requiere observar los 12 meses
    calendario al menos una vez.
    """

    empty_result = {
        "complete_years": [],
        "partial_years": [],
        "observed_years": [],
    }

    if df is None or df.empty:
        return empty_result

    if "date" not in df.columns:
        return empty_result

    valid_dates = pd.to_datetime(
        df["date"],
        errors="coerce",
    ).dropna()

    if valid_dates.empty:
        return empty_result

    # Obtener únicamente los meses realmente observados.
    monthly_periods = (
        valid_dates
        .dt.to_period("M")
        .drop_duplicates()
    )

    if monthly_periods.empty:
        return empty_result

    # Convertir explícitamente el PeriodIndex/Series resultante
    # a una estructura sobre la que podamos agrupar por año.
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

    observed_years = sorted(
        int(year)
        for year in months_by_year.index
    )

    complete_years = sorted(
        int(year)
        for year, count in months_by_year.items()
        if int(count) == 12
    )

    partial_years = sorted(
        int(year)
        for year, count in months_by_year.items()
        if int(count) < 12
    )

    return {
        "complete_years": complete_years,
        "partial_years": partial_years,
        "observed_years": observed_years,
    }

# ============================================================
# CALIDAD
# ============================================================

def data_quality_summary(
    df: pd.DataFrame,
) -> dict[str, Any]:

    if df.empty:
        return {
            "records": 0,
            "columns": 0,
            "missing": 0,
            "missing_pct": 0.0,
            "localities": 0,
            "start_year": None,
            "end_year": None,
            "months_observed": 0,
            "complete_years": [],
            "partial_years": [],
            "observed_years": [],
        }

    records = len(df)

    # Los faltantes se calculan sobre el dataframe original
    # transformado, sin contar artificialmente la columna date.
    missing = int(
        df.isna().sum().sum()
    )

    missing_pct = (
        missing / (records * len(df.columns)) * 100
        if records and len(df.columns)
        else 0.0
    )

    locality_count = 0

    if "locality" in df.columns:
        locality_count = int(
            df["locality"]
            .dropna()
            .nunique()
        )

    temporal = temporal_completeness(df)

    years = temporal["observed_years"]

    return {
        "records": records,
        "columns": len(df.columns),
        "missing": missing,
        "missing_pct": round(
            missing_pct,
            2,
        ),
        "localities": locality_count,
        "start_year": min(years) if years else None,
        "end_year": max(years) if years else None,
        "months_observed": (
            int(
                df["date"]
                .dropna()
                .dt.to_period("M")
                .nunique()
            )
            if "date" in df.columns
            else 0
        ),
        "complete_years": temporal[
            "complete_years"
        ],
        "partial_years": temporal[
            "partial_years"
        ],
        "observed_years": temporal[
            "observed_years"
        ],
    }


# ============================================================
# TENDENCIA ANUAL
# ============================================================

def trend_table(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty or "year" not in df.columns:
        return pd.DataFrame(
            columns=["year", "value"]
        )

    result = (
        df.groupby(
            "year",
            as_index=False,
        )["value"]
        .sum()
        .sort_values("year")
        .reset_index(drop=True)
    )

    return result


# ============================================================
# TENDENCIA MENSUAL
# ============================================================

def monthly_trend(
    df: pd.DataFrame,
) -> pd.DataFrame:

    columns = [
        "date",
        "year",
        "month",
        "value",
    ]

    if df.empty:
        return pd.DataFrame(
            columns=columns
        )

    work = df.loc[
        df["date"].notna()
        & df["value"].notna()
    ].copy()

    if work.empty:
        return pd.DataFrame(
            columns=columns
        )

    result = (
        work.groupby(
            ["date", "year", "month"],
            as_index=False,
        )["value"]
        .sum()
        .sort_values("date")
        .reset_index(drop=True)
    )

    return result


# ============================================================
# VARIACIÓN MENSUAL
# ============================================================

def monthly_variation(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = monthly_trend(df)

    if result.empty:
        return result

    result["previous"] = (
        result["value"].shift(1)
    )

    result["variation"] = (
        result["value"]
        - result["previous"]
    )

    result["variation_pct"] = np.where(
        result["previous"] != 0,
        (
            result["variation"]
            / result["previous"]
            * 100
        ),
        np.nan,
    )

    return result


# ============================================================
# ANOMALÍAS
# ============================================================

def detect_anomalies_monthly(
    df: pd.DataFrame,
    window: int = 12,
    z_threshold: float = 2.0,
) -> pd.DataFrame:

    result = monthly_trend(df)

    if result.empty:
        return result

    values = result["value"].astype(float)

    # Se utilizan únicamente observaciones anteriores.
    rolling_mean = (
        values
        .shift(1)
        .rolling(
            window=window,
            min_periods=max(3, window // 2),
        )
        .mean()
    )

    rolling_std = (
        values
        .shift(1)
        .rolling(
            window=window,
            min_periods=max(3, window // 2),
        )
        .std()
    )

    result["reference_mean"] = rolling_mean
    result["reference_std"] = rolling_std

    result["z_score"] = np.where(
        rolling_std > 0,
        (
            values
            - rolling_mean
        ) / rolling_std,
        np.nan,
    )

    result["is_anomaly"] = (
        result["z_score"]
        .abs()
        >= z_threshold
    )

    result["anomaly"] = result[
        "is_anomaly"
    ]

    return result


def detect_anomalies(
    df: pd.DataFrame,
    window: int = 3,
    z_threshold: float = 2.0,
) -> pd.DataFrame:

    if df.empty:
        return pd.DataFrame()

    # Si existen fechas, se utiliza el análisis mensual.
    if "date" in df.columns:
        return detect_anomalies_monthly(
            df,
            window=max(window, 3),
            z_threshold=z_threshold,
        )

    result = trend_table(df)

    if result.empty:
        return result

    values = result["value"].astype(float)

    rolling_mean = (
        values
        .shift(1)
        .rolling(
            window=window,
            min_periods=2,
        )
        .mean()
    )

    rolling_std = (
        values
        .shift(1)
        .rolling(
            window=window,
            min_periods=2,
        )
        .std()
    )

    result["reference_mean"] = rolling_mean
    result["reference_std"] = rolling_std

    result["z_score"] = np.where(
        rolling_std > 0,
        (
            values
            - rolling_mean
        ) / rolling_std,
        np.nan,
    )

    result["is_anomaly"] = (
        result["z_score"]
        .abs()
        >= z_threshold
    )

    result["anomaly"] = result[
        "is_anomaly"
    ]

    return result


# ============================================================
# ESTACIONALIDAD
# ============================================================

def seasonality_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:

    columns = [
        "month",
        "month_name",
        "mean",
        "std",
        "observations",
    ]

    if df.empty:
        return pd.DataFrame(
            columns=columns
        )

    if "date" not in df.columns:
        return pd.DataFrame(
            columns=columns
        )

    completeness = temporal_completeness(df)

    complete_years = completeness[
        "complete_years"
    ]

    work = df.loc[
        df["date"].notna()
        & df["value"].notna()
    ].copy()

    # Si existen años completos, se utilizan solamente
    # para evitar sesgos por años parciales.
    if complete_years:
        work = work.loc[
            work["year"].isin(
                complete_years
            )
        ]

    if work.empty:
        return pd.DataFrame(
            columns=columns
        )

    result = (
        work.groupby("month")["value"]
        .agg(
            mean="mean",
            std="std",
            observations="count",
        )
        .reset_index()
    )

    result["month_name"] = result[
        "month"
    ].map(MONTH_NAMES_ES)

    result = result[
        [
            "month",
            "month_name",
            "mean",
            "std",
            "observations",
        ]
    ].sort_values("month")

    return result.reset_index(
        drop=True
    )


# ============================================================
# FORMATO DE MES
# ============================================================

def format_month_es(
    value: Any,
) -> str:

    if pd.isna(value):
        return ""

    try:
        date = pd.to_datetime(value)
    except Exception:
        return str(value)

    month = MONTH_NAMES_ES.get(
        int(date.month),
        "",
    )

    return f"{month} de {date.year}"


# ============================================================
# PRONÓSTICO NAIVE
# ============================================================

def naive_forecast(
    values: pd.Series,
) -> float | None:

    clean = pd.to_numeric(
        values,
        errors="coerce",
    ).dropna()

    if clean.empty:
        return None

    return float(
        max(
            0.0,
            clean.iloc[-1],
        )
    )


# ============================================================
# CARACTERÍSTICAS PARA MODELOS
# ============================================================

def _build_forecast_features(
    series: pd.Series,
    frequency: str = "monthly",
) -> pd.DataFrame:

    values = pd.to_numeric(
        series,
        errors="coerce",
    )

    frame = pd.DataFrame(
        {
            "y": values
        }
    )

    if frequency == "monthly":

        frame["lag_1"] = (
            frame["y"].shift(1)
        )

        frame["lag_2"] = (
            frame["y"].shift(2)
        )

        frame["lag_3"] = (
            frame["y"].shift(3)
        )

        frame["lag_12"] = (
            frame["y"].shift(12)
        )

        frame["rolling_3"] = (
            frame["y"]
            .shift(1)
            .rolling(3)
            .mean()
        )

    else:

        frame["lag_1"] = (
            frame["y"].shift(1)
        )

        frame["lag_2"] = (
            frame["y"].shift(2)
        )

        frame["lag_3"] = (
            frame["y"].shift(3)
        )

        frame["rolling_3"] = (
            frame["y"]
            .shift(1)
            .rolling(3)
            .mean()
        )

    return frame


# ============================================================
# MÉTRICAS
# ============================================================

def _model_metrics(
    y_true: pd.Series,
    y_pred: np.ndarray,
) -> dict[str, float]:

    y_true = pd.to_numeric(
        y_true,
        errors="coerce",
    )

    y_pred = np.asarray(
        y_pred,
        dtype=float,
    )

    mae = mean_absolute_error(
        y_true,
        y_pred,
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_true,
            y_pred,
        )
    )

    try:
        r2 = r2_score(
            y_true,
            y_pred,
        )
    except Exception:
        r2 = np.nan

    return {
        "mae": round(
            float(mae),
            2,
        ),
        "rmse": round(
            float(rmse),
            2,
        ),
        "r2": round(
            float(r2),
            2,
        )
        if np.isfinite(r2)
        else None,
    }


# ============================================================
# EVALUACIÓN DE MODELOS
# ============================================================

def evaluate_forecast_models(
    df: pd.DataFrame,
) -> dict[str, Any]:

    empty_result = {
        "baseline": {
            "model": "Naive",
            "mae": None,
            "rmse": None,
            "r2": None,
        },
        "seasonal_naive": {
            "model": "Naive estacional",
            "mae": None,
            "rmse": None,
            "r2": None,
        },
        "random_forest": {
            "model": "Random Forest",
            "mae": None,
            "rmse": None,
            "r2": None,
        },
        "winner": None,
        "forecast": None,
        "forecast_label": None,
        "evaluation_years": [],
        "complete_years": [],
        "partial_years": [],
        "evaluation_observations": 0,
        "models_compared": [],
        "excluded_partial_year": None,
        "interpretation": (
            "No hay suficientes observaciones "
            "para realizar una evaluación "
            "predictiva temporal."
        ),
    }

    if df.empty:
        return empty_result

    monthly = (
        "date" in df.columns
        and df["date"].notna().any()
    )

    if monthly:

        trend = monthly_trend(df)

        if trend.empty:
            return empty_result

        completeness = temporal_completeness(
            df
        )

        complete_years = completeness[
            "complete_years"
        ]

        partial_years = completeness[
            "partial_years"
        ]

        # ----------------------------------------------------
        # Para evaluación histórica:
        # si hay años completos, se excluyen los años
        # parciales, especialmente el último año parcial.
        # ----------------------------------------------------

        evaluation = trend.copy()

        if complete_years:
            evaluation = evaluation.loc[
                evaluation["year"].isin(
                    complete_years
                )
            ].copy()

        evaluation = evaluation.sort_values(
            "date"
        )

        frequency = "monthly"

    else:

        trend = trend_table(df)

        if trend.empty:
            return empty_result

        completeness = temporal_completeness(
            df
        )

        complete_years = completeness[
            "complete_years"
        ]

        partial_years = completeness[
            "partial_years"
        ]

        evaluation = trend.copy()

        if complete_years:
            evaluation = evaluation.loc[
                evaluation["year"].isin(
                    complete_years
                )
            ].copy()

        evaluation = evaluation.sort_values(
            "year"
        )

        frequency = "annual"

    if len(evaluation) < 12:
        return {
            **empty_result,
            "complete_years": complete_years,
            "partial_years": partial_years,
            "evaluation_years": sorted(
                evaluation["year"]
                .unique()
                .tolist()
            )
            if "year" in evaluation.columns
            else [],
            "excluded_partial_year": (
                max(partial_years)
                if partial_years
                else None
            ),
        }

    series = evaluation[
        "value"
    ].astype(float).reset_index(
        drop=True
    )

    features = _build_forecast_features(
        series,
        frequency=frequency,
    )

    # --------------------------------------------------------
    # Naive
    # --------------------------------------------------------

    baseline_pred = series.shift(1)

    # --------------------------------------------------------
    # Naive estacional
    # --------------------------------------------------------

    if frequency == "monthly":
        seasonal_pred = series.shift(12)
    else:
        seasonal_pred = pd.Series(
            np.nan,
            index=series.index,
        )

    # --------------------------------------------------------
    # Random Forest
    # --------------------------------------------------------

    feature_columns = [
        "lag_1",
        "lag_2",
        "lag_3",
        "rolling_3",
    ]

    if frequency == "monthly":
        feature_columns.append(
            "lag_12"
        )

    model_data = features.dropna(
        subset=feature_columns
        + ["y"]
    ).copy()

    if len(model_data) < 12:
        return {
            **empty_result,
            "complete_years": complete_years,
            "partial_years": partial_years,
            "evaluation_years": sorted(
                evaluation["year"]
                .unique()
                .tolist()
            ),
            "excluded_partial_year": (
                max(partial_years)
                if partial_years
                else None
            ),
        }

    # --------------------------------------------------------
    # División temporal 80/20
    # --------------------------------------------------------

    split = int(
        len(model_data) * 0.80
    )

    if split < 5:
        return empty_result

    train = model_data.iloc[:split]
    test = model_data.iloc[split:]

    if test.empty:
        return empty_result

    # --------------------------------------------------------
    # Métricas Naive
    # --------------------------------------------------------

    baseline_eval = pd.DataFrame(
        {
            "actual": series,
            "pred": baseline_pred,
        }
    ).dropna()

    # Restricción temporal equivalente al test.
    test_start_index = test.index.min()

    baseline_test = baseline_eval.loc[
        baseline_eval.index >= test_start_index
    ]

    baseline_metrics = (
        _model_metrics(
            baseline_test["actual"],
            baseline_test["pred"],
        )
        if len(baseline_test) >= 2
        else {
            "mae": None,
            "rmse": None,
            "r2": None,
        }
    )

    # --------------------------------------------------------
    # Métricas Naive estacional
    # --------------------------------------------------------

    seasonal_eval = pd.DataFrame(
        {
            "actual": series,
            "pred": seasonal_pred,
        }
    ).dropna()

    seasonal_test = seasonal_eval.loc[
        seasonal_eval.index >= test_start_index
    ]

    seasonal_metrics = (
        _model_metrics(
            seasonal_test["actual"],
            seasonal_test["pred"],
        )
        if frequency == "monthly"
        and len(seasonal_test) >= 2
        else {
            "mae": None,
            "rmse": None,
            "r2": None,
        }
    )

    # --------------------------------------------------------
    # Random Forest
    # --------------------------------------------------------

    X_train = train[
        feature_columns
    ]

    y_train = train["y"]

    X_test = test[
        feature_columns
    ]

    y_test = test["y"]

    rf = RandomForestRegressor(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )

    rf.fit(
        X_train,
        y_train,
    )

    rf_pred = rf.predict(
        X_test
    )

    rf_metrics = _model_metrics(
        y_test,
        rf_pred,
    )

    # --------------------------------------------------------
    # Seleccionar ganador por MAE
    # --------------------------------------------------------

    candidates = {
        "Naive": baseline_metrics,
        "Naive estacional": seasonal_metrics,
        "Random Forest": rf_metrics,
    }

    valid_candidates = {
        name: metrics
        for name, metrics in candidates.items()
        if metrics.get("mae") is not None
    }

    if not valid_candidates:
        return empty_result

    winner = min(
        valid_candidates,
        key=lambda name: valid_candidates[
            name
        ]["mae"],
    )

    # --------------------------------------------------------
    # Pronóstico del siguiente periodo
    # --------------------------------------------------------

    latest_value = float(
        series.iloc[-1]
    )

    if winner == "Naive":

        forecast = latest_value

    elif winner == "Naive estacional":

        if frequency == "monthly" and len(series) >= 12:
            forecast = float(
                series.iloc[-12]
            )
        else:
            forecast = latest_value

    else:

        final_features = (
            _build_forecast_features(
                series,
                frequency=frequency,
            )
        )

        latest_row = final_features[
            feature_columns
        ].iloc[[-1]]

        # Si no se pueden construir las características
        # completas, se utiliza el último valor observado.
        if latest_row.isna().any().any():
            forecast = latest_value
        else:

            final_rf = RandomForestRegressor(
                n_estimators=300,
                max_depth=8,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
            )

            final_data = model_data

            final_rf.fit(
                final_data[
                    feature_columns
                ],
                final_data["y"],
            )

            forecast = float(
                final_rf.predict(
                    latest_row
                )[0]
            )

    forecast = max(
        0.0,
        float(forecast),
    )

    # --------------------------------------------------------
    # Etiqueta del pronóstico
    # --------------------------------------------------------

    if monthly:

        last_date = trend[
            "date"
        ].max()

        forecast_date = (
            last_date
            + pd.offsets.MonthBegin(1)
        )

        forecast_label = format_month_es(
            forecast_date
        )

    else:

        last_year = int(
            trend["year"].max()
        )

        forecast_label = str(
            last_year + 1
        )

    # --------------------------------------------------------
    # Interpretación metodológica
    # --------------------------------------------------------

    winner_metrics = valid_candidates[
        winner
    ]

    r2 = winner_metrics.get(
        "r2"
    )

    if r2 is not None and r2 < 0:

        interpretation = (
            f"El modelo con menor MAE en la "
            f"evaluación temporal fue {winner} "
            f"({winner_metrics['mae']:.2f}). "
            f"Su R² fue {r2:.2f}, por lo que el "
            f"modelo presenta capacidad explicativa "
            f"limitada frente a una referencia "
            f"basada en la media. El resultado es "
            f"exploratorio y no debe interpretarse "
            f"como una herramienta clínica ni como "
            f"una garantía del comportamiento futuro."
        )

    else:

        interpretation = (
            f"El modelo con menor MAE en la "
            f"evaluación temporal fue {winner} "
            f"({winner_metrics['mae']:.2f}). "
            f"El resultado corresponde a una "
            f"evaluación exploratoria de la serie "
            f"histórica y no constituye una "
            f"herramienta clínica ni una garantía "
            f"del comportamiento futuro."
        )

    return {
        "baseline": {
            "model": "Naive",
            **baseline_metrics,
        },
        "seasonal_naive": {
            "model": "Naive estacional",
            **seasonal_metrics,
        },
        "random_forest": {
            "model": "Random Forest",
            **rf_metrics,
        },
        "winner": winner,
        "forecast": round(
            forecast,
            1,
        ),
        "forecast_label": forecast_label,
        "evaluation_years": sorted(
            evaluation["year"]
            .unique()
            .tolist()
        ),
        "complete_years": complete_years,
        "partial_years": partial_years,
        "evaluation_observations": int(
            len(test)
        ),
        "models_compared": list(
            valid_candidates.keys()
        ),
        "excluded_partial_year": (
            max(partial_years)
            if partial_years
            else None
        ),
        "interpretation": interpretation,
    }


# ============================================================
# PRONÓSTICO DIRECTO
# ============================================================

def forecast_next(
    df: pd.DataFrame,
) -> dict[str, Any]:

    result = evaluate_forecast_models(
        df
    )

    return {
        "forecast": result.get(
            "forecast"
        ),
        "forecast_label": result.get(
            "forecast_label"
        ),
        "winner": result.get(
            "winner"
        ),
        "interpretation": result.get(
            "interpretation"
        ),
    }


# ============================================================
# RESUMEN GENERAL
# ============================================================

def build_analysis_summary(
    df: pd.DataFrame,
) -> dict[str, Any]:

    if df.empty:
        return {
            "records": 0,
            "average": 0,
            "maximum": 0,
            "maximum_label": None,
            "latest": 0,
            "latest_label": None,
        }

    monthly = monthly_trend(df)

    if monthly.empty:
        annual = trend_table(df)

        if annual.empty:
            return {
                "records": int(len(df)),
                "average": 0,
                "maximum": 0,
                "maximum_label": None,
                "latest": 0,
                "latest_label": None,
            }

        maximum_row = annual.loc[
            annual["value"].idxmax()
        ]

        latest_row = annual.iloc[-1]

        return {
            "records": int(len(df)),
            "average": round(
                float(
                    annual["value"].mean()
                ),
                1,
            ),
            "maximum": round(
                float(
                    maximum_row["value"]
                ),
                1,
            ),
            "maximum_label": str(
                int(maximum_row["year"])
            ),
            "latest": round(
                float(
                    latest_row["value"]
                ),
                1,
            ),
            "latest_label": str(
                int(latest_row["year"])
            ),
        }

    maximum_row = monthly.loc[
        monthly["value"].idxmax()
    ]

    latest_row = monthly.iloc[-1]

    return {
        "records": int(len(df)),
        "average": round(
            float(
                monthly["value"].mean()
            ),
            1,
        ),
        "maximum": round(
            float(
                maximum_row["value"]
            ),
            1,
        ),
        "maximum_label": format_month_es(
            maximum_row["date"]
        ),
        "latest": round(
            float(
                latest_row["value"]
            ),
            1,
        ),
        "latest_label": format_month_es(
            latest_row["date"]
        ),
    }