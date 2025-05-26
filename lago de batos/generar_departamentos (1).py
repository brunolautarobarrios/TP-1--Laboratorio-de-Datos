import pandas as pd

# Ruta al archivo
ruta_archivo = "C:/Users/2013b/OneDrive/Documentos/data science/segundo año/laboratorio de datos/tp1/establecimientos_educativos.xlsx"

# Cargar datos a partir de la fila 14 (index 13), sin encabezados
df = pd.read_excel(ruta_archivo, header=None, skiprows=13)

# Seleccionar columnas por posición: 
# - Columna 4 → ID depto
# - Columna 5 → nombre depto
# - Columna 2 → nombre provincia
df_departamentos = df[[4, 5, 2]].dropna().drop_duplicates().copy()

# Renombrar columnas
df_departamentos.columns = ['dpto_id', 'nombre_departamento', 'provincia']

# Asegurar que el ID quede como string con ceros (ej: 02007)
df_departamentos['dpto_id'] = df_departamentos['dpto_id'].astype(str).str.zfill(5)

# Guardar CSV
df_departamentos.to_csv("departamentos.csv", index=False)
print("✅ Archivo 'departamentos.csv' generado correctamente con ID numérico.")