"""
SALUDDATA STEM
Punto de entrada para ejecutar el servidor Flask.

PEDAGOGÍA:
Este archivo es deliberadamente pequeño. Una buena arquitectura evita
concentrar toda la lógica en un único archivo. Aquí solamente iniciamos
la aplicación; las rutas y los servicios viven en módulos separados.

CONCEPTO:
- Punto de entrada.
- Importación de módulos.
- Servidor de desarrollo.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug=True facilita el aprendizaje durante el desarrollo:
    # Flask recarga la aplicación cuando cambia el código.
    # En producción debe utilizarse una configuración apropiada.
    app.run(host="127.0.0.1", port=5000, debug=True)
