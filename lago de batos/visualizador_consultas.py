import pandas as pd
import duckdb
from tabulate import tabulate

# Cargar CSV
carpeta = 'C:/Users/Maru/Desktop/bruno/facu/1C 2025/labo datos/lago de batos/'

departamentos = pd.read_csv(carpeta + 'departamentosNUEVO.csv')
bibliotecas = pd.read_csv(carpeta + 'bibliotecas_populares_limpio.csv')
nivel_educativo = pd.read_csv(carpeta + 'nivel_educativo_por_departamento (1).csv')
establecimientos = pd.read_csv(carpeta + 'establecimientos_educativos_limpia.csv')

# Conexión a DuckDB
con = duckdb.connect()
con.register('departamentos', departamentos)
con.register('bibliotecas', bibliotecas)
con.register('nivel_educativo', nivel_educativo)
con.register('establecimientos', establecimientos)

# Función para mostrar tabla y exportar si se desea
def mostrar_tabla(sql, descripcion, nombre_csv=None, redondear_floats=False):
    print(f'\n🟡 {descripcion}\n')
    df = con.execute(sql).df()

    if redondear_floats:
        float_cols = df.select_dtypes(include='float')
        df[float_cols.columns] = float_cols.round(2)

    if df.empty:
        print("⚠️ No se encontraron resultados.")
    else:
        print(tabulate(df.head(30), headers='keys', tablefmt='fancy_grid', showindex=False))

        exportar = input("\n¿Querés exportar esta tabla como CSV? (s/n): ").strip().lower()
        if exportar == 's' and nombre_csv:
            df.to_csv(carpeta + nombre_csv, index=False)
            print(f"✅ Archivo guardado como: {carpeta + nombre_csv}")

# Diccionario de consultas
consultas = {
    "1": {
        "descripcion": "Cantidad de Bibliotecas Populares por Provincia",
        "sql": """
            SELECT d.provincia, COUNT(*) AS cantidad_bp
            FROM bibliotecas b
            JOIN departamentos d ON b.id_departamento = d.id_depto
            GROUP BY d.provincia
            ORDER BY cantidad_bp DESC
        """,
        "archivo": "bp_por_provincia.csv"
    },
    "2": {
        "descripcion": "Cantidad de EE comunes por Provincia",
        "sql": """
            SELECT provincia, COUNT(*) AS cantidad_ee_comun
            FROM establecimientos
            WHERE modalidad_comun = 1
            GROUP BY provincia
            ORDER BY cantidad_ee_comun DESC
        """,
        "archivo": "ee_comun_por_provincia.csv"
    },
    "3": {
        "descripcion": "Cantidad de EE por Nivel Educativo y Provincia",
        "sql": """
            SELECT d.provincia,
                   SUM(n.jardin_maternal) AS jardin_maternal,
                   SUM(n.jardin_infante) AS jardin_infante,
                   SUM(n.primaria) AS primaria,
                   SUM(n.secundaria) AS secundaria,
                   SUM(n.terciario) AS terciario
            FROM nivel_educativo n
            JOIN departamentos d ON n.id_departamento = d.id_depto
            GROUP BY d.provincia
            ORDER BY primaria DESC
        """,
        "archivo": "ee_por_nivel_y_provincia.csv"
    },
    "4": {
        "descripcion": "Cantidad de EE comunes y BP por Departamento",
        "sql": """
            SELECT d.provincia, d.nombre_depto,
                   COUNT(DISTINCT e.id_establecimiento) FILTER (WHERE e.modalidad_comun = 1) AS ee_comun,
                   COUNT(DISTINCT b.id_biblioteca) AS cantidad_bp
            FROM departamentos d
            LEFT JOIN establecimientos e ON d.id_depto = e.id_depto
            LEFT JOIN bibliotecas b ON d.id_depto = b.id_departamento
            GROUP BY d.provincia, d.nombre_depto
            ORDER BY ee_comun DESC, cantidad_bp DESC
        """,
        "archivo": "ee_bp_por_departamento.csv"
    },
    "5": {
        "descripcion": "BP y EE comunes por cada 1000 habitantes (por departamento)",
        "sql": """
            SELECT d.provincia, d.nombre_depto,
                   COUNT(DISTINCT b.id_biblioteca) AS cantidad_bp,
                   SUM(CASE WHEN e.modalidad_comun = 1 THEN 1 ELSE 0 END) AS cantidad_ee_comun,
                   n.poblacion_total,
                   ROUND(COUNT(DISTINCT b.id_biblioteca) * 1000.0 / n.poblacion_total, 2) AS bp_cada_1000,
                   ROUND(SUM(CASE WHEN e.modalidad_comun = 1 THEN 1 ELSE 0 END) * 1000.0 / n.poblacion_total, 2) AS ee_cada_1000
            FROM departamentos d
            LEFT JOIN bibliotecas b ON b.id_departamento = d.id_depto
            LEFT JOIN establecimientos e ON e.id_depto = d.id_depto
            JOIN nivel_educativo n ON d.id_depto = n.id_departamento
            GROUP BY d.provincia, d.nombre_depto, n.poblacion_total
            ORDER BY bp_cada_1000 DESC
        """,
        "archivo": "bp_ee_por_mil_habitantes.csv",
        "redondear": True
    },
    "6": {
        "descripcion": "Dominio de email más frecuente por Provincia (BP)",
        "sql": """
            SELECT provincia, dominio_email
            FROM (
                SELECT d.provincia, b.dominio_email,
                       COUNT(*) AS cantidad,
                       ROW_NUMBER() OVER (PARTITION BY d.provincia ORDER BY COUNT(*) DESC) AS orden
                FROM bibliotecas b
                JOIN departamentos d ON b.id_departamento = d.id_depto
                GROUP BY d.provincia, b.dominio_email
            ) t
            WHERE orden = 1
            ORDER BY provincia
        """,
        "archivo": "dominio_email_frecuente_por_provincia.csv"
    }
}

# Menú interactivo
def mostrar_menu():
    while True:
        print("\n📊 MENÚ DE CONSULTAS DISPONIBLES:")
        for key in sorted(consultas.keys()):
            print(f"{key}. {consultas[key]['descripcion']}")
        print("0. Salir")

        opcion = input("\nSeleccioná una opción: ").strip()

        if opcion == "0":
            print("👋 Fin del programa.")
            break
        elif opcion in consultas:
            consulta = consultas[opcion]
            mostrar_tabla(
                sql=consulta["sql"],
                descripcion=consulta["descripcion"],
                nombre_csv=consulta["archivo"],
                redondear_floats=consulta.get("redondear", False)
            )
        else:
            print("❌ Opción inválida. Probá otra vez.")

# Ejecutar el menú
mostrar_menu()
