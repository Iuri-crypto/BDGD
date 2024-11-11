import psycopg2

from Consegui_dar_zoom_na_camada import password

# configurações de conexão ao banco de dados PostgreSQL
host = 'localhost'
port = '5432'
dbname = 'bdgd'
user = 'iuri'
password = 'aa11bb22'

# Conecta ao banco de dados PostgreSQL
try: # tenta estabeçlecer uma conexão com o banco de dados
    conn = psycopg2.connect(                 # estabelece a conexão com o banco de dados
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cur = conn.cursor()                      # cria um cursor que será usado para executar as consultas SQL

    # Consulta À tabela  SSDMT
    cur.execute('select * from ssdmt')

    results = cur.fetchall()

    for i, row in enumerate(results[:10]):
        print(f'Linha {i+1}: {row}')

except Exception as e:
    print(f'Erro ao conectar ao banco de dados ou ao consultar a tabela: {e}')

finally:
    if conn:
        cur.close()
        conn.close()

print('Consulta a tabela ssdmt concluida')



