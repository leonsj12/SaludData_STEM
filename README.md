<div align="center">

<img src="assets/banner-saluddata-stem.png" alt="SaludData STEM — Explorador interactivo de datos abiertos de salud pública" width="100%">

<br>

# SaludData STEM

### Explorador interactivo de datos abiertos de salud pública

<p>
Herramienta web desarrollada en Python para consultar, procesar, analizar y visualizar información abierta relacionada con salud pública mediante técnicas de ciencia de datos.
</p>

<br>

<a href="https://saluddata-stem-4ch5.onrender.com/">Aplicación en línea</a>
  ·   <a href="https://github.com/leonsj12/SaludData_STEM">Código fuente</a>

<br><br>

[![Estado](https://img.shields.io/badge/Estado-MVP%20funcional-16a34a?style=for-the-badge)](https://saluddata-stem-4ch5.onrender.com/)
[![Versión](https://img.shields.io/badge/Versión-2.3-2563eb?style=for-the-badge)](https://github.com/leonsj12/SaludData_STEM)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge\&logo=python\&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Web%20App-000000?style=for-the-badge\&logo=flask\&logoColor=white)](https://flask.palletsprojects.com/)

<br><br>

<img src="https://skillicons.dev/icons?i=python,flask,pandas,sklearn,plotly,git,github&theme=light" alt="Tecnologías: Python, Flask, Pandas, Scikit-learn, Plotly, Git y GitHub">

<br><br>

> **Convertir datos abiertos en información comprensible, reproducible y responsable.**

</div>

## Índice

* [Descripción](#descripción)
* [Propósito](#propósito)
* [Fuentes y datos disponibles](#fuentes-y-datos-disponibles)
* [Características principales](#características-principales)
* [Flujo de trabajo](#flujo-de-trabajo)
* [Arquitectura del sistema](#arquitectura-del-sistema)
* [Tecnologías utilizadas](#tecnologías-utilizadas)
* [Estructura del proyecto](#estructura-del-proyecto)
* [Instalación](#instalación)
* [Ejecución](#ejecución)
* [Dashboard](#dashboard)
* [Análisis disponibles](#análisis-disponibles)
* [Criterios metodológicos](#criterios-metodológicos)
* [Evaluación experimental de modelos](#evaluación-experimental-de-modelos)
* [Limitaciones](#limitaciones)
* [Reproducibilidad](#reproducibilidad)
* [Componente educativo STEM](#componente-educativo-stem)
* [Proyección académica](#proyección-académica)
* [Referencias](#referencias)
* [Colaboración](#colaboración)
* [Licencia](#licencia)

## Descripción

**SaludData STEM V2.3** es un prototipo funcional de ciencia de datos orientado a la exploración de información abierta relacionada con mortalidad cardiovascular, respiratoria y mortalidad general en Bogotá D.C.

La aplicación integra un flujo de preparación, procesamiento, análisis y visualización de datos. Actualmente trabaja con tres fuentes diferenciadas:

1. **Mortalidad cardiovascular**
2. **Mortalidad respiratoria**
3. **Mortalidad general**

El dashboard permite seleccionar la fuente de análisis y explorar sus dimensiones disponibles mediante indicadores y visualizaciones interactivas.

La versión actual incorpora una estrategia de **preprocesamiento y almacenamiento local de los datos**, de manera que la aplicación no necesita descargar y transformar los conjuntos completos cada vez que un usuario realiza una consulta. Los datos originales se conservan como archivos RAW y posteriormente se generan archivos procesados en formato Parquet para facilitar su lectura y utilización por la aplicación.

Esta evolución mantiene el propósito original de SaludData STEM: utilizar datos reales de salud pública como medio para aprender programación, ciencia de datos, análisis, visualización e interpretación responsable.

## Propósito

La disponibilidad de datos abiertos representa una oportunidad para acercar la ciencia de datos a problemas reales.

SaludData STEM propone un entorno en el que los datos recorren un proceso reproducible:

```text
Datos abiertos
      ↓
Adquisición y organización
      ↓
Validación
      ↓
Transformación
      ↓
Procesamiento
      ↓
Análisis exploratorio
      ↓
Indicadores y agregaciones
      ↓
Visualización interactiva
      ↓
Interpretación
```

El propósito es facilitar la exploración de información pública desde una perspectiva técnica, educativa y responsable.

El proyecto también busca utilizar este proceso como una experiencia de aprendizaje STEM, especialmente orientada a jóvenes mujeres interesadas en programación, ciencia de datos e investigación aplicada.

## Fuentes y datos disponibles

SaludData STEM utiliza conjuntos de datos abiertos relacionados con mortalidad en Bogotá D.C., publicados por entidades oficiales.

Entre las fuentes utilizadas se encuentran conjuntos de datos de la **Secretaría Distrital de Salud de Bogotá D.C.**

### Conjuntos actualmente integrados

| Fuente             | Registros procesados | Columnas | Granularidad principal |
| ------------------ | -------------------: | -------: | ---------------------- |
| Cardiovascular     |               74.560 |       13 | Mensual                |
| Respiratorio       |              164.840 |       13 | Mensual                |
| Mortalidad general |              274.627 |        7 | Anual                  |

Los conjuntos cardiovascular y respiratorio contienen variables relacionadas con año, mes, sexo, edad, localidad, clasificación de enfermedad y otras dimensiones disponibles en las fuentes originales. El conjunto de mortalidad general contiene información por año, localidad, sexo, grupo de edad, clasificación de causas y total de muertes.

Los datos se organizan en diferentes etapas dentro del proyecto:

```text
Datos originales
      ↓
data/raw/
      ↓
Validación y limpieza
      ↓
data/processed/
      ↓
Análisis y agregaciones
      ↓
data/analytics/
      ↓
API
      ↓
Dashboard
```

La interpretación debe considerar la cobertura temporal, granularidad, estructura, valores faltantes, duplicados y demás características propias de cada conjunto.

## Características principales

### Exploración de fuentes

El dashboard permite seleccionar entre tres fuentes:

* Cardiovascular.
* Respiratorio.
* Mortalidad general.

La interfaz actual implementa estos tres selectores directamente en el explorador.

### Preparación de datos

El proyecto incorpora procesos para:

* Lectura de archivos CSV.
* Detección de codificación y separadores.
* Limpieza básica.
* Normalización de estructuras.
* Validación de variables.
* Conservación de copias RAW.
* Conversión a formato Parquet.
* Generación de metadatos.

Los datos procesados se almacenan en `data/processed/`, mientras que los archivos originales se conservan en `data/raw/`.

### Análisis exploratorio

La aplicación permite explorar:

* Cantidad de registros.
* Distribución temporal.
* Dimensiones territoriales.
* Sexo.
* Edad.
* Causas o categorías disponibles.
* Indicadores descriptivos.
* Comportamientos de las series.

### Análisis temporal

La granularidad temporal depende de cada fuente.

Los conjuntos cardiovascular y respiratorio se procesan mediante series **mensuales**, mientras que la mortalidad general se procesa mediante una serie **anual**. En el procesamiento actual se identifican 196 periodos mensuales para las fuentes cardiovascular y respiratoria y 21 periodos anuales para mortalidad general.

### Visualización interactiva

El dashboard utiliza gráficos interactivos para facilitar la exploración de:

* Evolución temporal.
* Distribución territorial.
* Distribución por sexo.
* Distribución por edad.
* Categorías o causas.

La interfaz actual actualiza estas visualizaciones de acuerdo con la fuente seleccionada.

### Detección exploratoria de desviaciones

El motor analítico contempla la identificación estadística de observaciones que se apartan de determinados patrones.

Esta función tiene carácter exploratorio y descriptivo. Una desviación estadística no implica por sí misma una causa clínica o epidemiológica.

## Flujo de trabajo

<div align="center">

```text
┌──────────────────────┐
│ Datos abiertos       │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Adquisición          │
│ y organización       │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Validación y limpieza│
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Datos procesados     │
│ Parquet              │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Análisis             │
│ exploratorio         │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Agregaciones         │
│ e indicadores        │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ API                  │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Dashboard interactivo│
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Interpretación       │
└──────────────────────┘
```

</div>

## Arquitectura del sistema

La aplicación está desarrollada con **Python y Flask**.

La arquitectura actual separa la preparación de los datos de la consulta realizada por el dashboard.

```text
                   FUENTES DE DATOS
                          │
                          ▼
                ┌──────────────────┐
                │ Datos RAW        │
                │ CSV              │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Validación y     │
                │ limpieza         │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Datos procesados │
                │ Parquet          │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Motor analítico  │
                │ y agregaciones   │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ API Flask        │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Dashboard        │
                │ interactivo      │
                └──────────────────┘
```

La aplicación web consulta actualmente endpoints internos como:

```text
/api/analytics
/api/summary
```

El dashboard carga los resultados analíticos desde la API y posteriormente construye las visualizaciones en el navegador.

## Tecnologías utilizadas

<div align="center">

|    Tecnología    | Utilización                        |
| :--------------: | :--------------------------------- |
|    **Python**    | Lenguaje principal                 |
|     **Flask**    | Aplicación web y API               |
|    **Pandas**    | Manipulación y análisis de datos   |
| **Scikit-learn** | Experimentación con modelos        |
|    **Plotly**    | Visualización interactiva          |
|    **Parquet**   | Almacenamiento de datos procesados |
|      **Git**     | Control de versiones               |
|    **GitHub**    | Repositorio del proyecto           |
|    **Render**    | Despliegue de la aplicación        |

</div>

<br>

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,flask,pandas,sklearn,git,github&theme=light" alt="Stack tecnológico">
</p>

## Estructura del proyecto

La estructura del proyecto se organiza separando aplicación, datos, procesamiento y recursos visuales:

```text
SaludData_STEM/
│
├── app/
│   ├── templates/
│   │   └── dashboard.html
│   └── ...
│
├── assets/
│   └── banner-saluddata-stem.png
│
├── data/
│   ├── raw/
│   │   ├── cardiovascular.csv
│   │   ├── respiratorio.csv
│   │   └── mortalidad.csv
│   │
│   ├── processed/
│   │   ├── cardiovascular.parquet
│   │   ├── respiratorio.parquet
│   │   └── mortalidad.parquet
│   │
│   ├── analytics/
│   │   ├── cardiovascular_monthly.parquet
│   │   ├── respiratorio_monthly.parquet
│   │   ├── mortalidad_annual.parquet
│   │   └── ...
│   │
│   └── metadata/
│       ├── cardiovascular.json
│       ├── respiratorio.json
│       └── mortalidad.json
│
├── scripts/
│   ├── diagnostico.py
│   ├── analizar_datos.py
│   └── ...
│
├── tests/
│   └── ...
│
├── app.py
├── wsgi.py
├── requirements.txt
├── README.md
└── ...
```

Los nombres exactos de archivos auxiliares pueden evolucionar durante el desarrollo. La estructura conceptual importante es la separación entre **datos originales, datos procesados, resultados analíticos y aplicación web**.

## Instalación

### Clonar el repositorio

```bash
git clone https://github.com/leonsj12/SaludData_STEM.git
cd SaludData_STEM
```

### Crear un entorno virtual

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

## Ejecución

La ejecución local se realiza mediante Flask:

```bash
python app.py
```

Después, la aplicación puede abrirse desde el navegador utilizando la dirección local indicada por Flask.

### Aplicación en línea

La versión desplegada actualmente está disponible en:

**[SaludData STEM — Aplicación en línea](https://saluddata-stem-4ch5.onrender.com/)**

## Dashboard

El dashboard constituye la interfaz principal de exploración de los datos.

Actualmente permite seleccionar:

```text
01  Cardiovascular
02  Respiratorio
03  Mortalidad
```

Cada fuente presenta la información disponible de acuerdo con su propia estructura.

El flujo general del usuario es:

```text
Seleccionar fuente
        ↓
Consultar resumen
        ↓
Explorar serie temporal
        ↓
Explorar territorio
        ↓
Explorar sexo
        ↓
Explorar edad
        ↓
Explorar causas/categorías
        ↓
Interpretar resultados
```

La implementación actual actualiza el resumen y las visualizaciones cuando cambia la fuente seleccionada.

## Análisis disponibles

### Estadística descriptiva

Caracterización inicial de los conjuntos mediante cantidades, distribuciones y agregaciones relevantes para las variables disponibles.

### Análisis temporal

La aplicación construye series temporales según la frecuencia disponible:

* **Mensual:** cardiovascular.
* **Mensual:** respiratorio.
* **Anual:** mortalidad general.

### Análisis territorial

Permite explorar la distribución de los registros según las categorías territoriales disponibles en cada fuente, incluyendo la dimensión de localidad cuando está presente.

### Análisis por sexo

Permite comparar descriptivamente las categorías de sexo disponibles.

### Análisis por edad

Permite explorar los grupos de edad disponibles en cada conjunto.

### Análisis de causas y categorías

Permite visualizar las principales categorías presentes en la fuente seleccionada.

Cuando una fuente contiene una única categoría para determinada dimensión, el dashboard la presenta como información descriptiva en lugar de generar una comparación artificial.

### Detección de desviaciones

El motor analítico incorpora una etapa exploratoria de detección de desviaciones estadísticas.

En los análisis actuales se identificaron, por ejemplo, 5 desviaciones en la serie cardiovascular y 8 en la serie respiratoria durante el procesamiento registrado.

Estos resultados deben interpretarse únicamente como indicadores estadísticos exploratorios.

## Criterios metodológicos

El proyecto considera diferentes aspectos antes de interpretar los resultados.

### Calidad de los datos

Se revisan, entre otros elementos:

* Valores faltantes.
* Registros duplicados.
* Tipos de datos.
* Consistencia de variables.
* Valores extremos.
* Cobertura temporal.
* Granularidad.
* Estructura de las fuentes.
* Cambios en los conjuntos publicados.

En el procesamiento registrado, por ejemplo, los conjuntos cardiovascular y respiratorio presentan cero valores nulos, aunque se identifican registros duplicados que deben considerarse durante el análisis.

### Correspondencia entre método y datos

No todas las fuentes permiten realizar los mismos análisis.

Por ello, SaludData STEM adapta el procedimiento a:

* Cantidad de observaciones.
* Frecuencia temporal.
* Variables disponibles.
* Cobertura.
* Nivel de agregación.

Esto evita aplicar modelos o procedimientos estadísticos únicamente por razones técnicas cuando los datos no ofrecen condiciones suficientes para ello.

### Interpretación

Las tendencias, asociaciones y correlaciones encontradas deben interpretarse dentro del contexto de los datos utilizados.

Una asociación estadística no constituye evidencia suficiente de causalidad.

### Uso responsable

SaludData STEM es una herramienta académica, educativa y exploratoria.

No sustituye:

* Sistemas oficiales de información.
* Procesos de vigilancia epidemiológica.
* Estudios epidemiológicos especializados.
* Herramientas clínicas.
* Valoración médica profesional.

## Evaluación experimental de modelos

El proyecto contempla la evaluación experimental de modelos de pronóstico cuando la frecuencia, cantidad y estructura de los datos permiten construir un conjunto experimental adecuado.

El proceso general es:

```text
Datos históricos
      ↓
Preparación
      ↓
Construcción de serie
      ↓
Separación temporal
      ↓
Entrenamiento
      ↓
Predicción
      ↓
Evaluación
      ↓
Interpretación
```

Entre los modelos contemplados en el desarrollo experimental se encuentran:

* Modelo ingenuo (*Naive*).
* Naive estacional cuando corresponda.
* Random Forest.

La evaluación utiliza métricas apropiadas para el problema, como **MAE (Mean Absolute Error)**.

Los modelos tienen una finalidad **experimental y educativa**. No constituyen pronósticos oficiales, diagnósticos ni herramientas de decisión clínica.

## Limitaciones

Los resultados dependen de las características y calidad de las fuentes originales.

Entre las principales limitaciones se encuentran:

* Diferencias en la estructura de las fuentes.
* Diferencias de granularidad temporal.
* Cobertura temporal variable.
* Cambios en los conjuntos de datos.
* Valores faltantes o registros duplicados.
* Diferencias en las categorías disponibles.
* Posibles sesgos derivados de la fuente.
* Restricciones para determinados análisis estadísticos.
* Limitaciones para modelos predictivos cuando no existe suficiente información temporal.

Además, los conteos de eventos no deben interpretarse automáticamente como tasas poblacionales cuando no se dispone del denominador correspondiente.

Por estas razones, los resultados deben interpretarse como evidencia **descriptiva y exploratoria derivada de los datos disponibles**.

## Reproducibilidad

El proyecto busca favorecer la revisión y repetición del proceso de análisis.

La organización actual permite conservar diferentes etapas:

```text
Fuente original
      +
Fecha de consulta
      +
Datos RAW
      +
Datos procesados
      +
Metadatos
      +
Código
      +
Transformaciones
      +
Resultados analíticos
      +
Parámetros
```

La generación de archivos Parquet permite que la aplicación utilice datos previamente procesados en lugar de repetir toda la transformación durante cada consulta.

Esta estrategia mejora la organización del pipeline y contribuye a reducir el trabajo repetitivo durante la interacción con el dashboard.

## Componente educativo STEM

El componente STEM constituye una parte central del proyecto.

SaludData STEM propone que una estudiante pueda recorrer un proceso completo:

```text
Pregunta
   ↓
Fuente de datos
   ↓
Obtención
   ↓
Programación
   ↓
Limpieza
   ↓
Análisis
   ↓
Visualización
   ↓
Interpretación
   ↓
Comunicación
```

La estudiante puede asumir simultáneamente roles de:

* Investigadora.
* Programadora.
* Analista de datos.
* Exploradora científica.
* Comunicadora de resultados.

El objetivo es mostrar que la programación y la ciencia de datos pueden utilizarse para investigar problemas reales y construir evidencia comprensible.

El proyecto presta especial atención a la participación de jóvenes mujeres en STEM, buscando presentarlas como **creadoras de soluciones tecnológicas**, no solamente como usuarias de tecnología.

## Proyección académica

SaludData STEM plantea una integración entre:

```text
Datos abiertos
      +
Ciencia de datos
      +
Salud pública
      +
Programación
      +
Visualización
      +
Educación STEM
```

El proyecto puede continuar evolucionando mediante:

* Nuevas fuentes de datos.
* Nuevos indicadores.
* Mejoras en el pipeline.
* Nuevas visualizaciones.
* Métodos estadísticos adicionales.
* Modelos experimentales.
* Actividades educativas.
* Documentación pedagógica.

La ampliación de los datos y la optimización del almacenamiento no modifican la pregunta ni el propósito original del proyecto. Representan una evolución técnica del mismo prototipo para permitir una exploración más eficiente y organizada.

## Referencias

### Fuentes institucionales

* Secretaría Distrital de Salud de Bogotá D.C.
* Datos Abiertos Bogotá.
* Conjuntos de datos abiertos de mortalidad utilizados por el proyecto.

### Tecnologías

* Python.
* Flask.
* Pandas.
* Scikit-learn.
* Plotly.
* Git.
* GitHub.
* Render.

### Referencias académicas

El proyecto se fundamenta en literatura relacionada con:

* Enfermedades cardiovasculares.
* Calidad del aire y salud.
* Datos abiertos.
* Principios FAIR.
* Ciencia de datos reproducible.
* Análisis exploratorio.
* Aprendizaje automático.
* Educación STEM.
* Participación de mujeres en STEM.

Las referencias específicas deben mantenerse de acuerdo con las fuentes académicas e institucionales utilizadas en el documento principal del proyecto.

## Colaboración

**SaludData STEM** es un proyecto académico y tecnológico realizado por **Leon, S.**, con la colaboración de **[Leon, E.](https://github.com/eduardoleon9010?tab=repositories)** en actividades de revisión, aportes y fortalecimiento del proyecto.

### Leon, E.

**Colaborador**

<a href="https://github.com/eduardoleon9010?tab=repositories">
<img src="https://img.shields.io/badge/Leon%2C%20E.-Perfil%20y%20repositorios-181717?style=for-the-badge&logo=github&logoColor=white" alt="Leon, E. — Perfil de GitHub">
</a>

## Licencia

Este proyecto se presenta con fines académicos, educativos y de investigación.

El uso, modificación o distribución del código debe respetar las condiciones de las dependencias utilizadas y las licencias correspondientes.

Los datos utilizados pertenecen a sus respectivas fuentes de origen y deben utilizarse de acuerdo con las condiciones establecidas por dichas fuentes.

<div align="center">

<br>

**SaludData STEM**

*Datos abiertos · Ciencia de datos · Salud pública · Educación STEM*

<br>

<a href="https://github.com/leonsj12/SaludData_STEM">Repositorio</a>
 ·  <a href="https://saluddata-stem-4ch5.onrender.com/">Aplicación</a>

<br><br>

**Autor:** Leon, S.

**Colaborador:** [Leon, E.](https://github.com/eduardoleon9010?tab=repositories)

<br>

**V2.3**

</div>
