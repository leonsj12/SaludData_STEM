# Manual pedagógico de SaludData STEM

## 1. Filosofía

Este proyecto no se diseñó solamente para "tener una aplicación funcionando".
Se diseñó como un laboratorio de aprendizaje.

Cada módulo intenta responder cuatro preguntas:

> ¿Qué hace?
>
> ¿Cómo lo hace?
>
> ¿Por qué lo hacemos así?
>
> ¿Qué concepto STEM estamos aprendiendo?

## 2. Ruta completa de ciencia de datos

### Etapa 1 — Pregunta

Una investigación comienza con una pregunta clara.

Ejemplo:

> ¿Cómo cambian determinados indicadores de salud pública a través del tiempo?

Una buena pregunta limita qué datos necesitamos.

### Etapa 2 — Datos

Se identifican fuentes abiertas oficiales.

No debemos asumir que un archivo está limpio solamente porque proviene
de una institución.

### Etapa 3 — Programación

Python permite automatizar tareas repetitivas:

- lectura;
- limpieza;
- transformación;
- análisis;
- visualización.

### Etapa 4 — Calidad

Antes de analizar:

- revisar columnas;
- detectar valores faltantes;
- revisar tipos;
- revisar duplicados cuando corresponda;
- comprobar fechas;
- documentar decisiones.

### Etapa 5 — Transformación

Un DataFrame puede transformarse para responder preguntas concretas.

Ejemplo:

`registros individuales → suma mensual`

### Etapa 6 — Análisis

Se estudian:

- tendencias;
- variaciones;
- distribuciones;
- relaciones;
- anomalías.

### Etapa 7 — Visualización

Una gráfica convierte una tabla en una representación visual.

Pero una gráfica también puede engañar si:

- los ejes están mal;
- falta contexto;
- se mezclan unidades;
- se comparan periodos incompletos.

### Etapa 8 — Interpretación

El resultado debe distinguir:

**Observación:** "el valor aumentó".

**Hipótesis:** "podría existir una explicación".

**Causalidad:** requiere evidencia adicional y un diseño apropiado.

SaludData STEM no pretende demostrar causalidad clínica.

## 3. Conceptos de programación

### Funciones

Una función encapsula una tarea.

```python
def monthly_change(series):
    ...
```

Ventaja pedagógica: permite reutilizar y probar el procedimiento.

### Módulos

El proyecto divide responsabilidades:

- `data.py`: preparación;
- `analysis.py`: análisis;
- `local_data.py`: almacenamiento;
- `api.py`: comunicación;
- `main.py`: interfaz;
- `update_data.py`: actualización.

### Excepciones

Las excepciones permiten controlar problemas sin ocultarlos.

Por ejemplo, un CSV puede no poder interpretarse con una codificación.

## 4. Conceptos de ciencia de datos

### DataFrame

Un DataFrame es una estructura tabular de pandas.

Puede imaginarse como una tabla:

| ANO | MES | LOCALIDAD | TOTAL |
|---|---|---|---:|
| 2025 | 1 | X | 12 |

### Agregación

Agrupar significa transformar muchos registros en un resumen.

Ejemplo:

`groupby(["ANO", "MES"]).sum()`

### Serie temporal

Una serie temporal ordena observaciones según el tiempo.

Esto permite estudiar:

- tendencia;
- estacionalidad;
- cambios;
- anomalías.

## 5. Anomalías

El z-score se expresa conceptualmente como:

`z = (x - media) / desviación estándar`

Un z-score grande indica distancia respecto de la media.

Pero:

**anómalo estadísticamente ≠ clínicamente peligroso**

## 6. Aprendizaje automático

El proyecto puede evolucionar hacia modelos de series temporales y aprendizaje
supervisado.

Antes de usar un modelo debemos definir:

- variable objetivo;
- variables predictoras;
- conjunto de entrenamiento;
- conjunto de prueba;
- métrica;
- línea base.

Una predicción debe compararse contra una estrategia sencilla.

Por ejemplo:

> "El siguiente periodo será igual al anterior"

puede ser una línea base útil.

Si un modelo sofisticado no supera la línea base, debemos preguntarnos
si la complejidad está aportando valor.

## 7. Métricas

### MAE

Error absoluto medio.

Interpretación sencilla:

> en promedio, ¿a cuántas unidades se distancia la predicción del valor real?

### RMSE

Penaliza más los errores grandes.

### R²

Mide cuánto de la variabilidad de la variable objetivo explica el modelo
respecto de una referencia.

Un R² negativo puede ocurrir cuando el modelo funciona peor que una
referencia simple. No significa que Python esté "dañado".

## 8. Reproducibilidad

La ciencia de datos debe poder repetirse.

Por eso:

- guardamos la fuente;
- registramos fecha de descarga;
- guardamos versiones procesadas;
- documentamos transformaciones;
- automatizamos pruebas.

## 9. Ética

Los datos de salud requieren especial cuidado.

SaludData STEM trabaja con información pública y agregada, pero aun así
se debe evitar:

- identificar personas;
- diagnosticar;
- estigmatizar localidades;
- presentar correlaciones como causas;
- convertir una alerta estadística en una alerta médica.

## 10. Perspectiva de mujeres en STEM

El proyecto puede utilizarse para mostrar que las jóvenes pueden participar
en todo el ciclo tecnológico:

`PREGUNTA → PROGRAMACIÓN → DATOS → MODELO → INTERPRETACIÓN → COMUNICACIÓN`

La perspectiva STEM no consiste solamente en usar tecnología: consiste
en comprenderla, construirla, cuestionarla y comunicar sus resultados.
