import sys
from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsVectorLayer,
    QgsFeatureRequest
)
from qgis.utils import iface
import psycopg2
from shapely import wkt as shapely_wkt
import geopandas as gpd

# Configurações do banco de dados PostgreSQL
db_params = {
    'host': 'localhost',
    'user': 'iuri',
    'dbname': 'bdgd',
    'password': 'aa11bb22'
}

# Inicializar a aplicação QGIS
QgsApplication.setPrefixPath(r"C:\Program Files\QGIS 3.36.2\bin", True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Carregar o projeto e o layer
project = QgsProject.instance()
project.read('C:/Users/Lucas/Desktop/ARQUIVOs_DE_TERCEIROS/acess_bdgd.qgz')
layer = QgsProject.instance().mapLayersByName('ramlig')[0]


# Função para converter WKT para coordenadas (latitude e longitude)
def wkt_to_lat_lon(wkt):
    # Converter WKT para geometria
    geom = shapely_wkt.loads(wkt)

    # Criar um GeoDataFrame
    gdf = gpd.GeoDataFrame(geometry=[geom], crs='EPSG:4326')

    # Extrair coordenadas
    lat, lon = gdf.geometry.y[0], gdf.geometry.x[0]

    return lat, lon


# Conectar ao banco de dados PostgreSQL e obter códigos
conn = psycopg2.connect(**db_params)
cur = conn.cursor()
cur.execute("SELECT DISTINCT pn_con_2 FROM ramlig;")
codigos = cur.fetchall()

# Armazenar resultados
resultados = []

for codigo_tuple in codigos:
    codigo = codigo_tuple[0]

    # Filtrar o layer usando o código
    request = QgsFeatureRequest().setFilterExpression(f'"COD_ID" = \'{codigo}\'')
    for feature in layer.getFeatures(request):
        geom = feature.geometry().asWkt()
        lat, lon = wkt_to_lat_lon(geom)
        resultados.append((codigo, lat, lon))

# Fechar a aplicação QGIS
qgs.exitQgis()

# Conectar ao banco de dados para armazenar os resultados
conn = psycopg2.connect(**db_params)
cur = conn.cursor()

# Criar uma tabela para armazenar os resultados (se não existir)
cur.execute("""
CREATE TABLE IF NOT EXISTS ramal_coordinates (
    codigo TEXT PRIMARY KEY,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);
""")

# Inserir os resultados na tabela
for resultado in resultados:
    cur.execute("""
    INSERT INTO ramal_coordinates (codigo, latitude, longitude)
    VALUES (%s, %s, %s)
    ON CONFLICT (codigo) DO UPDATE
    SET latitude = EXCLUDED.latitude,
        longitude = EXCLUDED.longitude;
    """, resultado)

# Commit e fechar a conexão
conn.commit()
cur.close()
conn.close()
