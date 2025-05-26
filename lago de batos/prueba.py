import pandas as pd
import duckdb
import os
from tabulate import tabulate

# Carpeta con barra final o usar os.path.join
carpeta = 'C:/Users/Maru/Desktop/bruno/facu/1C 2025/labo datos/lago de batos/'

# Cargar archivos

departamentos = pd.read_csv(carpeta + 'departamentosNUEVO.csv')
bibliotecas = pd.read_csv(carpeta + 'bibliotecas_populares_limpio.csv')
nivel_educativo_depto = pd.read_csv(carpeta + 'nivel_educativo_por_departamento (1).csv')
establecimientos = pd.read_csv(carpeta + 'establecimientos_educativos_limpia.csv')

# Crear conexión a DuckDB
con = duckdb.connect()

# Registrar tablas temporales
establecimientos = pd.read_csv(carpeta + 'establecimientos_educativos_limpia.csv')
con.register('establecimientos', establecimientos)
con.register('departamentos', departamentos)
con.register('bibliotecas', bibliotecas)
con.register('nivel_educativo_depto', nivel_educativo_depto)

#Cantidad de BP por provincia, ordenadas. ¿Para qué? 
#Saber dónde están concentradas las BP (culturalmente más ricas). Comparar con cantidad de EE en la misma provincia.

consulta_BP_por_provincia = '''SELECT d.provincia, COUNT(*) AS cantidad_bp
FROM bibliotecas b
JOIN departamentos d ON b.id_departamento = d.id_depto
GROUP BY d.provincia
ORDER BY cantidad_bp DESC
'''

BP_por_provincia = con.execute(consulta_BP_por_provincia).df()
#print(BP_por_provincia)

#Cantidad de EE comunes por provincia
#Para tener la visión educativa real (y comparable con BP). Distinguir provincias con más acceso educativo común.

consulta_EE_por_provincia = '''SELECT provincia, COUNT(*) AS cantidad_ee_comun
FROM establecimientos
WHERE modalidad_comun = 1
GROUP BY provincia
ORDER BY cantidad_ee_comun DESC
'''

EE_por_provincia = con.execute(consulta_EE_por_provincia).df()
#print(EE_por_provincia)

#Cantidad de EE por nivel educativo (por provincia)
#Saber qué provincias tienen más infraestructura educativa formal por nivel.

consulta_EE_por_nivel = '''SELECT d.provincia,
       SUM(n.jardin_maternal) AS jardin_maternal,
       SUM(n.jardin_infante) AS jardin_infante,
       SUM(n.primaria) AS primaria,
       SUM(n.secundaria) AS secundaria,
       SUM(n.terciario) AS terciario
FROM nivel_educativo_depto n
JOIN departamentos d ON n.id_departamento = d.id_depto
GROUP BY d.provincia
ORDER BY primaria DESC 
'''

EE_por_nivel = con.execute(consulta_EE_por_nivel).df()
#print(EE_por_nivel)

#EE comunes y BP por departamento (comparación local)
#Contrastar la oferta educativa y cultural en cada zona. 
#Detectar departamentos con desequilibrios (mucha EE y poca BP, o al revés).

consulta_EE_BP_por_depto = ''' SELECT d.provincia, d.nombre_depto,
       COUNT(DISTINCT e.id_establecimiento) FILTER (WHERE e.modalidad_comun = 1) AS ee_comun,
       COUNT(DISTINCT b.id_biblioteca) AS cantidad_bp
FROM departamentos d
LEFT JOIN establecimientos e ON d.id_depto = e.id_depto
LEFT JOIN bibliotecas b ON d.id_depto = b.id_departamento
GROUP BY d.provincia, d.nombre_depto
ORDER BY ee_comun DESC, cantidad_bp DESC
'''

#Relación BP y EE cada mil habitantes (normalizado por población)
#Detectar desigualdades ajustadas por población. Fundamental para un análisis territorial justo.

EE_BP_por_depto = con.execute(consulta_EE_BP_por_depto).df()
#print(EE_BP_por_depto)

consulta_BP_EE_cada_mil_hab = ''' SELECT d.provincia, d.nombre_depto,
       COUNT(DISTINCT b.id_biblioteca) AS cantidad_bp,
       SUM(CASE WHEN e.modalidad_comun = 1 THEN 1 ELSE 0 END) AS cantidad_ee_comun,
       n.poblacion_total,
       ROUND(COUNT(DISTINCT b.id_biblioteca) * 1000.0 / n.poblacion_total, 2) AS bp_cada_1000,
       ROUND(SUM(CASE WHEN e.modalidad_comun = 1 THEN 1 ELSE 0 END) * 1000.0 / n.poblacion_total, 2) AS ee_cada_1000
FROM departamentos d
LEFT JOIN bibliotecas b ON b.id_departamento = d.id_depto
LEFT JOIN establecimientos e ON e.id_depto = d.id_depto
JOIN nivel_educativo_depto n ON d.id_depto = n.id_departamento
GROUP BY d.provincia, d.nombre_depto, n.poblacion_total
ORDER BY ee_cada_1000 DESC
'''

BP_EE_cada_mil_hab = con.execute(consulta_BP_EE_cada_mil_hab).df()
#print(BP_EE_cada_mil_hab)

#Outliers: mucha BP con poca población
#Para detectar casos atípicos que podrían tener explicación cultural, histórica o política.

consulta_outliers = '''SELECT d.provincia, d.nombre_depto, COUNT(*) AS cantidad_bp, n.poblacion_total
FROM bibliotecas b
JOIN departamentos d ON b.id_departamento = d.id_depto
JOIN nivel_educativo_depto n ON d.id_depto = n.id_departamento
GROUP BY d.provincia, d.nombre_depto, n.poblacion_total
HAVING n.poblacion_total < 20000 AND COUNT(*) > 10
ORDER BY cantidad_bp DESC
'''

outliers = con.execute(consulta_outliers).df()
#print(outliers)

#Outliers 2:
#Buscar lo contrario — lugares con alta población y pocas BP
#Esto puede ayudar a detectar regiones desatendidas en términos culturales.

consulta_outliers2 = '''SELECT d.provincia, d.nombre_depto, COUNT(*) AS cantidad_bp, n.poblacion_total
FROM bibliotecas b
JOIN departamentos d ON b.id_departamento = d.id_depto
JOIN nivel_educativo_depto n ON d.id_depto = n.id_departamento
GROUP BY d.provincia, d.nombre_depto, n.poblacion_total
HAVING n.poblacion_total > 100000 AND COUNT(*) <= 1
ORDER BY n.poblacion_total DESC
'''

outliers2 = con.execute(consulta_outliers2).df()
#print(outliers2)

