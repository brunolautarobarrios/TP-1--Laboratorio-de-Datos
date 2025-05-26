# Limpieza y procesamiento de Establecimientos Educativos - Modalidad Común

import pandas as pd
import os

# Ruta al archivo original de Establecimientos Educativos (completar antes de ejecutar)
ruta_excel_original = "C:/Users/2013b/OneDrive/Documentos/data science/segundo año/laboratorio de datos/tp1/establecimientos"  # ← COMPLETAR con ruta absoluta del archivo Excel

# Lectura del archivo original, salteando encabezados y forzando tipo de localidad como string
establecimientos = pd.read_excel(
    ruta_excel_original,
    skiprows=6,
    dtype={"Código de localidad": str}
)

# Simplificación de las columnas de modalidad
modalidades = ['Común', 'Especial', 'Adultos', 'Artística', 'Hospitalaria', 'Intercultural', 'Encierro']
establecimientos["Modalidad"] = establecimientos[modalidades].apply(
    lambda fila: ', '.join([mod for mod in modalidades if fila[mod] == 1]),
    axis=1
)
establecimientos.drop(columns=modalidades, inplace=True)

# Filtro de establecimientos con modalidad "Común"
establecimientos_comunes = establecimientos[establecimientos["Modalidad"] == "Común"][[
    "Cueanexo",
    "Nivel inicial - Jardín maternal",
    "Nivel inicial - Jardín de infantes",
    "Primario",
    "Secundario",
    "Secundario - INET",
    "SNU",
    "SNU - INET"
]]

# Normalización de valores vacíos en las columnas categóricas
columnas_cat = [
    "Nivel inicial - Jardín maternal",
    "Nivel inicial - Jardín de infantes",
    "Primario",
    "Secundario",
    "Secundario - INET",
    "SNU",
    "SNU - INET"
]

establecimientos_comunes[columnas_cat] = establecimientos_comunes[columnas_cat].replace(r'^\s*$', pd.NA, regex=True)
establecimientos_comunes[columnas_cat] = establecimientos_comunes[columnas_cat].fillna(0).astype(int)

# Combinación de columnas
establecimientos_comunes["Secundario"] = (
    (establecimientos_comunes["Secundario"] == 1) | (establecimientos_comunes["Secundario - INET"] == 1)
).astype(int)

establecimientos_comunes["Terciario"] = (
    (establecimientos_comunes["SNU"] == 1) | (establecimientos_comunes["SNU - INET"] == 1)
).astype(int)

# Eliminación de columnas combinadas
establecimientos_comunes.drop(columns=["Secundario - INET", "SNU", "SNU - INET"], inplace=True)

# Renombrado de columnas
establecimientos_comunes.columns = [
    "id_establecimiento",
    "jardin_maternal",
    "jardin_infantes",
    "primario",
    "secundario",
    "terciario"
]

# Exportación a CSV
carpeta_output = "DataSets Limpios"
os.makedirs(carpeta_output, exist_ok=True)

ruta_csv_comunes = os.path.join(carpeta_output, "establecimientos_educativos_comunes.csv")
establecimientos_comunes.to_csv(ruta_csv_comunes, index=False, encoding='utf-8')

print("✅ Archivo generado correctamente en:", ruta_csv_comunes)
