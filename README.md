# SaludData STEM — V3 Pedagógica

## Analiza · Aprende · Automatiza

SaludData STEM es un proyecto educativo de programación, ciencia de datos y análisis exploratorio construido con Python y Flask.

El proyecto utiliza datos abiertos oficiales de Bogotá para explorar patrones y tendencias relacionados con salud cardiovascular y respiratoria. **No es una herramienta clínica ni realiza diagnósticos.**

## Objetivo pedagógico

El código está documentado internamente para que cada componente explique:

1. Qué hace.
2. Cómo lo hace.
3. Por qué se diseñó así.
4. Qué concepto de programación o ciencia de datos se está aprendiendo.

La ruta metodológica es:

`DATOS CRUDOS → CALIDAD → LIMPIEZA → TRANSFORMACIÓN → ANÁLISIS → VISUALIZACIÓN → INTERPRETACIÓN`

## Arquitectura

```text
data/raw/          Datos originales descargados de las fuentes oficiales
       ↓
data/processed/    Datos limpios y optimizados en Parquet
       ↓
data/analytics/    Agregaciones preparadas para visualización
       ↓
app/services/      Lógica de datos y análisis
       ↓
app/routes/        API y páginas Flask
       ↓
templates + JS     Dashboard interactivo
```

La aplicación web **no descarga datos en cada visita**. La actualización se realiza mediante:

```cmd
python scripts\update_data.py
```

Después:

```cmd
python run.py
```

Abrir:

`http://127.0.0.1:5000`

## Instalación en Windows

Se recomienda Python 3.12 de 64 bits.

```cmd
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts\update_data.py
python run.py
```

## Si ya existe el entorno virtual

```cmd
.venv\Scripts\activate
pip install -r requirements.txt
python scripts\update_data.py
python run.py
```

## Conceptos STEM que se pueden estudiar

- Variables y tipos de datos.
- Funciones.
- Módulos.
- Excepciones.
- Programación orientada a servicios.
- ETL: Extract, Transform, Load.
- Calidad de datos.
- Codificación de caracteres.
- Separadores CSV.
- DataFrames.
- Agregación.
- Series temporales.
- Anomalías estadísticas.
- Visualización.
- APIs REST.
- Arquitectura cliente-servidor.
- Reproducibilidad.
- Pruebas automatizadas.
- Git y GitHub.
- Introducción al aprendizaje automático.

## Importante

Una disminución o aumento estadístico observado en los datos no demuestra por sí mismo una causa médica. Los resultados deben interpretarse como exploración de datos públicos y no como diagnóstico, pronóstico individual ni recomendación sanitaria.
