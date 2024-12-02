import psycopg2

# Dados de conexão com o banco de dados
host = 'localhost'
port = '5432'
dbname = 'BDGD_2023_ENERGISA'
user = 'iuri'
password = 'aa11bb22'

# Conexão com o banco de dados
try:
    # Estabelecendo a conexão
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    # Criação de um cursor para executar comandos SQL
    cursor = conn.cursor()

    # Definição da consulta SQL
    query = """
    SELECT DISTINCT u.pac_1, 
                    s.cod_id as busca, 
                    e.clas_ten
    FROM uncrmt u
    INNER JOIN unsemt s ON u.pac_1 = s.pac_2
    INNER JOIN eqse e ON s.cod_id = e.un_se
    WHERE s.cod_id IN (
        SELECT e.un_se
        FROM eqse e
        WHERE e.un_se IS NOT NULL
    );
    """

    # Executando a consulta
    cursor.execute(query)

    # Recuperando os dados da consulta
    rows = cursor.fetchall()

    # Gravando os dados em um arquivo .txt
    with open("resultado_consulta.txt", "w") as file:
        for row in rows:
            file.write(f"pac_1: {row[0]}, busca: {row[1]}, clas_ten: {row[2]}\n")

    print("Dados gravados com sucesso no arquivo 'resultado_consulta.txt'.")

except Exception as e:
    print(f"Erro: {e}")

finally:
    # Fechando a conexão e o cursor
    if cursor:
        cursor.close()
    if conn:
        conn.close()
