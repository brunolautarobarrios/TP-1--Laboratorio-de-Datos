import pandas as pd
import matplotlib.pyplot as plt

# ---------------- CONFIGURACIÓN ---------------- #
carpeta = 'C:/Users/Maru/Desktop/bruno/facu/1C 2025/labo datos/lago de batos/'

# Cargar datos limpios
bp = pd.read_csv(carpeta + 'bibliotecas_populares_limpio.csv')
ee = pd.read_csv(carpeta + 'establecimientos_educativos_limpia.csv')
deptos = pd.read_csv(carpeta + 'departamentosNUEVO.csv')
niveles = pd.read_csv(carpeta + 'niveles_establecimientos_comunes.csv')
poblacion = pd.read_csv(carpeta + 'nivel_educativo_por_departamento (1).csv')

# ---------------- i) Cantidad de BP por provincia ---------------- #
bp_merged = bp.merge(deptos, left_on='id_departamento', right_on='id_depto')
bp_count = bp_merged.groupby('provincia').size().sort_values(ascending=False)

plt.figure(figsize=(12, 6))
bp_count.plot(kind='bar')
plt.title('Cantidad de Bibliotecas Populares por provincia')
plt.ylabel('Cantidad de BP')
plt.xlabel('Provincia')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

# ---------------- ii) EE por población por nivel educativo ---------------- #
niveles_merge = niveles.merge(ee[['id_establecimiento', 'id_depto']], on='id_establecimiento')
niveles_dept = niveles_merge.groupby('id_depto')[['Nivel inicial - Jardín de infantes', 'Primario', 'Secundario']].sum().reset_index()
niveles_dept = niveles_dept.merge(poblacion[['id_departamento', 'jardin_infante', 'primaria', 'secundaria']], 
                                  left_on='id_depto', right_on='id_departamento')

plt.figure(figsize=(10, 6))
plt.scatter(niveles_dept['jardin_infante'], niveles_dept['Nivel inicial - Jardín de infantes'], color='orange', label='Jardín')
plt.scatter(niveles_dept['primaria'], niveles_dept['Primario'], color='blue', label='Primario')
plt.scatter(niveles_dept['secundaria'], niveles_dept['Secundario'], color='green', label='Secundario')
plt.title('Cantidad de EE vs Población por nivel educativo')
plt.xlabel('Población por nivel')
plt.ylabel('Cantidad de EE')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# ---------------- iii) Boxplot de EE comunes por provincia ---------------- #
ee_comunes = ee[ee['modalidad_comun'] == 1]
ee_count = ee_comunes.groupby(['provincia', 'id_depto']).size().reset_index(name='cant_ee')
orden_provincias = ee_count.groupby('provincia')['cant_ee'].median().sort_values().index.tolist()

plt.figure(figsize=(12, 6))
ee_count['provincia'] = pd.Categorical(ee_count['provincia'], categories=orden_provincias, ordered=True)
ee_count.boxplot(by='provincia', column='cant_ee', grid=False, rot=90)
plt.title('Distribución de EE comunes por provincia')
plt.suptitle('')
plt.ylabel('Cantidad de EE comunes')
plt.tight_layout()
plt.show()

# ---------------- iv) Relación entre BP y EE por cada 1000 habitantes ---------------- #
bp_count = bp.groupby('id_departamento').size().reset_index(name='cant_bp')
ee_count_total = ee_comunes.groupby('id_depto').size().reset_index(name='cant_ee')

relacion = poblacion[['id_departamento', 'poblacion_total']].merge(
    bp_count, on='id_departamento', how='left').merge(
    ee_count_total, left_on='id_departamento', right_on='id_depto', how='left').fillna(0)

relacion['bp_1000'] = relacion['cant_bp'] * 1000 / relacion['poblacion_total']
relacion['ee_1000'] = relacion['cant_ee'] * 1000 / relacion['poblacion_total']

plt.figure(figsize=(8, 6))
plt.scatter(relacion['bp_1000'], relacion['ee_1000'], alpha=0.7)
plt.xlabel('BP cada 1000 habitantes')
plt.ylabel('EE comunes cada 1000 habitantes')
plt.title('Relación entre BP y EE cada 1000 habitantes')
plt.grid(True)
plt.tight_layout()
plt.show()
