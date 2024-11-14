import psycopg2
from psycopg2 import sql
from qgis.core import (
    QgsApplication,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsField,
    QgsPointXY,
    QgsCoordinateReferenceSystem,
    QgsVectorFileWriter,
)
from PyQt5.QtCore import QVariant

# Inicializando o QGIS
QgsApplication.setPrefixPath("C:/OSGeo4W/apps/qgis", True)  # Ajuste o caminho conforme a sua instalação
qgs = QgsApplication([], False)
qgs.initQgis()

# Parâmetros do banco de dados PostgreSQL
db_params = {
    "host": "localhost",
    "user": "iuri",
    "dbname": "bdgd_2023",
    "password": "aa11bb22"
}


# Função para buscar dados da base PostgreSQL
def fetch_data(query):
    try:
        conn = psycopg2.connect(
            host=db_params["host"],
            user=db_params["user"],
            dbname=db_params["dbname"],
            password=db_params["password"]
        )
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return []


# Consultas SQL
sql_query_1 = """
    SELECT u.cod_id, u.pac_1, u.pac_2, u.shape
    FROM untrmt u
    WHERE u.cod_id NOT IN (SELECT e.uni_tr_mt FROM eqtrmt e)
"""

sql_query_2 = """
    SELECT u.cod_id, u.pac_1, u.pac_2, u.shape
    FROM untrmt u
"""

# Buscar os dados das duas consultas SQL
data_blue = fetch_data(sql_query_1)  # Dados para a camada azul
data_yellow = fetch_data(sql_query_2)  # Dados para a camada amarela


# Função para criar camada a partir de dados
def create_layer_from_data(data, color, filename):
    # Definindo o CRS (Sistema de Referência de Coordenadas) EPSG:4326
    crs = QgsCoordinateReferenceSystem("EPSG:4326")
    layer = QgsVectorLayer("Point?crs=EPSG:4326", "TempLayer", "memory")

    # Adicionando o campo cod_id
    layer_data_provider = layer.dataProvider()
    layer_data_provider.addAttributes([
        QgsField("cod_id", QVariant.String),
        QgsField("pac_1", QVariant.String),
        QgsField("pac_2", QVariant.String)
    ])
    layer.updateFields()

    # Criar as feições a partir dos dados
    for row in data:
        cod_id, pac_1, pac_2, wkt = row


        # Converter WKT para geometria
        geom = QgsGeometry.fromWkt(wkt)

        if geom.isValid():
            feature = QgsFeature()
            feature.setGeometry(geom)
            feature.setAttributes([cod_id, pac_1, pac_2])
            layer_data_provider.addFeature(feature)

    # Salvar como arquivo
    QgsVectorFileWriter.writeAsVectorFormat(layer, filename, "UTF-8", layer.crs(), "ESRI Shapefile")

    # Aplicar a simbologia
    layer.setRenderer(QgsPointSymbol.createSimple({'color': color}))

    return layer


# Criando camadas para os pontos
layer_blue = create_layer_from_data(data_blue, 'blue', "blue_points.shp")
layer_yellow = create_layer_from_data(data_yellow, 'yellow', "yellow_points.shp")

# Adicionando as camadas ao QGIS
QgsProject.instance().addMapLayer(layer_blue)
QgsProject.instance().addMapLayer(layer_yellow)

# Salvar o projeto do QGIS
project_file = "output_project.qgz"
QgsProject.instance().write(project_file)

# Finalizando a aplicação QGIS
qgs.exitQgis()

print("Processamento concluído!")
