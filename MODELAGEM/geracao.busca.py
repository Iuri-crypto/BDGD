import psycopg2
import json

# Função para conectar ao PostgreSQL e executar a consulta
def export_to_geojson():
    # Parâmetros de conexão (substitua pelos dados do seu banco de dados)
    conn = psycopg2.connect(
        host='localhost',
        port = '5432',
        dbname = 'BDGD_2023_ENERGISA',
        user = 'iuri',
        password = 'aa11bb22'
    )

    # Definindo o cursor
    cursor = conn.cursor()

    # Consulta SQL para extrair os dados com geometria convertida para GeoJSON
    query = """
    SELECT shape
    FROM unsemt

    """

    # Executando a consulta
    cursor.execute(query)

    # Recuperando os resultados
    rows = cursor.fetchall()

    # Estrutura para armazenar os dados no formato GeoJSON
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    # Processando os dados e convertendo para GeoJSON
    for row in rows:
        pac = row[0]
        shape_geojson = json.loads(row[1])  # Convertendo o GeoJSON armazenado em texto para um dicionário

        # Criando o objeto Feature para cada linha de dados
        feature = {
            "type": "Feature",
            "geometry": shape_geojson,
            "properties": {
                "pac": pac
            }
        }
        geojson["features"].append(feature)

    # Salvando o GeoJSON em um arquivo
    with open('output.geojson', 'w') as f:
        json.dump(geojson, f, indent=4)

    # Fechando a conexão
    cursor.close()
    conn.close()

    print("GeoJSON exportado com sucesso para 'output.geojson'.")

# Executando a função
export_to_geojson()
