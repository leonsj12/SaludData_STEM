<div align="center">

<img src="assets/banner-saluddata-stem.png" alt="SaludData STEM — Explorador interactivo de datos abiertos de salud pública" width="100%">

<br><br>

# SaludData STEM

### Explorador interactivo de datos abiertos de salud pública

Herramienta web para consultar, validar, transformar, analizar y visualizar información abierta relacionada con salud pública mediante técnicas de ciencia de datos.

<br>

**Python · Flask · Pandas · Scikit-learn · Plotly · CKAN**

<br><br>

[![Estado](https://img.shields.io/badge/Estado-MVP%20funcional-16a34a?style=for-the-badge)](https://saluddata-stem.onrender.com)
[![Versión](https://img.shields.io/badge/Versión-2.3-2563eb?style=for-the-badge)](https://github.com/leonsj12/SaludData_STEM)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Web%20App-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Licencia](https://img.shields.io/badge/Licencia-Académica-64748b?style=for-the-badge)](#licencia)

<br>

[Aplicación en línea](https://saluddata-stem.onrender.com) · [Repositorio](https://github.com/leonsj12/SaludData_STEM)

<br><br>

> **Convertir datos abiertos en información comprensible, reproducible y responsable.**

</div>

---

## Índice

- [Descripción](#descripción)
- [Propósito](#propósito)
- [Características principales](#características-principales)
- [Fuentes de datos](#fuentes-de-datos)
- [Arquitectura del sistema](#arquitectura-del-sistema)
- [Tecnologías utilizadas](#tecnologías-utilizadas)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Ejecución](#ejecución)
- [Funcionamiento del dashboard](#funcionamiento-del-dashboard)
- [Análisis disponibles](#análisis-disponibles)
- [Evaluación experimental de modelos](#evaluación-experimental-de-modelos)
- [Criterios metodológicos](#criterios-metodológicos)
- [Limitaciones](#limitaciones)
- [Reproducibilidad](#reproducibilidad)
- [Proyección académica](#proyección-académica)
- [Referencias](#referencias)
- [Colaboración](#colaboración)
- [Licencia](#licencia)

---

## Descripción

**SaludData STEM V2.3** es un prototipo funcional de ciencia de datos orientado al análisis exploratorio de información abierta relacionada con la mortalidad cardiovascular y respiratoria en Bogotá D.C.

La aplicación web fue desarrollada en **Python y Flask** e integra diferentes etapas del procesamiento de datos, incluyendo consulta, validación, transformación, análisis estadístico, análisis temporal, visualización y evaluación experimental de modelos cuando las características de la fuente lo permiten.

El proyecto busca transformar registros públicos en información comprensible y útil para la exploración de fenómenos relacionados con salud pública, incorporando además una perspectiva educativa vinculada con las áreas de ciencia, tecnología, ingeniería y matemáticas (STEM).

---

## Propósito

La disponibilidad de datos abiertos constituye una oportunidad para acercar la ciencia de datos a problemas reales y fortalecer experiencias educativas basadas en información pública.

**SaludData STEM** propone un entorno donde los datos pueden ser explorados mediante un flujo de trabajo reproducible:

```text
Datos abiertos
      ↓
Consulta y adquisición
      ↓
Validación
      ↓
Transformación
      ↓
Análisis exploratorio
      ↓
Indicadores y análisis temporal
      ↓
Visualización
      ↓
Evaluación experimental
      ↓
Interpretación
```

El propósito no es únicamente presentar gráficos, sino facilitar un proceso de análisis que permita comprender cómo los datos públicos pueden convertirse en información para la investigación y el aprendizaje.

---

## Características principales

### Exploración de datos

- Consulta de información abierta relacionada con salud pública.
- Revisión y validación de los datos.
- Transformación y normalización de variables.
- Filtrado de información para diferentes perspectivas de análisis.

### Análisis exploratorio

- Estadística descriptiva.
- Distribución de variables.
- Indicadores de resumen.
- Comparación de categorías.
- Identificación de tendencias y comportamientos relevantes.

### Análisis temporal

- Evolución de registros a través del tiempo.
- Comparación de periodos.
- Identificación de variaciones.
- Detección exploratoria de desviaciones estadísticas.

### Visualización interactiva

La aplicación utiliza **Plotly** para presentar información mediante visualizaciones interactivas que facilitan la exploración de los resultados.

### Evaluación experimental

Cuando la granularidad y cobertura de los datos lo permiten, se realizan experimentos con modelos de pronóstico y procedimientos de evaluación.

Estos resultados tienen carácter **experimental y académico** y no constituyen predicciones médicas ni epidemiológicas oficiales.

### Enfoque STEM

El proyecto utiliza datos reales como recurso para fortalecer experiencias de aprendizaje relacionadas con ciencia, tecnología, ingeniería y matemáticas, con especial interés en contribuir al acercamiento de jóvenes mujeres a experiencias de ciencia de datos y tecnología.

---

## Fuentes de datos

SaludData STEM utiliza información pública relacionada con salud y mortalidad disponible a través de fuentes institucionales.

Entre las fuentes utilizadas se encuentran conjuntos de datos publicados por la **Secretaría Distrital de Salud de Bogotá D.C.**

La aplicación contempla mecanismos de consulta e integración con plataformas de datos abiertos, incluyendo servicios basados en **CKAN** cuando están disponibles.

La interpretación de los resultados debe considerar siempre:

- La calidad de los datos originales.
- La cobertura temporal.
- La granularidad de los registros.
- Los valores faltantes.
- Las transformaciones realizadas.
- Los posibles sesgos.
- Las condiciones bajo las cuales fueron generados los datos.

---

## Arquitectura del sistema

El sistema integra una aplicación web desarrollada con Flask y diferentes componentes especializados para procesamiento, análisis y visualización.

```text
┌─────────────────────────────────────┐
│          FUENTES DE DATOS            │
│     Datos abiertos de salud pública  │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│        ADQUISICIÓN Y VALIDACIÓN      │
│              Python / CKAN           │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│       PROCESAMIENTO DE DATOS         │
│              Pandas                  │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│      ANÁLISIS Y MODELOS              │
│        Scikit-learn / Python         │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│       VISUALIZACIÓN INTERACTIVA      │
│               Plotly                 │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│          APLICACIÓN WEB              │
│               Flask                  │
└─────────────────────────────────────┘
```

---

## Tecnologías utilizadas

| Tecnología | Aplicación en el proyecto |
|---|---|
| **Python** | Lenguaje principal |
| **Flask** | Desarrollo de la aplicación web |
| **Pandas** | Manipulación y transformación de datos |
| **Scikit-learn** | Procesamiento y evaluación experimental |
| **Plotly** | Visualización interactiva |
| **CKAN** | Consulta e integración de datos abiertos |
| **Git** | Control de versiones |
| **GitHub** | Repositorio y colaboración |
| **Render** | Despliegue de la aplicación |

---

## Estructura del proyecto

La estructura del repositorio se organiza para separar los recursos visuales, componentes de la aplicación y archivos de configuración.

```text
SaludData_STEM/
│
├── assets/
│   └── banner-saluddata-stem.png
│
├── static/
│   └── ...
│
├── templates/
│   └── ...
│
├── app.py
├── requirements.txt
├── README.md
└── ...
```

> La estructura puede evolucionar a medida que se incorporen nuevos componentes, análisis y fuentes de datos.

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/leonsj12/SaludData_STEM.git
cd SaludData_STEM
```

### 2. Crear un entorno virtual

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

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

---

## Ejecución

Una vez instalado el entorno y sus dependencias:

```bash
python app.py
```

La aplicación estará disponible en la dirección local indicada por Flask.

### Aplicación desplegada

La versión funcional del proyecto se encuentra disponible en:

**[Abrir SaludData STEM](https://saluddata-stem.onrender.com)**

---

## Funcionamiento del dashboard

El dashboard constituye la interfaz principal de exploración de la información.

Su objetivo es facilitar el paso desde los datos originales hacia diferentes niveles de análisis:

```text
                    DATOS
                      │
                      ▼
              ┌───────────────┐
              │ Exploración   │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │  Indicadores  │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ Visualización │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ Análisis      │
              │ temporal      │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ Experimentación│
              └───────────────┘
```

La interfaz está orientada a favorecer una lectura progresiva de la información y permitir que los resultados puedan explorarse de manera interactiva.

---

## Análisis disponibles

### Estadística descriptiva

Permite caracterizar los datos mediante medidas estadísticas y distribuciones relevantes para las variables disponibles.

### Análisis temporal

Permite observar la evolución de los registros y comparar diferentes periodos disponibles en las fuentes.

### Distribución de variables

Facilita la exploración de frecuencias, categorías y comportamientos de las variables seleccionadas.

### Desviaciones estadísticas

Se pueden realizar procedimientos exploratorios orientados a identificar observaciones o periodos que presentan comportamientos alejados de determinados patrones estadísticos.

Una desviación estadística **no implica por sí misma una causa clínica o epidemiológica**.

### Visualización

Los resultados pueden representarse mediante gráficos interactivos que permiten explorar diferentes dimensiones de los datos.

---

## Evaluación experimental de modelos

Cuando la estructura y cobertura de los datos lo permiten, SaludData STEM incorpora experimentación con modelos de pronóstico.

El proceso general comprende:

```text
Datos históricos
      ↓
Preparación
      ↓
Selección de variables
      ↓
Construcción del conjunto experimental
      ↓
Entrenamiento
      ↓
Predicción
      ↓
Evaluación
      ↓
Interpretación
```

La experimentación con modelos tiene una finalidad **académica y exploratoria**.

Los resultados no deben interpretarse como diagnósticos, recomendaciones clínicas o pronósticos oficiales de salud pública.

---

## Criterios metodológicos

El proyecto busca mantener una aproximación reproducible al tratamiento y análisis de los datos.

### Calidad de los datos

Se consideran aspectos como:

- Valores faltantes.
- Registros duplicados.
- Tipos de datos.
- Consistencia de variables.
- Valores extremos.
- Cobertura temporal.
- Granularidad.
- Cambios en las fuentes.

### Interpretación

Los resultados deben analizarse dentro del contexto de los datos utilizados.

Una asociación estadística, correlación o tendencia observada **no constituye evidencia suficiente de causalidad**.

### Uso responsable

La plataforma tiene finalidad académica, educativa y exploratoria.

No está diseñada para sustituir sistemas oficiales de información, procesos de vigilancia epidemiológica ni valoración médica profesional.

---

## Limitaciones

Los resultados de SaludData STEM están condicionados por las características de las fuentes utilizadas.

Entre las principales limitaciones se encuentran:

- Disponibilidad variable de los conjuntos de datos.
- Diferencias en cobertura temporal.
- Cambios en las fuentes originales.
- Valores faltantes.
- Limitaciones de granularidad.
- Posibles sesgos presentes en los datos.
- Restricciones para realizar determinados análisis predictivos.
- Dependencia de la calidad de la información pública disponible.

Por esta razón, los resultados deben interpretarse como **evidencia exploratoria derivada de los datos disponibles**.

---

## Reproducibilidad

Uno de los principios del proyecto es favorecer la posibilidad de repetir y revisar los procesos de análisis.

Para ello se busca conservar:

```text
Fuente de datos
      +
Fecha de consulta
      +
Código
      +
Dependencias
      +
Transformaciones
      +
Parámetros
      +
Resultados
```

La reproducibilidad permite que estudiantes, docentes, investigadores y desarrolladores puedan revisar el proceso y realizar nuevas experimentaciones sobre los datos.

---

## Proyección académica

SaludData STEM puede evolucionar hacia una herramienta educativa y experimental que integre:

```text
Datos abiertos
      +
Ciencia de datos
      +
Salud pública
      +
Educación STEM
```

Entre sus posibles líneas de evolución se encuentran:

- Incorporación de nuevas fuentes de datos.
- Ampliación de indicadores.
- Nuevos métodos de análisis exploratorio.
- Evaluación de diferentes modelos.
- Incorporación de nuevos recursos de visualización.
- Desarrollo de actividades educativas.
- Fortalecimiento de experiencias prácticas con datos reales.
- Promoción de la participación de jóvenes mujeres en áreas STEM.

El proyecto parte de una idea central:

> **Los datos abiertos pueden convertirse en un recurso para aprender, investigar, formular preguntas y construir conocimiento.**

---

## Referencias

Las referencias deben priorizar las fuentes institucionales, metodológicas y tecnológicas utilizadas durante el desarrollo del proyecto.

### Fuentes institucionales

- Secretaría Distrital de Salud de Bogotá D.C.
- Plataformas oficiales de datos abiertos utilizadas por el proyecto.
- Conjuntos de datos empleados en los análisis.

### Tecnologías y herramientas

- Python
- Flask
- Pandas
- Scikit-learn
- Plotly
- CKAN

Las fuentes específicas utilizadas para cada análisis deben conservarse para facilitar la trazabilidad y reproducibilidad del trabajo.

---

## Colaboración

SaludData STEM es un proyecto de carácter académico y tecnológico que puede evolucionar mediante la colaboración, revisión y aportes de la comunidad.

### Leon, E.

[Leon, E. — GitHub](https://github.com/eduardoleon9010?tab=repositories)

Perfil y repositorios:

https://github.com/eduardoleon9010?tab=repositories

---

## Licencia

Este proyecto se presenta con fines **académicos, educativos y de investigación**.

El uso, modificación o distribución del código debe respetar las condiciones de las dependencias utilizadas y las licencias correspondientes.

Los datos utilizados por SaludData STEM pertenecen a sus respectivas fuentes de origen y deben utilizarse de acuerdo con las condiciones establecidas por dichas fuentes.

---

<div align="center">

### SaludData STEM

**Datos abiertos · Ciencia de datos · Salud pública · Educación STEM**

<br>

> **Convertir datos abiertos en información comprensible, reproducible y responsable.**

<br>

[Repositorio](https://github.com/leonsj12/SaludData_STEM) · [Aplicación en línea](https://saluddata-stem.onrender.com) · [Leon, E.](https://github.com/eduardoleon9010?tab=repositories)

<br><br>

**SaludData STEM V2.3**

</div>

