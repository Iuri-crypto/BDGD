import psycopg2

# Configurações de conexão ao banco de dados PostgreSQL
host = 'localhost'
port = '5432'
dbname = 'bdgd'
user = 'iuri'
password = 'aa11bb22'

ctmt_value = '37568614'

# Conecta ao banco de dados PostgreSQL
try:
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cur = conn.cursor()

    # Consulta á tabela  SSDMT para extrair apenas as colunas especificadas
    query = """
             'SELECT cod_id, pn_con_1, pn_con_2,ctmt, comp, tip_cnd, shape
             FROM ssdmt
             WHERE ctmt = %s;  # %s é um parametro de posição qué substituido pelo valor do ctmt
             """

    cur.execute(query, (ctmt_value,))

    results = cur.fetchall()

except Exception as e:
    print(f'Erro ao conectar ao banco de dados ou ao consultar a tabela: {e}')

finally:
    # Verifica se as variáveis conn e cur estão definidas e fecha-as corretamente
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
