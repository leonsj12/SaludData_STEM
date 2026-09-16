# Decisiones técnicas

## 1. Flask

Se utiliza Flask porque permite enseñar una arquitectura web de Python
sin ocultar demasiado funcionamiento.

## 2. pandas

Se utiliza pandas como herramienta central de manipulación tabular.

## 3. Parquet

Se utiliza para separar los archivos fuente de las versiones preparadas
para análisis.

## 4. Actualización independiente

`python scripts\update_data.py`

La actualización es explícita y reproducible.

## 5. Dashboard liviano

El navegador solicita un resumen pequeño mediante `/api/summary`.

No recibe automáticamente todo el CSV.

## 6. Modularidad

Cada componente tiene una responsabilidad principal.

Esto facilita:

- mantenimiento;
- pruebas;
- enseñanza;
- sustitución de componentes;
- futuras ampliaciones.

## 7. Interpretación responsable

El proyecto es exploratorio y educativo. No realiza diagnóstico,
tratamiento ni predicción clínica individual.
