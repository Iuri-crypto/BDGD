import psycopg2
import os


class DatabaseQuery:
    def __init__(self, dbhost, dbport, dbdbname, dbuser, dbpassword):
        """Inicializa os parâmetros de conexão"""
        self.host = dbhost
        self.port = dbport
        self.dbname = dbdbname
        self.user = dbuser
        self.password = dbpassword
        self.conn = None
        self.cur = None

    def connect(self):
        """Estabelece a conexão com o banco de dados PostgreSQL"""
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cur = self.conn.cursor()
            print("Conexão Estabelecida com sucesso.")
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def consulta_banco(self):
        """Consulta o banco de dados e coleta os dados"""
        try:
            # Consulta a tabela SSDMT para extrair as colunas especificadas
            query = """
                SELECT 
                        ugmt_tab.cod_id, ugmt_tab.pac, ugmt_tab.ctmt, ugmt_tab.fas_con,
                        ugmt_tab.ten_con, ugmt_tab.pot_inst, ugmt_tab.cep,
                        ugmt_tab.ceg_gd,

                FROM 
                    ugmt_tab;       
            """
            # Executa a consulta
            self.cur.execute(query)
            results = self.cur.fetchall()
            return results
        except Exception as e:
            print(f"Erro ao gerar comandos para o OpenDSS: {e}")
            return []

    def lines(self):
        """Cria comandos no formato desejado para o OpenDSS"""
        dados = self.consulta_banco()

        # Caminho principal para salvar as subpastas
        base_dir = r'C:\MODELAGEM_GERADORES_MÉDIA_TENSÃO_BDGD_2023_ENERGISA'

        # Dicionário para armazenar os ctmt já processados
        ctmts_processados = {}

        # Iterar sobre os dados e gerar uma subpasta para cada CTMT
        for index, linha in enumerate(dados):
            cod_id = linha[0]
            pac = linha[1]
            ctmt = linha[2]
            fas_con = linha[3]
            ten_con = linha[4]
            potencia_instalada_kwp = linha[5]
            cep = linha[6]
            potencia_max = linha[5]
            energia_desejada = linha[8:20]
            demanda_contratada = linha[20]
            ceg_gd = linha[7]

            if ceg_gd[:2] != ('GD' and 'UFV'):

                if ctmt not in ctmts_processados:
                    ctmt_folder = os.path.join(base_dir, str(ctmt))
                    os.makedirs(ctmt_folder, exist_ok=True)

                file_path = os.path.join(ctmt_folder, 'Generators.dss')
                file = open(file_path, 'w')

                # Adicionar o ctmt ao dicionário de ctmts processados (armazena o arquivo aberto)
                ctmts_processados[ctmt] = file

                with open(file_path, 'a') as file:
                    ten = 13.8
                    if ten_con == 49:
                        ten = 13.8
                    if ten_con == 72:
                        ten = 34.5

                    mapa_fases = {
                        'ABC': '.1.2.3', 'ACB': '.1.3.2', 'BAC': '.1.2.3', 'BCA': '.1.2.3', 'CAB': '.1.2.3',
                        'CBA': '.1.2.3',
                        'ABCN': '.1.2.3', 'ACBN': '.1.2.3', 'BACN': '.1.2.3', 'BCAN': '.1.2.3', 'CABN': '.1.2.3',
                        'CBAN': '.1.2.3',
                        'ABN': '.1.2', 'ACN': '.1.3', 'BAN': '.1.2', 'CAN': '.1.3', 'A': '.1', 'B': '.2', 'C': '.3',
                        'AN': '.1',
                        'BA': '.1.2', 'BN': '.2', 'CN': '.3', 'AB': '.1.2', 'AC': '.1.3', 'BC': '.2.3',
                        'CNA': '.1', 'ANB': '.1.2', 'BNC': '.2.3', 'CA': '.1.3',
                    }
                    rec_fases = mapa_fases[fas_con]


                    command_pvsystem = f"""
                    ! CTMT - {ctmt}
                                
                            New Generator.{cod_id} Bus1 = {pac}{rec_fases} KW = {potencia_max} Model = {1} PF = 1 KVA = {potencia_max} KV = {ten} Xdp = {0.27} xdpp = {0.20} H = {2}
                            ~ Conn=Delta
                     """


                    file.write(command_pvsystem + "\n")

    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        print("Conexão com o banco de dados fechada.")


# Uso da classe
if __name__ == "__main__":
    # Parâmetros de conexão
    host = 'localhost'
    port = '5432'
    dbname = 'BDGD_2023_ENERGISA'
    user = 'iuri'
    password = 'aa11bb22'

    # Criar uma instância da classe DatabaseQuery
    db_query = DatabaseQuery(host, port, dbname, user, password)

    # Conectar ao banco de dados
    db_query.connect()

    # Gerar comandos para o OpenDSS
    db_query.lines()

    # Fechar a conexão com o banco de dados
    db_query.close()
