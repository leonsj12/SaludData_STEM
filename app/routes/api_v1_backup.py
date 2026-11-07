from flask import Blueprint, jsonify

from app.services.local_data import (
    get_api_summary
)

from app.services.analytics import (
    obtener_analitica_dashboard
)


api_bp = Blueprint(
    "api",
    __name__
)


# ---------------------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------------------
@api_bp.get("/api/health")
def health():

    return jsonify(
        {
            "status": "ok",
            "mode": "local-analytics-v1",
            "message": (
                "SaludData STEM funciona "
                "con analitica local."
            ),
        }
    )


# ---------------------------------------------------------------------
# RESUMEN DE DATOS
# ---------------------------------------------------------------------
@api_bp.get("/api/summary")
def summary():

    return jsonify(
        get_api_summary()
    )


# ---------------------------------------------------------------------
# ANALITICA
# ---------------------------------------------------------------------
@api_bp.get("/api/analytics")
def analytics():

    return jsonify(
        obtener_analitica_dashboard()
    )