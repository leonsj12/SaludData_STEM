from flask import Blueprint, jsonify, request

from app.routes.main import SOURCES
from app.services.data import load_dataset
from app.services.analysis import prepare_health_data, trend_table, detect_anomalies, forecast_next

api_bp = Blueprint("api", __name__)


@api_bp.get("/health")
def health():
    """Endpoint mínimo para comprobar que el servicio web está activo."""
    return jsonify({"status": "ok", "project": "SaludData STEM"})


@api_bp.get("/summary")
def summary():
    """Devuelve un resumen JSON de una fuente sanitaria."""
    key = request.args.get("fuente", "cardiovascular")
    if key not in SOURCES:
        return jsonify({"error": "Fuente no válida"}), 400

    source = SOURCES[key]
    raw = load_dataset(source["resource_id"])
    df = prepare_health_data(raw, source["mode"])
    trend = trend_table(df)
    anomaly = detect_anomalies(trend)
    model = forecast_next(trend)

    return jsonify({
        "source": source["label"],
        "records": int(len(df)),
        "years": sorted(df["year"].dropna().astype(int).unique().tolist()),
        "trend": trend.to_dict(orient="records"),
        "anomalies": anomaly.to_dict(orient="records") if not anomaly.empty else [],
        "model": model,
    })
