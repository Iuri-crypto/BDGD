from qgis.core import QgsApplication, QgsProject, QgsVectorLayer, QgsRectangle
from qgis.gui import QgsMapCanvas
import psycopg2
import os
import subprocess
import time

# Inicializa a aplicação QGIS com interface gráfica
QgsApplication.setPrefixPath("C:/OSGEO4W/apps/qgis", True)
qgs = QgsApplication([], True)  # True ativa a interface gráfica
qgs.initQgis()

# Configurações de conexão ao banco de dados PostgreSQL
host = "localhost"
port = "5432"
dbname = "bdgd"
user = "iuri"
password = "aa11bb22"
schema = "public"  # Ajuste o esquema conforme necessário

# Nome do projeto
project_path = r"C:\Meu GitHub\Pesquisa_e_Dia_a_Dia\Pesquisa Perdas Não Técnicas\pythonProject\teste08.qgz"  # Altere o caminho conforme necessário

# Cria um novo projeto QGIS
project = QgsProject.instance()
project.setFileName(project_path)

# Cria uma instância do canvas do mapa
canvas = QgsMapCanvas()
canvas.setWindowTitle("QGIS Canvas")

# Conecta ao banco de dados PostgreSQL e carrega todas as camadas
try:
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cur = conn.cursor()
    # Consulta para listar tabelas com colunas de geometria no esquema especificado
    cur.execute(f"""
        SELECT f_table_name, f_geometry_column 
        FROM geometry_columns 
        WHERE f_table_schema = '{schema}';
    """)

    tables = cur.fetchall()

    for table_name, geom_column in tables:
        # Cria a string de conexão para o banco de dados PostgreSQL
        uri = f"dbname='{dbname}' host={host} port={port} user='{user}' password='{password}' key='id' table=\"{schema}\".\"{table_name}\" ({geom_column}) sql="
        layer = QgsVectorLayer(uri, table_name, "postgres")

        if layer.isValid():
            project.addMapLayer(layer)
            print(f"Camada '{table_name}' carregada com sucesso.")
        else:
            print(f"Erro ao carregar a camada '{table_name}'.")
            print(f"URI: {uri}")

    # Tenta carregar outras tabelas que não possuem colunas de geometria como tabelas simples
    cur.execute(f"""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = '{schema}'
        AND table_name NOT IN (SELECT f_table_name FROM geometry_columns WHERE f_table_schema = '{schema}');
    """)

    other_tables = cur.fetchall()

    for table_name, in other_tables:
        # Ignorar tabelas conhecidas que não possuem dados geoespaciais relevantes
        if table_name in ['geography_columns', 'geometry_columns', 'spatial_ref_sys']:
            continue

        uri = f"dbname='{dbname}' host={host} port={port} user='{user}' password='{password}' key='id' table=\"{schema}\".\"{table_name}\" sql="
        layer = QgsVectorLayer(uri, table_name, "postgres")

        if layer.isValid():
            project.addMapLayer(layer)
            print(f"Tabela '{table_name}' carregada com sucesso.")
        else:
            print(f"Erro ao carregar a tabela '{table_name}'.")
            print(f"URI: {uri}")

except Exception as e:
    print(f"Erro ao conectar ao banco de dados ou ao carregar as tabelas: {e}")
finally:
    if conn:
        cur.close()
        conn.close()

# Ativa todas as camadas uma por uma e ajusta o zoom para cada uma
root = project.layerTreeRoot()
extent = QgsRectangle()  # Inicializa o retângulo de extensão

for layer in project.mapLayers().values():
    # Torna a camada visível
    layer_tree_layer = root.findLayer(layer.id())
    if layer_tree_layer:
        layer_tree_layer.setItemVisibilityChecked(True)  # Torna a camada visível

    # Ajusta o zoom para a extensão da camada
    layer_extent = layer.extent()
    extent.combineExtentWith(layer_extent)  # Usa combineExtentWith para unir as extensões

    print(f"Camada '{layer.name()}' ativada.")

# Define a extensão total das camadas no canvas
canvas.setExtent(extent)
canvas.refresh()  # Atualiza o canvas para refletir a nova extensão

# Salva o projeto QGIS
project.write()

# Abre o projeto QGIS no QGIS Desktop
qgis_path = r"C:\Program Files\QGIS 3.38.2\bin\qgis-bin.exe"  # Altere o caminho conforme necessário

# Verifique se o caminho para o QGIS está correto
if not os.path.isfile(qgis_path):
    print(f"O caminho para o QGIS não está correto: {qgis_path}")
else:
    # Abre o projeto no QGIS
    process = subprocess.Popen([qgis_path, project_path])

    # Loop para manter o script ativo enquanto o QGIS estiver aberto
    while True:
        if process.poll() is not None:
            print("QGIS foi fechado.")
            break
        time.sleep(5)  # Espera por 5 segundos antes de verificar novamente

# Finaliza a aplicação QGIS
qgs.exitQgis()

print("Projeto salvo e QGIS iniciado.")
