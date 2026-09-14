from flask import Flask


def create_app():
    """Crea y configura la aplicación Flask usando el patrón Application Factory."""
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY="saluddata-stem-dev")

    from .routes.main import main_bp
    from .routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
