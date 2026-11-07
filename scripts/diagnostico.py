"""
Diagnóstico rápido de SaludData STEM.

Sirve para comprobar que Python puede importar los módulos principales
y que los archivos Parquet locales, si existen, pueden abrirse.
"""

from app.services.local_data import get_summary

print("SALUDDATA STEM — DIAGNÓSTICO")
print("-" * 40)

for name, df in get_summary().items():
    print(f"{name:15} filas={len(df):>8} columnas={len(df.columns):>3}")

print("-" * 40)
print("Diagnóstico terminado.")
