# Plan de proyecto — SaludData STEM

## 1. Producto

Aplicación web educativa y de investigación que transforma datos abiertos sanitarios de Bogotá en indicadores, visualizaciones y modelos analíticos reproducibles.

## 2. MVP

- Tres fuentes oficiales.
- Dashboard de una sola aplicación.
- Filtros temporales y demográficos.
- Tendencias.
- Desviaciones históricas.
- Modelo Random Forest experimental.
- Explicación metodológica.

## 3. Roadmap

### Fase 1 — MVP
- Ingesta CKAN.
- Limpieza.
- Dashboard.
- Pruebas.

### Fase 2 — Ambiente
- PM2.5.
- Normalización temporal.
- Asociación descriptiva.
- Visualización conjunta.

### Fase 3 — Educación STEM
- Tutorial paso a paso.
- Actividades reproducibles.
- Modo estudiante.
- Evaluación antes/después.

### Fase 4 — Producción
- Logs.
- Health check.
- CI/CD.
- Versionado de datos.
- Monitoreo.
- Documentación de cambios de fuentes.

## 4. Criterios de éxito

- El usuario puede actualizar datos sin modificar el código.
- El dashboard reproduce los mismos resultados a partir de la misma fuente.
- El modelo informa métricas y no solo una predicción.
- Las limitaciones aparecen dentro de la interfaz.
- No se presentan resultados como diagnóstico.

## 5. Arquitectura

```text
Datos Abiertos Bogotá
        |
        v
     CKAN/API
        |
        v
 Validación + limpieza
        |
        +------> Indicadores
        |
        +------> Anomalías
        |
        +------> Modelo ML
        |
        v
    Streamlit
        |
        v
Hallazgos explicables
```
