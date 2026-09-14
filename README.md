<div align="center">

<img src="assets/banner-saluddata-stem.png" alt="SaludData STEM — Explorador interactivo de datos abiertos de salud pública" width="100%">

<br>

# SaludData STEM

### Explorador interactivo de datos abiertos de salud pública

<p>
Herramienta web desarrollada para consultar, validar, transformar, analizar y visualizar información abierta relacionada con salud pública mediante técnicas de ciencia de datos.
</p>

<br>

<a href="https://saluddata-stem.onrender.com">Aplicación en línea</a>
&nbsp;&nbsp;·&nbsp;&nbsp;
<a href="https://github.com/leonsj12/SaludData_STEM">Código fuente</a>

<br><br>

[![Estado](https://img.shields.io/badge/Estado-MVP%20funcional-16a34a?style=for-the-badge)](https://saluddata-stem.onrender.com)
[![Versión](https://img.shields.io/badge/Versión-2.3-2563eb?style=for-the-badge)](https://github.com/leonsj12/SaludData_STEM)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Web%20App-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

<br><br>

<img src="https://skillicons.dev/icons?i=python,flask,pandas,sklearn,plotly,git,github&theme=light" alt="Tecnologías: Python, Flask, Pandas, Scikit-learn, Plotly, Git y GitHub">

<br><br>

> **Convertir datos abiertos en información comprensible, reproducible y responsable.**

</div>

---

## Índice

- [Descripción](#descripción)
- [Propósito](#propósito)
- [Características principales](#características-principales)
- [Fuentes de datos](#fuentes-de-datos)
- [Flujo de trabajo](#flujo-de-trabajo)
- [Arquitectura del sistema](#arquitectura-del-sistema)
- [Tecnologías utilizadas](#tecnologías-utilizadas)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Ejecución](#ejecución)
- [Dashboard](#dashboard)
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

**SaludData STEM V2.3** es un prototipo funcional de ciencia de datos orientado al análisis exploratorio de información abierta relacionada con mortalidad cardiovascular y respiratoria en Bogotá D.C.

La aplicación integra un flujo de trabajo para consultar, validar, transformar, analizar y visualizar datos abiertos. Cuando la granularidad y cobertura de la fuente lo permiten, también contempla evaluación experimental de modelos de pronóstico.

El proyecto busca transformar registros públicos en información comprensible y, al mismo tiempo, utilizar datos reales como medio para fortalecer experiencias educativas relacionadas con ciencia, tecnología, ingeniería y matemáticas (STEM), con especial interés en la participación de jóvenes mujeres.

---

## Propósito

La disponibilidad de datos abiertos representa una oportunidad para acercar la ciencia de datos a problemas reales.

SaludData STEM propone un entorno en el que los datos pueden recorrer un proceso analítico reproducible:

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

El propósito es facilitar la exploración de información pública desde una perspectiva técnica, educativa y responsable.

---

## Características principales

### Exploración y preparación

- Consulta de información abierta relacionada con salud pública.
- Validación de registros.
- Transformación y normalización de variables.
- Filtrado de información.
- Preparación de datos para análisis posteriores.

### Análisis exploratorio

- Estadística descriptiva.
- Distribución de variables.
- Indicadores descriptivos.
- Comparación de categorías.
- Exploración de tendencias.
- Identificación de desviaciones estadísticas.

### Análisis temporal

- Evolución de registros a través del tiempo.
- Comparación entre periodos.
- Exploración de variaciones.
- Identificación de comportamientos atípicos.

### Visualización

La aplicación utiliza visualizaciones interactivas para facilitar la exploración de los resultados y la interpretación de diferentes dimensiones de los datos.

### Evaluación experimental

Cuando las características de la fuente lo permiten, se evalúan experimentalmente modelos de pronóstico.

Los resultados de esta etapa tienen carácter académico y exploratorio.

---

## Fuentes de datos

El proyecto trabaja con información abierta relacionada con salud pública y mortalidad en Bogotá D.C.

Entre las fuentes utilizadas se encuentran conjuntos de datos publicados por la **Secretaría Distrital de Salud de Bogotá D.C.**

La propuesta contempla el uso de plataformas y servicios de datos abiertos, incluyendo mecanismos asociados con **CKAN**.

La interpretación de los resultados debe considerar la calidad, cobertura temporal, granularidad, valores faltantes y condiciones de producción de cada fuente.

---

## Flujo de trabajo

<div align="center">

```text
┌──────────────┐
│ Datos abiertos│
└──────┬───────┘
       ↓
┌──────────────┐
│  Validación  │
└──────┬───────┘
       ↓
┌──────────────┐
│Transformación│
└──────┬───────┘
       ↓
┌──────────────┐
│   Análisis   │
└──────┬───────┘
       ↓
┌──────────────┐
│Visualización │
└──────┬───────┘
       ↓
┌──────────────┐
│ Evaluación   │
└──────────────┘
```

</div>

---

## Arquitectura del sistema

La aplicación está desarrollada alrededor de Python y Flask e integra componentes destinados al tratamiento, análisis y visualización de los datos.

```text
                    FUENTES DE DATOS
                           │
                           ▼
                 ┌──────────────────┐
                 │ Adquisición /    │
                 │ Validación       │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Procesamiento    │
                 │ de datos         │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Análisis         │
                 │ exploratorio     │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Visualización    │
                 │ interactiva      │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Aplicación web   │
                 │ Flask            │
                 └──────────────────┘
```

---

## Tecnologías utilizadas

<div align="center">

| Python | Flask | Pandas |
|:---:|:---:|:---:|
| Lenguaje principal | Aplicación web | Manipulación de datos |

| Scikit-learn | Plotly | CKAN |
|:---:|:---:|:---:|
| Experimentación | Visualización | Datos abiertos |

</div>

<br>

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,flask,pandas,sklearn,git,github&theme=light" alt="Stack tecnológico">
</p>

---

## Estructura del proyecto

La organización exacta del repositorio debe mantenerse alineada con los archivos actualmente presentes en GitHub.

Como mínimo, el README utiliza el recurso visual:

```text
SaludData_STEM/
│
├── assets/
│   └── banner-saluddata-stem.png
│
└── README.md
```

Los demás componentes deben reflejar la estructura real del repositorio y no se enumeran aquí para evitar documentar archivos que no formen parte de la versión publicada.

---

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

---

## Ejecución

La ejecución local se realiza mediante la aplicación Flask:

```bash
python app.py
```

La aplicación desplegada puede consultarse en:

**[SaludData STEM — Aplicación en línea](https://saluddata-stem.onrender.com)**

---

## Dashboard

El dashboard constituye la interfaz de exploración de la información.

Su propósito es facilitar la transición entre los datos y los resultados mediante una experiencia interactiva:

```text
Datos
  │
  ├── Exploración
  │
  ├── Indicadores
  │
  ├── Visualización
  │
  ├── Análisis temporal
  │
  └── Evaluación experimental
```

---

## Análisis disponibles

### Estadística descriptiva

Caracterización inicial de los datos mediante medidas y distribuciones relevantes para las variables disponibles.

### Análisis temporal

Exploración de la evolución de los registros a través del tiempo y comparación entre periodos.

### Distribución de variables

Exploración de frecuencias, categorías y comportamiento de las variables disponibles.

### Desviaciones estadísticas

Identificación exploratoria de observaciones o periodos que se apartan de determinados patrones estadísticos.

Una desviación estadística no implica por sí misma una causa clínica o epidemiológica.

### Visualización interactiva

Representación gráfica de los resultados para facilitar la exploración y comprensión de los datos.

---

## Evaluación experimental de modelos

Cuando la granularidad y cobertura de la información lo permiten, el proyecto contempla la evaluación experimental de modelos de pronóstico.

El proceso general puede representarse como:

```text
Datos históricos
      ↓
Preparación
      ↓
Selección de variables
      ↓
Conjunto experimental
      ↓
Entrenamiento
      ↓
Predicción
      ↓
Evaluación
      ↓
Interpretación
```

Los resultados tienen carácter experimental y académico. No constituyen diagnósticos, recomendaciones clínicas ni pronósticos oficiales de salud pública.

---

## Criterios metodológicos

El proyecto considera diferentes aspectos antes de interpretar los resultados.

### Calidad de los datos

- Valores faltantes.
- Registros duplicados.
- Tipos de datos.
- Consistencia de variables.
- Valores extremos.
- Cobertura temporal.
- Granularidad.
- Cambios en las fuentes.

### Interpretación

Las tendencias, asociaciones y correlaciones encontradas deben interpretarse dentro del contexto de los datos utilizados.

Una asociación estadística no constituye evidencia suficiente de causalidad.

### Uso responsable

SaludData STEM es una herramienta académica, educativa y exploratoria. No sustituye sistemas oficiales de información, procesos de vigilancia epidemiológica ni valoración médica profesional.

---

## Limitaciones

Los resultados dependen de las características y calidad de las fuentes originales.

Entre las principales limitaciones se encuentran:

- Disponibilidad variable de los datos.
- Cobertura temporal limitada en determinadas fuentes.
- Cambios en los conjuntos publicados.
- Valores faltantes.
- Diferencias de granularidad.
- Posibles sesgos.
- Restricciones para determinados análisis predictivos.

Por estas razones, los resultados deben interpretarse como evidencia exploratoria derivada de los datos disponibles.

---

## Reproducibilidad

El proyecto busca favorecer la revisión y repetición de los procesos de análisis.

Para ello resulta relevante conservar:

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

---

## Proyección académica

SaludData STEM plantea una integración entre:

```text
Datos abiertos
      +
Ciencia de datos
      +
Salud pública
      +
Educación STEM
```

El proyecto puede continuar evolucionando mediante nuevas fuentes, indicadores, procedimientos de análisis, visualizaciones y experiencias educativas.

Uno de sus propósitos es utilizar información pública como punto de partida para aprender, investigar, formular preguntas y construir conocimiento.

---

## Referencias

### Fuentes institucionales

- Secretaría Distrital de Salud de Bogotá D.C.
- Plataformas oficiales de datos abiertos utilizadas por el proyecto.
- Conjuntos de datos empleados en los análisis.

### Tecnologías

- Python
- Flask
- Pandas
- Scikit-learn
- Plotly
- CKAN

Las referencias específicas de cada conjunto de datos deben conservarse de acuerdo con las condiciones establecidas por sus respectivas fuentes.

---

## Colaboración

SaludData STEM es un proyecto académico y tecnológico susceptible de evolución mediante revisión, colaboración y aportes.

### Leon, E.

<a href="https://github.com/eduardoleon9010?tab=repositories">
<img src="https://img.shields.io/badge/Leon%2C%20E.-Perfil%20y%20repositorios-181717?style=for-the-badge&logo=github&logoColor=white" alt="Leon, E. — Perfil de GitHub">
</a>

---

## Licencia

Este proyecto se presenta con fines académicos, educativos y de investigación.

El uso, modificación o distribución del código debe respetar las condiciones de las dependencias utilizadas y las licencias correspondientes.

Los datos utilizados pertenecen a sus respectivas fuentes de origen y deben utilizarse de acuerdo con las condiciones establecidas por dichas fuentes.

---

<div align="center">

<br>

**SaludData STEM**

*Datos abiertos · Ciencia de datos · Salud pública · Educación STEM*

<br>

[Repositorio](https://github.com/leonsj12/SaludData_STEM) · [Aplicación](https://saluddata-stem.onrender.com) · [Leon, E.](https://github.com/eduardoleon9010?tab=repositories)

<br><br>

**V2.3**

</div>


