# Flujo de datos

```text
FUENTE OFICIAL
      │
      ▼
data/raw/
      │
      │ Extract
      ▼
LECTURA ROBUSTA
      │
      │ Transform
      ▼
NORMALIZACIÓN
      │
      ▼
data/processed/
      │
      │ Load
      ▼
SERVICIOS DE ANÁLISIS
      │
      ▼
API FLASK
      │
      ▼
DASHBOARD
      │
      ▼
INTERPRETACIÓN HUMANA
```

## ¿Por qué no descargar en cada consulta?

Porque la visualización y la adquisición son problemas diferentes.

La descarga puede:

- tardar;
- fallar;
- depender de Internet;
- cambiar la estructura;
- aumentar el tiempo de respuesta.

Separar ambos procesos hace que el dashboard sea más estable.

## ¿Por qué conservar RAW?

Para mantener una referencia del material descargado.

## ¿Por qué Parquet?

Porque es adecuado para análisis tabular y permite lecturas eficientes.

## ¿Por qué GitHub?

Git permite estudiar la evolución del código y GitHub facilita compartir
el proyecto y hacerlo reproducible.

No es obligatorio subir archivos RAW grandes. Se puede versionar el código,
metadatos y datasets procesados cuando su tamaño lo permita.
