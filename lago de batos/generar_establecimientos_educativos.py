import pandas as pd
from pathlib import Path

# Ruta del archivo original
archivo_excel = Path("C:/Users/2013b/OneDrive/Documentos/data science/segundo año/laboratorio de datos/tp1/establecimientos_educativos.xlsx")

# Leer el archivo Excel, saltando las primeras 11 filas (ajusta si es necesario)
df = pd.read_excel(archivo_excel, skiprows=11, dtype={'Código de localidad': str})

# Imprime los nombres de las columnas para verificar (puedes comentar esta línea luego)
print(df.columns.tolist())

# Lista de columnas de modalidad (ajusta si los nombres no coinciden exactamente)
modalidades = ['Común', 'Especial', 'Adultos', 'Artística', 'Hospitalaria', 'Intercultural', 'Encierro']

# Unificar columnas de modalidad en una sola columna "Modalidad"
df['Modalidad'] = df[modalidades].apply(lambda row: ', '.join([col for col in modalidades if row.get(col, 0) == 1]), axis=1)

# Eliminar las columnas originales de modalidad
df.drop(columns=modalidades, inplace=True)

# Guardar el DataFrame limpio
output_path = Path("C:/Users/2013b/OneDrive/Documentos/data science/segundo año/laboratorio de datos/tp1/establecimientos_educativos.csv")
df.to_csv(output_path, index=False, encoding="utf-8")
print("Archivo guardado: establecimientos_educativos.csv")