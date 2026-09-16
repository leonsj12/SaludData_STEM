"""
Rutas principales de la interfaz web.

PEDAGOGÍA:
Una ruta HTTP recibe una solicitud y devuelve una respuesta.
La ruta no debería contener cálculos complejos de ciencia de datos.
Esa responsabilidad pertenece a los servicios.
"""

from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    """Página inicial: explica el propósito educativo del proyecto."""
    return render_template("index.html")


@main_bp.get("/dashboard")
def dashboard():
    """Dashboard principal de exploración de datos."""
    return render_template("dashboard.html")
