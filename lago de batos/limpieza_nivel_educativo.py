import pandas as pd

# Ruta al archivo original
ruta_excel = "C:/Users/2013b/OneDrive/Documentos/data science/segundo año/laboratorio de datos/tp1/Poblacion_por_Edad_por_Departamento.xlsx"

# Leer el archivo, salteando encabezado y celdas no útiles (las primeras 12 filas)
df_raw = pd.read_excel(ruta_excel, skiprows=12, header=None)

# Eliminar filas vacías y resetear índice
df = df_raw.dropna(how='all').reset_index(drop=True)

# Lista para almacenar resultados
resultados = []

i = 0
while i < len(df):
    fila = df.iloc[i]
    
    # Buscar inicio de bloque con "AREA #"
    if isinstance(fila[1], str) and "AREA #" in fila[1]:
        id_departamento = fila[1].split("AREA #")[-1].strip()
        nombre_departamento = fila[2]
        
        # Avanzar hasta encontrar encabezado de subtabla
        i += 1
        while i < len(df) and not (df.iloc[i][1] == "Edad"):
            i += 1
        i += 1  # avanzar a la primera fila de datos
        
        # Inicializar contadores
        jardin_maternal = jardin_infante = primaria = secundaria = terciario = poblacion_total = 0
        
        # Recorrer subtabla
        while i < len(df):
            edad = df.iloc[i][1]
            casos = df.iloc[i][2]
            
            if isinstance(edad, str) and edad.strip().lower() == "total":
                poblacion_total = casos
                i += 1
                break

            if pd.api.types.is_number(edad):
                edad = int(edad)
                if edad in [0, 1, 2, 3]:
                    jardin_maternal += casos
                elif edad in [4, 5]:
                    jardin_infante += casos
                elif 6 <= edad <= 12:
                    primaria += casos
                elif 13 <= edad <= 18:
                    secundaria += casos
                elif 19 <= edad <= 50:
                    terciario += casos
            i += 1

        # Agregar resultado
        resultados.append({
            "id_departamento": id_departamento,
            "nombre_departamento": nombre_departamento,
            "jardin_maternal": jardin_maternal,
            "jardin_infante": jardin_infante,
            "primaria": primaria,
            "secundaria": secundaria,
            "terciario": terciario,
            "poblacion_total": poblacion_total
        })
    else:
        i += 1

# Crear DataFrame final
df_resultado = pd.DataFrame(resultados)

# Unir las comunas de CABA como un solo departamento
df_resultado.loc[df_resultado['nombre_departamento'].str.startswith('Comuna '), 'id_departamento'] = 2000
df_caba = df_resultado[df_resultado['id_departamento'] == 2000]
df_caba_sum = df_caba.drop(columns=['nombre_departamento']).sum(numeric_only=True)
df_caba_sum['id_departamento'] = 2000
df_caba_sum['nombre_departamento'] = 'Ciudad de Buenos Aires'
df_caba_final = pd.DataFrame([df_caba_sum])[df_resultado.columns]

# Reemplazar filas de CABA con la suma
df_resultado = df_resultado[df_resultado['id_departamento'] != 2000]
df_resultado = pd.concat([df_resultado, df_caba_final], ignore_index=True)

# Quitar columna redundante
df_resultado = df_resultado.drop(columns=["nombre_departamento"])

# Limpiar ceros a la izquierda en IDs
df_resultado['id_departamento'] = df_resultado['id_departamento'].astype(int)

# Exportar CSV
ruta_salida = "C:/Users/2013b/OneDrive/Documentos/data science/segundo año/laboratorio de datos/tp1/nivel_educativo_por_departamento.csv"
df_resultado.to_csv(ruta_salida, index=False)
print("✅ Archivo guardado como:", ruta_salida)
