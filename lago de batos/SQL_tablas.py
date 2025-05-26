# Autores: [Nombres del grupo]
# Descripción: Generación de consultas SQL del TP1 (Laboratorio de Datos 2025)
# Este script ejecuta las consultas pedidas en el TP usando DuckDB, con tablas ya cargadas.

import pandas as pd
import duckdb
from tabulate import tabulate

# Ruta base
carpeta = 'C:/Users/Maru/Desktop/bruno/facu/1C 2025/labo datos/lago de batos/'

# Cargar CSVs
departamentos = pd.read_csv(carpeta + 'departamentosNUEVO.csv')
bibliotecas = pd.read_csv(carpeta + 'bibliotecas_populares_limpio.csv')
nivel_educativo = pd.read_csv(carpeta + 'nivel_educativo_por_departamento (1).csv')
establecimientos = pd.read_csv(carpeta + 'establecimientos_educativos_limpia.csv')
ee_comunes = pd.read_csv(carpeta + 'niveles_establecimientos_comunes.csv')

# Conexión DuckDB
con = duckdb.connect()
con.register("departamentos", departamentos)
con.register("bibliotecas", bibliotecas)
con.register("nivel_educativo", nivel_educativo)
con.register("establecimientos", establecimientos)
con.register("ee_comunes", ee_comunes)

# Función para mostrar y exportar
def mostrar_y_exportar(sql, descripcion, archivo=None):
    print(f"\n🔹 {descripcion}\n")
    df = con.execute(sql).df()
    print(tabulate(df.head(30), headers='keys', tablefmt='fancy_grid', showindex=False))
    if archivo:
        df.to_csv(carpeta + archivo, index=False)
        print(f"📁 Exportado a: {archivo}")

# Consulta i (versión con nombres de columnas más cortos para consola)
sql_i = """
    SELECT 
        d.provincia AS Prov,
        d.nombre_depto AS Dpto,
        SUM(ec."Nivel inicial - Jardín de infantes") + SUM(ec."Nivel inicial - Jardín Maternal") AS Jard,
        ne.jardin_infante + ne.jardin_maternal AS Pob_Jard,
        SUM(ec.primario) AS Prim,
        ne.primaria AS Pob_Prim,
        SUM(ec.secundario) AS Sec,
        ne.secundaria AS Pob_Sec
    FROM ee_comunes ec
    JOIN establecimientos e ON ec.id_establecimiento = e.id_establecimiento
    JOIN departamentos d ON e.id_depto = d.id_depto
    JOIN nivel_educativo ne ON d.id_depto = ne.id_departamento
    GROUP BY d.provincia, d.nombre_depto, ne.jardin_infante, ne.jardin_maternal, ne.primaria, ne.secundaria
    ORDER BY d.provincia ASC, Prim DESC
"""
mostrar_y_exportar(sql_i, "Consulta I - EE por nivel y población (nombres cortos)", "dfi.csv")


# Consulta ii
sql_ii = """
    SELECT 
        d.provincia AS Provincia,
        d.nombre_depto AS Departamento,
        COUNT(b.id_biblioteca) AS "Cantidad BP fundadas desde 1950"
    FROM bibliotecas b
    JOIN departamentos d ON b.id_departamento = d.id_depto
    WHERE b.año_fundacion >= 1950
    GROUP BY d.provincia, d.nombre_depto
    ORDER BY d.provincia, "Cantidad BP fundadas desde 1950" DESC
"""
mostrar_y_exportar(sql_ii, "Consulta II - BP fundadas desde 1950", "dfii.csv")

# Consulta iii
sql_iii = """
    SELECT 
        d.provincia AS Provincia,
        d.nombre_depto AS Departamento,
        COUNT(DISTINCT b.id_biblioteca) AS Cant_BP,
        COUNT(DISTINCT e.id_establecimiento) FILTER (WHERE e.modalidad_comun = 1) AS Cant_EE,
        ne.poblacion_total AS Poblacion
    FROM departamentos d
    LEFT JOIN bibliotecas b ON b.id_departamento = d.id_depto
    LEFT JOIN establecimientos e ON e.id_depto = d.id_depto
    JOIN nivel_educativo ne ON d.id_depto = ne.id_departamento
    GROUP BY d.provincia, d.nombre_depto, ne.poblacion_total
    ORDER BY Cant_EE DESC, Cant_BP DESC, d.provincia, d.nombre_depto
"""
mostrar_y_exportar(sql_iii, "Consulta III - BP, EE y población por departamento", "dfiii.csv")

# Consulta iv
sql_iv = """
    SELECT provincia, departamento, dominio_email AS "Dominio más frecuente"
    FROM (
        SELECT 
            d.provincia,
            d.nombre_depto AS departamento,
            b.dominio_email,
            COUNT(*) AS cantidad,
            ROW_NUMBER() OVER (PARTITION BY d.nombre_depto ORDER BY COUNT(*) DESC) AS orden
        FROM bibliotecas b
        JOIN departamentos d ON b.id_departamento = d.id_depto
        WHERE b.dominio_email IS NOT NULL
        GROUP BY d.provincia, d.nombre_depto, b.dominio_email
    ) t
    WHERE orden = 1
    ORDER BY departamento
"""
mostrar_y_exportar(sql_iv, "Consulta IV - Dominio más frecuente por departamento", "dfiv.csv")
