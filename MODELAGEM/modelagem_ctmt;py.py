import psycopg2

# Configurações de conexão ao banco de dados PostgreSQL
host = 'localhost'
port = '5432'
dbname = 'bdgd'
user = 'iuri'
password = 'aa11bb22'

ctmt_value = '37568614'

# Função para criar a tabela 'cmax_results' se não existir
def create_cmax_results_table(cursor):
    create_table_query = """
        CREATE TABLE IF NOT EXISTS cmax_results (
            tip_cnd VARCHAR PRIMARY KEY,
            cmax_renamed NUMERIC
        );
    """
    cursor.execute(create_table_query)

# Função para inserir dados na tabela 'cmax_results'
def insert_cmax_results(cursor):
    insert_query = """
        INSERT INTO cmax_results (tip_cnd, cmax_renamed)
        SELECT seg.cod_id, seg.cmax_renamed
        FROM segcon seg
        JOIN ssdmt s ON seg.cod_id = s.tip_cnd
        WHERE s.ctmt = %s
        ON CONFLICT (tip_cnd) DO NOTHING;
    """
    cursor.execute(insert_query, (ctmt_value,))
    conn.commit()

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

    # Criar a tabela 'cmax_results' se não existir
    create_cmax_results_table(cur)
    print("Tabela 'cmax_results' criada ou já existe.")

    # Inserir dados na tabela 'cmax_results'
    insert_cmax_results(cur)
    print("Dados inseridos na tabela 'cmax_results'.")

except Exception as e:
    print(f'Erro ao conectar ao banco de dados ou ao consultar as tabelas: {e}')

finally:
    # Verifica se as variáveis conn e cur estão definidas e fecha-as corretamente
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
