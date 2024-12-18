import psycopg2
import time
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
            query = """
                SELECT 
                    cod_id,pac_1,pac_2,ctmt,fas_con,comp,tip_cnd,wkb_geometry
   
                FROM 
                    ssdbt
            """
            # Executa a consulta
            self.cur.execute(query)
            results = self.cur.fetchall()
            return results
        except Exception as e:
            print(f"Erro ao gerar comandos para o OpenDSS: {e}")
            return []

    def processa_lines(self):
        """ Processa uma linha de dados no banco e gera o comando no formato DSS """
        dados = self.consulta_banco()

        # Caminho principal para salvar as subpastas
        base_dir = r'C:\MODELAGEM_LINHAS_BAIXA_TENSÃO_BDGD_2023_ENERGISA'

        # Dicionario para armazenar os ctmts já processados
        ctmts_processados = {}

        # Iterar sobre os dados e gerar uma subpasta para cada CTMT
        for index, linha in enumerate(dados):
            cod_id = linha[0]
            pac_1 = linha[1]
            pac_2 = linha[2]
            ctmt = linha[3]
            fas_con = linha[4]
            comp = linha[5]
            tip_cnd = linha[6]
            wkb_geometry = linha[7]

            # Verificar se o ctmt já foi processado
            if ctmt not in ctmts_processados:
                ctmt_folder = os.path.join(base_dir, str(ctmt))
                os.makedirs(ctmt_folder, exist_ok=True)
                file_path = os.path.join(ctmt_folder, 'lines.dss')
                file = open(file_path, 'w')
                ctmts_processados[ctmt] = file
            else:
                file = ctmts_processados[ctmt]

            # fases = {'A', 'B', 'C', 'N'}
            # fases_presentes = [letra for letra in fas_con if letra in fases]

            mapa_fases = {
                'ABC': '.1.2.3', 'ACB': '.1.3.2', 'BAC': '.1.2.3', 'BCA': '.1.2.3', 'CAB': '.1.2.3', 'CBA': '.1.2.3',
                'ABCN': '.1.2.3', 'ACBN': '.1.2.3', 'BACN': '.1.2.3', 'BCAN': '.1.2.3', 'CABN': '.1.2.3',
                'CBAN': '.1.2.3',
                'ABN': '.1.2', 'ACN': '.1.3', 'BAN': '.1.2', 'CAN': '.1.3', 'A': '.1', 'B': '.2', 'C': '.3', 'AN': '.1',
                'BA': '.1.2', 'BN': '.2', 'CN': '.3', 'AB': '.1.2', 'AC': '.1.3', 'BC': '.2.3',
                'CNA': '.1', 'ANB': '.1.2', 'BNC': '.2.3', 'CA': '.1.3', 'N':'.0', 'BCN':'.2.3.0'
            }
            rec_fases = mapa_fases[fas_con]

            fases = [fas for fas in fas_con if fas in ['A', 'B', 'C']]

            # Gerar o comando no formato desejado
            command_line = (
            f'! Lines-ctmt: {ctmt}\n'
            f'New Line.{cod_id} Phases = {len(fases)} Bus1 = {pac_1}{rec_fases} Bus2 = {pac_2}{rec_fases} Linecode = {tip_cnd} Length = {comp} units = m\n'
)
            # Escrever o comando no arquivo .dss
            if file:
                file.write(command_line)

        # Fechar todos os arquivos antes de terminar o loop
        for file in ctmts_processados.values():
            file.close()

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

    start_time = time.time()

    # Criar uma instância da classe DatabaseQuery
    db_query = DatabaseQuery(host, port, dbname, user, password)

    # Conectar ao banco de dados
    db_query.connect()

    # Gerar comandos para o OpenDSS
    db_query.processa_lines()

    # Fechar a conexão com o banco de dados
    db_query.close()

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"O tempo de execução foi de {execution_time} segundos.")
