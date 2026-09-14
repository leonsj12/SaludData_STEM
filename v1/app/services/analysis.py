from __future__ import annotations

import unicodedata

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


# ============================================================
# SALUDDATA STEM - MOTOR ANALITICO V2
# ============================================================
#
# Objetivo:
#   Proporcionar funciones reproducibles para:
#
#   1. Limpiar y normalizar datos de salud.
#   2. Construir series temporales mensuales.
#   3. Resumir calidad y cobertura de los datos.
#   4. Analizar tendencias.
#   5. Detectar anomalas estadisticas.
#   6. Explorar patrones estacionales.
#   7. Comparar un modelo base contra Random Forest.
#
# Importante:
#   Este modulo NO realiza diagnostico medico.
#   Los resultados son exploratorios y estadisticos.
#
# ============================================================


# ============================================================
# 1. LIMPIEZA DE TEXTO
# ============================================================

def _clean_text(s: pd.Series) -> pd.Series:
    """
    Limpia una serie de texto y convierte valores vacios
    en valores nulos.

    Se utiliza StringDtype de pandas para evitar algunos
    comportamientos problematicos de versiones recientes.
    """

    out = s.astype("string").str.strip()

    # Convertimos cadenas equivalentes a valores nulos.
    out = out.mask(
        out.isna()
        | out.isin(["", "nan", "None", "NaN", "NULL", "null"]),
        pd.NA,
    )

    return out


def _repair_text_encoding(value):
    """
    Intenta reparar textos que fueron interpretados con una
    codificacion incorrecta.

    Ejemplos conocidos:
        Usaqun     -> Usaquen
        San Crist¢bal -> San Cristobal

    La funcion trabaja de forma conservadora:
    si no puede reparar un valor, conserva el original.
    """

    if pd.isna(value):
        return value

    text = str(value)

    # Tabla de reemplazos para errores frecuentes encontrados
    # en datasets publicados en formato CSV.
    replacements = {
        "": "é",
        "¢": "ó",
        "£": "ú",
        "¤": "ñ",
        "¦": "í",
        "¡": "á",
        "": "Á",
        "©": "É",
        "È": "Í",
        "Ë": "Ó",
        "Ì": "Ú",
        "¤": "ñ",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return text


def _normalize_locality(value):
    """
    Normaliza nombres de localidades sin eliminar las tildes.

    Tambien conserva el codigo numerico inicial cuando existe.

    Ejemplo:
        01 - Usaquen
        06 - Tunjuelito
    """

    if pd.isna(value):
        return value

    text = _repair_text_encoding(value)
    text = str(text).strip()

    return text


def _normalize_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia las columnas de texto relevantes.
    """

    out = df.copy()

    text_columns = [
        "sex",
        "age_group",
        "locality",
        "cause_group",
        "cause",
    ]

    for column in text_columns:
        if column in out.columns:
            out[column] = _clean_text(out[column])

    if "locality" in out.columns:
        out["locality"] = out["locality"].map(_normalize_locality)

    return out


# ============================================================
# 2. PREPARACION Y NORMALIZACION DE DATOS
# ============================================================

def prepare_health_data(
    df: pd.DataFrame,
    mode: str,
) -> pd.DataFrame:
    """
    Normaliza las diferentes fuentes sanitarias de SaludData STEM
    a un esquema comun.

    Parameters
    ----------
    df:
        DataFrame original descargado desde CKAN.

    mode:
        "general" para la fuente general de mortalidad.
        "specific" para fuentes especificas.

    Returns
    -------
    pd.DataFrame
        Dataset normalizado.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df debe ser un pandas DataFrame.")

    if mode not in {"general", "specific"}:
        raise ValueError(
            "mode debe ser 'general' o 'specific'."
        )

    out = df.copy()

    # Normalizamos nombres de columnas.
    out.columns = [
        str(column).strip().upper()
        for column in out.columns
    ]

    # --------------------------------------------------------
    # FUENTE GENERAL
    # --------------------------------------------------------

    if mode == "general":

        rename = {
            "ANO": "year",
            "SEXO": "sex",
            "GRUPO DE EDAD": "age_group",
            "LOCALIDAD": "locality",
            "TOTAL MUERTES": "value",
            "DESCRIPCION LISTA 105": "cause",
        }

        out = out.rename(columns=rename)

        required_columns = [
            "year",
            "sex",
            "age_group",
            "locality",
            "value",
            "cause",
        ]

        for column in required_columns:
            if column not in out.columns:
                out[column] = np.nan

        # Año.
        out["year"] = pd.to_numeric(
            out["year"],
            errors="coerce",
        )

        # Valor numerico.
        value = (
            out["value"]
            .astype("string")
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )

        out["value"] = pd.to_numeric(
            value,
            errors="coerce",
        ).fillna(0.0)

        out = _normalize_text_columns(out)

        out = out.dropna(
            subset=["year"]
        )

        # Filtramos causas relacionadas con el alcance
        # cardiovascular y respiratorio del proyecto.
        mask = out["cause"].str.contains(
            "corazon|cardio|cerebro|circulator|respir|"
            "pulmon|bronqu|asma|neumon|EPOC",
            case=False,
            na=False,
            regex=True,
        )

        focused = out.loc[mask].copy()

        # Solo aplicamos el filtro si produjo resultados.
        if not focused.empty:
            out = focused

    # --------------------------------------------------------
    # FUENTES ESPECIFICAS
    # --------------------------------------------------------

    else:

        rename = {
            "ANO": "year",
            "SEXO": "sex",
            "EDAD_QUINQUENAL": "age_group",
            "EDAD_FALLECIDO": "age",
            "LOCALIDAD": "locality",
            "CIE10_AGRUPADA": "cause_group",
            "CIE10_BASICA": "cause",
        }

        out = out.rename(columns=rename)

        required_columns = [
            "year",
            "sex",
            "age_group",
            "age",
            "locality",
            "cause_group",
            "cause",
        ]

        for column in required_columns:
            if column not in out.columns:
                out[column] = np.nan

        # Año.
        out["year"] = pd.to_numeric(
            out["year"],
            errors="coerce",
        )

        # Edad.
        out["age"] = pd.to_numeric(
            out["age"],
            errors="coerce",
        )

        # Cada registro representa una observacion.
        out["value"] = 1.0

        out = _normalize_text_columns(out)

        out = out.dropna(
            subset=["year"]
        )

    return out.reset_index(drop=True)


# ============================================================
# 3. CALIDAD Y COBERTURA DE DATOS
# ============================================================

def data_quality_summary(
    df: pd.DataFrame,
) -> dict:
    """
    Genera un resumen de calidad y cobertura del dataset.

    El resultado esta pensado para ser mostrado en el dashboard.
    """

    if df.empty:
        return {
            "records": 0,
            "columns": 0,
            "missing_total": 0,
            "missing_percent": 0.0,
            "year_min": None,
            "year_max": None,
            "complete_years": [],
            "partial_years": [],
            "months_observed": 0,
            "localities": 0,
        }

    records = len(df)

    missing_total = int(
        df.isna().sum().sum()
    )

    total_cells = (
        df.shape[0] * df.shape[1]
    )

    missing_percent = (
        missing_total / total_cells * 100
        if total_cells
        else 0.0
    )

    result = {
        "records": records,
        "columns": df.shape[1],
        "missing_total": missing_total,
        "missing_percent": round(
            missing_percent,
            2,
        ),
        "year_min": None,
        "year_max": None,
        "complete_years": [],
        "partial_years": [],
        "months_observed": 0,
        "localities": 0,
    }

    if "year" in df.columns:

        years = pd.to_numeric(
            df["year"],
            errors="coerce",
        ).dropna()

        if not years.empty:

            result["year_min"] = int(
                years.min()
            )

            result["year_max"] = int(
                years.max()
            )

    if "MES" in df.columns and "year" in df.columns:

        month_table = (
            df.dropna(
                subset=["year", "MES"]
            )
            .groupby("year")["MES"]
            .nunique()
        )

        result["complete_years"] = [
            int(year)
            for year, count in month_table.items()
            if count == 12
        ]

        result["partial_years"] = [
            int(year)
            for year, count in month_table.items()
            if count < 12
        ]

        result["months_observed"] = int(
            month_table.sum()
        )

    if "locality" in df.columns:

        result["localities"] = int(
            df["locality"]
            .dropna()
            .nunique()
        )

    return result


# ============================================================
# 4. TENDENCIA ANUAL
# ============================================================

def trend_table(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Genera la tendencia anual.

    Se mantiene compatible con la V1.
    """

    if (
        df.empty
        or "value" not in df.columns
        or "year" not in df.columns
    ):
        return pd.DataFrame(
            columns=["year", "value"]
        )

    trend = (
        df.groupby(
            "year",
            as_index=False,
        )["value"]
        .sum()
        .sort_values("year")
        .reset_index(drop=True)
    )

    return trend


# ============================================================
# 5. TENDENCIA MENSUAL
# ============================================================

def monthly_trend(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Construye una serie temporal mensual.

    Resultado:

        year | month | date       | value
        2010 | 1     | 2010-01-01 | 398
        2010 | 2     | 2010-02-01 | 288
        ...

    Se utiliza el primer dia del mes como indice temporal.
    """

    required = [
        "year",
        "MES",
        "value",
    ]

    if df.empty:
        return pd.DataFrame(
            columns=[
                "year",
                "month",
                "date",
                "value",
            ]
        )

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        return pd.DataFrame(
            columns=[
                "year",
                "month",
                "date",
                "value",
            ]
        )

    work = df.copy()

    work["year"] = pd.to_numeric(
        work["year"],
        errors="coerce",
    )

    work["MES"] = pd.to_numeric(
        work["MES"],
        errors="coerce",
    )

    work["value"] = pd.to_numeric(
        work["value"],
        errors="coerce",
    )

    work = work.dropna(
        subset=[
            "year",
            "MES",
            "value",
        ]
    )

    work = work[
        work["MES"].between(1, 12)
    ]

    monthly = (
        work.groupby(
            ["year", "MES"],
            as_index=False,
        )["value"]
        .sum()
        .rename(
            columns={
                "MES": "month",
            }
        )
    )

    monthly["year"] = (
        monthly["year"]
        .astype(int)
    )

    monthly["month"] = (
        monthly["month"]
        .astype(int)
    )

    monthly["date"] = pd.to_datetime(
        dict(
            year=monthly["year"],
            month=monthly["month"],
            day=1,
        ),
        errors="coerce",
    )

    monthly = (
        monthly.sort_values("date")
        .reset_index(drop=True)
    )

    return monthly[
        [
            "year",
            "month",
            "date",
            "value",
        ]
    ]


# ============================================================
# 6. COMPLETITUD TEMPORAL
# ============================================================

def temporal_completeness(
    monthly: pd.DataFrame,
) -> pd.DataFrame:
    """
    Determina cuantos meses existen por cada año.

    Permite distinguir años completos de años parciales.
    """

    if monthly.empty:
        return pd.DataFrame(
            columns=[
                "year",
                "months",
                "complete",
            ]
        )

    result = (
        monthly.groupby("year")
        .agg(
            months=("month", "nunique")
        )
        .reset_index()
    )

    result["complete"] = (
        result["months"] == 12
    )

    return result


# ============================================================
# 7. ANOMALIAS ANUALES
# ============================================================

def detect_anomalies(
    trend: pd.DataFrame,
    window: int = 5,
    z: float = 2.0,
) -> pd.DataFrame:
    """
    Detecta desviaciones respecto a una ventana movil.

    Compatible con la V1.
    """

    if (
        trend.empty
        or "value" not in trend.columns
        or len(trend) < 6
    ):
        return pd.DataFrame()

    out = trend.copy()

    rolling_mean = (
        out["value"]
        .rolling(
            window,
            min_periods=3,
        )
        .mean()
    )

    rolling_std = (
        out["value"]
        .rolling(
            window,
            min_periods=3,
        )
        .std(ddof=0)
    )

    out["rolling_mean"] = rolling_mean

    out["rolling_std"] = rolling_std

    out["zscore"] = (
        out["value"] - rolling_mean
    ) / rolling_std.replace(
        0,
        np.nan,
    )

    out["anomaly"] = (
        out["zscore"]
        .abs()
        .fillna(0)
        >= z
    )

    return out


# ============================================================
# 8. ANOMALIAS MENSUALES
# ============================================================

def detect_anomalies_monthly(
    monthly: pd.DataFrame,
    window: int = 12,
    z: float = 2.5,
) -> pd.DataFrame:
    """
    Detecta anomalas en la serie mensual.

    Utiliza una ventana de 12 meses para comparar cada
    observacion con su comportamiento temporal reciente.

    El umbral por defecto es 2.5 desviaciones estandar.
    """

    if (
        monthly.empty
        or "value" not in monthly.columns
        or len(monthly) < 15
    ):
        return pd.DataFrame()

    out = monthly.copy()

    out = (
        out.sort_values("date")
        .reset_index(drop=True)
    )

    # Desplazamos un periodo para evitar comparar el dato
    # consigo mismo.
    previous = (
        out["value"]
        .shift(1)
    )

    rolling_mean = (
        previous
        .rolling(
            window,
            min_periods=6,
        )
        .mean()
    )

    rolling_std = (
        previous
        .rolling(
            window,
            min_periods=6,
        )
        .std(ddof=0)
    )

    out["rolling_mean"] = rolling_mean

    out["rolling_std"] = rolling_std

    out["zscore"] = (
        out["value"] - rolling_mean
    ) / rolling_std.replace(
        0,
        np.nan,
    )

    out["anomaly"] = (
        out["zscore"]
        .abs()
        >= z
    )

    return out


# ============================================================
# 9. ESTACIONALIDAD
# ============================================================

def seasonality_summary(
    monthly: pd.DataFrame,
) -> pd.DataFrame:
    """
    Resume el comportamiento historico por mes calendario.

    Esto permite explorar si algunos meses presentan valores
    sistematicamente mayores o menores.

    No implica causalidad.
    """

    if (
        monthly.empty
        or "month" not in monthly.columns
        or "value" not in monthly.columns
    ):
        return pd.DataFrame(
            columns=[
                "month",
                "mean",
                "median",
                "std",
                "min",
                "max",
                "observations",
            ]
        )

    result = (
        monthly.groupby("month")["value"]
        .agg(
            [
                "mean",
                "median",
                "std",
                "min",
                "max",
                "count",
            ]
        )
        .reset_index()
        .rename(
            columns={
                "count": "observations",
            }
        )
    )

    return result


# ============================================================
# 10. VARIACION INTERMENSUAL
# ============================================================

def monthly_variation(
    monthly: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calcula la variacion porcentual respecto al mes anterior.
    """

    if monthly.empty:
        return pd.DataFrame()

    out = (
        monthly.sort_values("date")
        .reset_index(drop=True)
        .copy()
    )

    out["variation"] = (
        out["value"]
        .pct_change()
        * 100
    )

    return out


# ============================================================
# 11. MODELO BASE
# ============================================================

def naive_forecast(
    trend: pd.DataFrame,
) -> dict | None:
    """
    Modelo base ingenuo.

    Predice el siguiente valor utilizando el ultimo valor
    observado.

    Se utiliza como referencia para evaluar si un modelo ML
    realmente aporta valor.
    """

    if (
        trend.empty
        or "value" not in trend.columns
        or len(trend) < 3
    ):
        return None

    values = (
        trend.sort_values("date")
        if "date" in trend.columns
        else trend.sort_values("year")
    )

    values = (
        values["value"]
        .astype(float)
        .reset_index(drop=True)
    )

    actual = values.iloc[1:]
    predicted = values.shift(1).iloc[1:]

    mae = mean_absolute_error(
        actual,
        predicted,
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual,
            predicted,
        )
    )

    r2 = r2_score(
        actual,
        predicted,
    )

    return {
        "model": "Naive",
        "forecast": float(values.iloc[-1]),
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
    }


# ============================================================
# 12. RANDOM FOREST
# ============================================================

def forecast_next(
    trend: pd.DataFrame,
):
    """
    Random Forest para pronostico exploratorio.

    Compatible con la V1.

    Idealmente debe utilizarse con una serie mensual, no con
    solamente 17 observaciones anuales.
    """

    if (
        trend.empty
        or "value" not in trend.columns
        or len(trend) < 10
    ):
        return None

    s = (
        trend.sort_values(
            "date"
            if "date" in trend.columns
            else "year"
        )
        .reset_index(drop=True)["value"]
        .astype(float)
    )

    data = pd.DataFrame(
        {
            "y": s,
        }
    )

    # Variables rezagadas.
    for lag in (1, 2, 3, 6, 12):
        if len(data) > lag:
            data[f"lag_{lag}"] = (
                data["y"].shift(lag)
            )

    # Promedios moviles.
    data["roll_3"] = (
        data["y"]
        .shift(1)
        .rolling(3)
        .mean()
    )

    data["roll_6"] = (
        data["y"]
        .shift(1)
        .rolling(6)
        .mean()
    )

    # Eliminamos filas sin suficientes observaciones.
    data = data.dropna()

    if len(data) < 20:
        return None

    X = data.drop(
        columns=["y"]
    )

    y = data["y"]

    # Division temporal.
    split = int(
        len(data) * 0.80
    )

    split = max(
        10,
        split,
    )

    if split >= len(data):
        split = len(data) - 1

    X_train = X.iloc[:split]
    X_test = X.iloc[split:]

    y_train = y.iloc[:split]
    y_test = y.iloc[split:]

    if X_test.empty:
        return None

    model = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        min_samples_leaf=2,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train,
    )

    prediction = model.predict(
        X_test
    )

    forecast = float(
        model.predict(
            X.iloc[[-1]]
        )[0]
    )

    mae = mean_absolute_error(
        y_test,
        prediction,
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            prediction,
        )
    )

    r2 = r2_score(
        y_test,
        prediction,
    ) if len(y_test) > 1 else np.nan

    importance = dict(
        zip(
            X.columns,
            model.feature_importances_,
        )
    )

    return {
        "model": "Random Forest",
        "forecast": forecast,
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
        "importance": {
            key: float(value)
            for key, value in importance.items()
        },
        "train_size": int(
            len(X_train)
        ),
        "test_size": int(
            len(X_test)
        ),
    }


# ============================================================
# 13. EVALUACION COMPARATIVA DE MODELOS
# ============================================================

def evaluate_forecast_models(
    monthly: pd.DataFrame,
) -> dict:
    """
    Compara un modelo ingenuo contra Random Forest.

    La comparacion se realiza sobre la serie mensual.

    Resultado:

        {
            "baseline": {...},
            "random_forest": {...},
            "winner": "...",
            "interpretation": "..."
        }

    El ganador se determina utilizando MAE.
    Menor MAE = mejor desempeño.
    """

    if (
        monthly.empty
        or "value" not in monthly.columns
        or len(monthly) < 20
    ):
        return {
            "baseline": None,
            "random_forest": None,
            "winner": None,
            "interpretation": (
                "No hay suficientes observaciones "
                "para comparar modelos."
            ),
        }

    work = (
        monthly.sort_values("date")
        .reset_index(drop=True)
        .copy()
    )

    # --------------------------------------------------------
    # Evaluacion temporal comun
    # --------------------------------------------------------

    values = (
        work["value"]
        .astype(float)
        .reset_index(drop=True)
    )

    # Usamos los ultimos 20% como prueba.
    split = int(
        len(values) * 0.80
    )

    split = max(
        12,
        split,
    )

    if split >= len(values):
        split = len(values) - 1

    test_actual = values.iloc[split:]

    # Modelo base: ultimo valor conocido.
    baseline_predictions = (
        values.shift(1)
        .iloc[split:]
    )

    baseline_valid = (
        ~baseline_predictions.isna()
    )

    baseline_actual = (
        test_actual.loc[
            baseline_valid.index[
                baseline_valid
            ]
        ]
    )

    baseline_pred = (
        baseline_predictions.loc[
            baseline_valid.index[
                baseline_valid
            ]
        ]
    )

    baseline_mae = mean_absolute_error(
        baseline_actual,
        baseline_pred,
    )

    baseline_rmse = np.sqrt(
        mean_squared_error(
            baseline_actual,
            baseline_pred,
        )
    )

    baseline_r2 = (
        r2_score(
            baseline_actual,
            baseline_pred,
        )
        if len(baseline_actual) > 1
        else np.nan
    )

    baseline = {
        "model": "Naive",
        "mae": float(baseline_mae),
        "rmse": float(baseline_rmse),
        "r2": float(baseline_r2),
    }

    # --------------------------------------------------------
    # Random Forest
    # --------------------------------------------------------

    data = pd.DataFrame(
        {
            "y": values,
        }
    )

    for lag in (
        1,
        2,
        3,
        6,
        12,
    ):
        data[
            f"lag_{lag}"
        ] = data["y"].shift(lag)

    data["roll_3"] = (
        data["y"]
        .shift(1)
        .rolling(3)
        .mean()
    )

    data["roll_6"] = (
        data["y"]
        .shift(1)
        .rolling(6)
        .mean()
    )

    data = data.dropna()

    if len(data) < 30:
        return {
            "baseline": baseline,
            "random_forest": None,
            "winner": "Naive",
            "interpretation": (
                "No hay suficientes observaciones "
                "para evaluar Random Forest."
            ),
        }

    X = data.drop(
        columns=["y"]
    )

    y = data["y"]

    split_ml = int(
        len(data) * 0.80
    )

    if split_ml >= len(data):
        split_ml = len(data) - 1

    X_train = X.iloc[:split_ml]
    X_test = X.iloc[split_ml:]

    y_train = y.iloc[:split_ml]
    y_test = y.iloc[split_ml:]

    model = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        min_samples_leaf=2,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train,
    )

    prediction = model.predict(
        X_test
    )

    rf_mae = mean_absolute_error(
        y_test,
        prediction,
    )

    rf_rmse = np.sqrt(
        mean_squared_error(
            y_test,
            prediction,
        )
    )

    rf_r2 = (
        r2_score(
            y_test,
            prediction,
        )
        if len(y_test) > 1
        else np.nan
    )

    random_forest = {
        "model": "Random Forest",
        "mae": float(rf_mae),
        "rmse": float(rf_rmse),
        "r2": float(rf_r2),
        "train_size": int(
            len(X_train)
        ),
        "test_size": int(
            len(X_test)
        ),
    }

    # --------------------------------------------------------
    # Seleccion del mejor modelo
    # --------------------------------------------------------

    if rf_mae < baseline_mae:
        winner = "Random Forest"

        interpretation = (
            "Random Forest presenta un MAE menor que "
            "el modelo base en el periodo de prueba. "
            "El resultado debe interpretarse como "
            "exploratorio y no como una garantia predictiva."
        )

    else:
        winner = "Naive"

        interpretation = (
            "El modelo base presenta un MAE menor o igual "
            "al de Random Forest. En consecuencia, el modelo "
            "de aprendizaje automatico no demuestra una "
            "mejora predictiva suficiente en esta evaluacion."
        )

    return {
        "baseline": baseline,
        "random_forest": random_forest,
        "winner": winner,
        "interpretation": interpretation,
    }


# ============================================================
# 14. RESUMEN ANALITICO GENERAL
# ============================================================

def build_analysis_summary(
    df: pd.DataFrame,
) -> dict:
    """
    Ejecuta las principales funciones analiticas y devuelve
    un resumen centralizado.

    Esta funcion facilita que Flask utilice un unico punto
    de entrada para el dashboard.
    """

    quality = data_quality_summary(
        df
    )

    annual = trend_table(
        df
    )

    monthly = monthly_trend(
        df
    )

    completeness = temporal_completeness(
        monthly
    )

    anomalies = detect_anomalies_monthly(
        monthly
    )

    seasonality = seasonality_summary(
        monthly
    )

    models = evaluate_forecast_models(
        monthly
    )

    return {
        "quality": quality,
        "annual": annual,
        "monthly": monthly,
        "completeness": completeness,
        "anomalies": anomalies,
        "seasonality": seasonality,
        "models": models,
    }