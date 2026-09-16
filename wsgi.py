"""Punto de entrada WSGI para despliegues compatibles."""

from app import create_app

app = create_app()
