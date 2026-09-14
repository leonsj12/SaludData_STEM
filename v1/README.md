# SaludData STEM — Flask

Prototipo web modular en Python + Flask para analizar datos abiertos de salud de Bogotá.

## Arquitectura

```text
SaludData_STEM/
├── app/
│   ├── __init__.py
│   ├── routes/
│   │   ├── main.py
│   │   └── api.py
│   ├── services/
│   │   ├── data.py
│   │   └── analysis.py
│   ├── templates/
│   └── static/
├── tests/
├── docs/
├── run.py
├── wsgi.py
├── requirements.txt
├── render.yaml
└── Dockerfile
```

## Ejecutar en Windows

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python run.py
```

Abrir: http://127.0.0.1:5000

API de salud: http://127.0.0.1:5000/api/health

## Pruebas

```powershell
pytest -q
```

## Git

```powershell
git init
git add .
git commit -m "feat: primer prototipo Flask de SaludData STEM"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/saluddata-stem.git
git push -u origin main
```

## Despliegue

Render puede usar el `render.yaml` incluido. Build: `pip install -r requirements.txt`. Start: `gunicorn wsgi:app`.

## Nota científica

Los resultados son exploratorios. No son diagnósticos, no sustituyen vigilancia epidemiológica y una asociación estadística no demuestra causalidad.

## Flujo profesional recomendado

```text
Local → Git → GitHub → GitHub Actions → Render → URL pública
```

- **Local:** desarrollo y pruebas.
- **Git:** historial y control de versiones.
- **GitHub:** repositorio central.
- **GitHub Actions:** ejecuta pruebas automáticamente.
- **Render:** despliegue web público.

Para producción, Flask no debe exponerse mediante el servidor de desarrollo; se utiliza Gunicorn, que es el comando configurado en `render.yaml` y `wsgi.py`.
