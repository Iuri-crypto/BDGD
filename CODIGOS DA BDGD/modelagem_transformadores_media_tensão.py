import psycopg2
import py_dss_interface
import os

from numpy.testing.print_coercion_tables import print_new_cast_table

dss = py_dss_interface.DSSDLL()

class DataBaseQuery:
    def __init__(self, dbhost, dbport, dbdbname, dbuser, dbpassword):
        """Inicializa os paramêmtros de conexão"""
        self.host = dbhost
        self.port = dbport
        self.dbname = dbdbname
        self.user = dbuser
        self.password = dbpassword
        self.conn = None
        self.cur = None

    def connect(self):
        """ Estabelece a Conexão com o Banco de Dados do PostgreSQL"""
        try:
            self.conn = psycopg2.connect(
                dbname = self.dbname,
                user = self.user,
                password = self.password,
                host = self.host,
                port = self.port
            )
            self.cur = self.conn.cursor()
            print("Conexão Estabelecida com Sucesso.")
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def consulta_banco(self):
        """ Consulta o banco de dados e coleta os dados"""
        try:
            """ Consulta a tabela (untrmt) e coleta os dados das colunas:
                 wkb_geometry, cod_id, pac_1, pac_2 e ctmt

                 Consulta a tabela (eqtrmt) e coleta os dados da colunas:
                 pot_nom, lig, ten_pri, ten_sec, lig_fas_p, lig_fas_s,
                 r, xhl, uni_tr_mt

                 Há a necessidade de cruzar os dados da coluna cod_id
                 da tabela untrmt com a coluna uni_tr_mt da tabela
                 eqtrmt, para pegar todas as informações dos trafos
            """
            query = """
                SELECT 
                    untrmt.wkb_geometry,
                    untrmt.cod_id,
                    untrmt.pac_1,
                    untrmt.pac_2,
                    untrmt.ctmt,
                    eqtrmt.pot_nom,
                    eqtrmt.lig,
                    eqtrmt.ten_pri,
                    eqtrmt.ten_sec,
                    eqtrmt.lig_fas_p,
                    eqtrmt.lig_fas_s,
                    eqtrmt.r,
                    eqtrmt.xhl     
                FROM 
                    untrmt
                LEFT JOIN 
                    eqtrmt ON eqtrmt.uni_tr_mt = untrmt.cod_id
            """
            # Executa a consulta
            self.cur.execute(query)
            results = self.cur.fetchall()
            return results
        except Exception as e:
            print(f"Erro ao gerar comandos para o OpenDSS: {e}")
            return []

    def transformers(self):
        """Cria comandos no formato arquivo.dss (bloco de notas) para o OpenDSS"""
        dados = self.consulta_banco()

        # Caminho principal para salvar as subpastas
        base_dir = r'C:\modelagem_transformadores'

        # Dicionário para armazenar os ctmt já processados
        ctmts_processados = {}

        # Iterar sobre os dados e gerar uma subpasta para cada ctmt
        for index, linha in enumerate(dados):
            cod_id = linha[0]
            pac_1 = linha[1]
            pac_2 = linha[2]
            ctmt = linha[3]
            pot_nom = linha[4]
            lig = linha[5]
            ten_pri = linha[6]
            ten_sec = linha[7]
            lig_fas_p = linha[8]
            lig_fas_s = linha[9]
            r = linha[10]
            xhl = linha[11]

            # Verificar se o ctmt já foi processado
            if ctmt not in ctmts_processados:
                # Se o ctmt não foi processado ainda, criar uma nova pasta para o ctmt
                ctmt_folder = os.path.join(base_dir, str(ctmt))
                os.makedirs(ctmt_folder, exist_ok=True)

                # Criar o novo arquivo .dss para este ctmt
                file_path = os.path.join(ctmt_folder, 'transformers.dss')
                file = open(file_path, 'w')

                # Adicionar o ctmt ao dicionario de ctmts processados (armazena o arquivo aberto)
                ctmts_processados[ctmt] = file

            else:
                # Se o ctmt já foi processado, usar o arquivo existente e abrir no modo append ('a')
                file = ctmts_processados[ctmt]

            # Gerar o comando para cada linha
            command_transformers = f"""
            ! Transformer-ctmt: {ctmt}
            New Transformer.{cod_id} Phases={} Windings=2 xhl={} 
            ~ wdg=1 bus={pac_1} conn={} kv={} Kva={} %r={}
            ~ wdg=2 bus={pac_2} conn={} kv={} Kva={} %r={}
            """


# Uso da classe
if __name__ == "__main__":
    # Parâmetros de conexão
    host = 'localhost'
    port = '5432'
    dbname = 'BDGD_2023_ENERGISA'
    user = 'iuri'
    password = 'aa11bb22'

    # Cria uma instância da classe DataBaseQuery
    db_query = DataBaseQuery(host, port, dbname, user, password)

