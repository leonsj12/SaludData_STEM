# -*- coding: utf-8 -*-

"""
SALUDDATA STEM
API principal

Versiones:

V1
---
/api/health
/api/summary
/api/analytics

V3
---
/api/explorer/options
/api/explorer/query

La API V3 utiliza el servicio explorer.py para realizar
consultas dinámicas sobre los archivos Parquet locales.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.services.local_data import get_api_summary
from app.services.analytics import obtener_analitica_dashboard
from app.services.explorer import (
    obtener_opciones,
    explorar,
)


# ============================================================
# BLUEPRINT
# ============================================================

api_bp = Blueprint(
    "api",
    __name__,
)


# ============================================================
# API V1 — SALUD DEL SISTEMA
# ============================================================

@api_bp.get("/api/health")
def health():

    return jsonify(
        {
            "status": "ok",
            "mode": "local-analytics-v1",
            "message": (
                "SaludData STEM funciona con "
                "analítica local."
            ),
        }
    )


# ============================================================
# API V1 — RESUMEN
# ============================================================

@api_bp.get("/api/summary")
def summary():

    return jsonify(
        get_api_summary()
    )


# ============================================================
# API V1 — ANALÍTICA PRECOMPUTADA
# ============================================================

@api_bp.get("/api/analytics")
def analytics():

    return jsonify(
        obtener_analitica_dashboard()
    )


# ============================================================
# API V3 — OPCIONES DE FILTROS
# ============================================================

@api_bp.get("/api/explorer/options")
def explorer_options():

    """
    Devuelve las opciones disponibles para construir
    los filtros del dashboard.

    Ejemplo:

        /api/explorer/options?dataset=cardiovascular
    """

    dataset = request.args.get(
        "dataset",
        "cardiovascular",
    )

    try:

        opciones = obtener_opciones(
            dataset
        )

        return jsonify(
            {
                "status": "ok",
                "dataset": dataset,
                "options": opciones,
            }
        )

    except ValueError as error:

        return jsonify(
            {
                "status": "error",
                "message": str(error),
            }
        ), 400

    except FileNotFoundError as error:

        return jsonify(
            {
                "status": "error",
                "message": str(error),
            }
        ), 404

    except Exception as error:

        return jsonify(
            {
                "status": "error",
                "message": (
                    "Error al obtener las opciones "
                    "del explorador."
                ),
                "detail": str(error),
            }
        ), 500


# ============================================================
# API V3 — CONSULTA FILTRADA
# ============================================================

@api_bp.get("/api/explorer/query")
def explorer_query():

    """
    Ejecuta una consulta filtrada.

    Parámetros disponibles:

        dataset
        year
        sex
        locality
        age_group
        cause

    Ejemplo:

        /api/explorer/query
        ?dataset=cardiovascular
        &year=2022
        &sex=Femenino

    Todos los filtros excepto dataset son opcionales.
    """

    dataset = request.args.get(
        "dataset",
        "cardiovascular",
    )

    # --------------------------------------------------------
    # AÑO
    # --------------------------------------------------------

    year_text = request.args.get(
        "year"
    )

    year = None

    if year_text:

        try:

            year = int(year_text)

        except ValueError:

            return jsonify(
                {
                    "status": "error",
                    "message": (
                        "El parámetro 'year' "
                        "debe ser un número entero."
                    ),
                }
            ), 400

    # --------------------------------------------------------
    # RESTO DE FILTROS
    # --------------------------------------------------------

    sex = request.args.get(
        "sex"
    )

    locality = request.args.get(
        "locality"
    )

    age_group = request.args.get(
        "age_group"
    )

    cause = request.args.get(
        "cause"
    )

    try:

        resultado = explorar(
            nombre=dataset,
            year=year,
            sex=sex,
            locality=locality,
            age_group=age_group,
            cause=cause,
        )

        return jsonify(
            {
                "status": "ok",
                "data": resultado,
            }
        )

    except ValueError as error:

        return jsonify(
            {
                "status": "error",
                "message": str(error),
            }
        ), 400

    except FileNotFoundError as error:

        return jsonify(
            {
                "status": "error",
                "message": str(error),
            }
        ), 404

    except Exception as error:

        return jsonify(
            {
                "status": "error",
                "message": (
                    "Error durante la consulta "
                    "del explorador."
                ),
                "detail": str(error),
            }
        ), 500