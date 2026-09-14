from flask import Flask


def create_app():
    app = Flask(__name__)

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    try:
        from app.routes.api import api_bp
        app.register_blueprint(api_bp)
    except ImportError:
        pass

    return app