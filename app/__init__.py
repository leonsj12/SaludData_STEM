"""
Fábrica de la aplicación Flask.

PEDAGOGÍA:
En lugar de crear una aplicación monolítica, usamos el patrón
Application Factory. Esto permite crear la aplicación desde un único
punto y facilita las pruebas automatizadas y futuros entornos.

CONCEPTO STEM:
Arquitectura modular y separación de responsabilidades.
"""

from flask import Flask


def create_app():
    """Construye y configura una instancia de Flask."""
    app = Flask(__name__)

    # Las rutas se registran aquí para mantener separado el transporte
    # HTTP de la lógica de análisis.
    from app.routes.main import main_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    return app
