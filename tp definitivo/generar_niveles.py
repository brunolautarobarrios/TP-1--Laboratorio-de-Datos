import pandas as pd

# Diccionario con los niveles y sus nombres legibles (IDs corregidos)
niveles_dict = {
    "jardin_maternal": "Jardín maternal",
    "jardin_infante": "Jardín de infantes",
    "primario": "Primario",
    "secundario": "Secundario",
    "secundario_inet": "Secundario - INET",
    "snu": "SNU",
    "snu_inet": "SNU - INET",
    "snu_cursos": "SNU - Cursos"
}

# Convertir a DataFrame
df_niveles = pd.DataFrame(list(niveles_dict.items()), columns=["id_nivel", "nombre_nivel"])

# Guardar archivo CSV
ruta_salida = "C:/Users/2013b/OneDrive/Documentos/data science/segundo año/laboratorio de datos/tp1/niveles.csv"
df_niveles.to_csv(ruta_salida, index=False)

print("✅ Archivo 'niveles.csv' generado correctamente.")