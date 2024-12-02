import psycopg2   # conectar-se a bancos de dados PosgreSQL
from psycopg2 import sql  # módulo que permite consultas seguras e otimizadas

# Configuração da Conexão
host = 'localhost'
port = '5432'
dbname = 'bdgd'
user = 'iuri'
password = 'aa11bb22'

ctmt_value = '37568614'

def create_table_if_not_exist(cursor):
    create_table_query = """
            CREATE TABLE IF NOT EXIST linhas_do_alimentador (
            cod_id VARCHAR,
            pn_con_1 VARCHAR,
            pn_con_2 VARCHAR,
            ctmt VARCHAR,
            comp VARCHAR,
            tip_cnd VARCHAR,
            shape VARCHAR,
            r1 NUMERIC,
            x1 NUMERIC,
            CNOM numeric
            );
        """

    cursor.execute(create_table_query)

# Conectar ao Banco de Dados e Executar Consultas
try:
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cur = conn.cursor()

    query_ssdmt = """
        SELECT cod_id, pn_con_1, pn_con_2, ctmt, comp, tip_cnd, shape
        FROM ssdmt
        WHERE ctmt = %s;
    """

    cur.execute(query_ssdmt, (ctmt_value,))
    ssdmt_results = cur.fetchall()

    # Processar Dados da Consulta
    col_names = [desc[0] for desc in cur.description]
    tip_cnd_index = col_names.index('tip_cnd')
    tip_cnd_values = [row[tip_cnd_index] for row in ssdmt_results]

    query_segcon = """
         SELECT cod_id, r1, x1, cnom
         FROM segcon
         WHERE cod_id = ANY(%s);
    """

    cur.execute(query_segcon, (tip_cnd_values,))
    segcon_results = cur.fetchall()

    segcon_dict = {row[0]: row[1:] for row in segcon_results}
    combined_results = []
    for row in ssdmt_results:
        tip_cnd_value = row[tip_cnd_index]
        segcon_data = segcon_dict.get(tip_cnd_value, (None, None, None))
        combined_row = row + segcon_data
        combined_results.append(combined_row)


    # Criar Tabela, Inserir Dados e Verificar Estrutura
    create_table_if_not_exist(cur)
    conn.commit()   # Salva as alterações no banco de dados

    check_table_columns(cur, 'combined_results')





