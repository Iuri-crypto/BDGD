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
        """Consulta o banco de dados e coleta os dados de `ssmt`"""
        try:
            # Consulta à tabela SSDMT para extrair as colunas especificadas
            query_ssmt = """
               SELECT 
                    uncrmt.cod_id,
                    uncrmt.fas_con,
                    uncrmt.tip_unid,
                    uncrmt.pot_nom,
                    uncrmt.pac_1,
                    uncrmt.ctmt,
                    uncrmt.tip_unid,
                    ctmt.ten_nom -- Adiciona a coluna ten_nom da tabela ctmt
                FROM 
                    uncrmt
                JOIN 
                    ctmt ON uncrmt.ctmt = ctmt.cod_id; -- Realiza o join com base na coluna ctmt
            """
            self.cur.execute(query_ssmt)
            results_ssmt = self.cur.fetchall()
            return results_ssmt
        except Exception as e:
            print(f"Erro ao executar a consulta SSDMT: {e}")
            return []

    def lines(self):
        """Cria comandos no formato desejado para o OpenDSS, incluindo os valores de tensão"""
        dados_ssmt = self.consulta_banco()  # Dados da consulta SSDMT

        # Caminho principal para salvar as subpastas
        base_dir = r'C:\MODELAGEM_COMPENSADORES_DE_REATIVO_MÉDIA_TENSÃO_BDGD_2023_ENERGISA'

        # Dicionário para armazenar os ctmt já processados
        ctmts_processados = {}

        # Iterar sobre os dados de SSDMT e gerar uma subpasta para cada CTMT
        for index, linha in enumerate(dados_ssmt):
            cod_id = linha[0]
            fas_con = linha[1]
            tip_uni = linha[2]
            pot_nom = linha[3]
            pac_1 = linha[4]
            ctmt = linha[5]
            tip_unid = linha[6]
            ten_nom = linha[7]

            # Verificar se o ctmt já foi processado
            if ctmt not in ctmts_processados:
                # Se o ctmt não foi processado ainda, criar uma nova pasta para o ctmt
                ctmt_folder = os.path.join(base_dir, str(ctmt))
                os.makedirs(ctmt_folder, exist_ok=True)

                # Criar o novo arquivo .dss para este ctmt
                file_path = os.path.join(ctmt_folder, 'Compensadores_de_reativo.dss')
                file = open(file_path, 'w')

                # Adicionar o ctmt ao dicionário de ctmts processados (armazena o arquivo aberto)
                ctmts_processados[ctmt] = file
            else:
                # Se o ctmt já foi processado, usar o arquivo existente e abrir no modo append ('a')
                file = ctmts_processados[ctmt]

            # Gerar o comando para cada linha
            mapa_fases = {
                'ABC': '.1.2.3', 'ACB': '.1.3.2', 'BAC': '.1.2.3', 'BCA': '.1.2.3', 'CAB': '.1.2.3', 'CBA': '.1.2.3',
                'ABCN': '.1.2.3', 'ACBN': '.1.2.3', 'BACN': '.1.2.3', 'BCAN': '.1.2.3', 'CABN': '.1.2.3',
                'CBAN': '.1.2.3',
                'ABN': '.1.2', 'ACN': '.1.3', 'BAN': '.1.2', 'CAN': '.1.3', 'A': '.1', 'B': '.2', 'C': '.3', 'AN': '.1',
                'BA': '.1.2', 'BN': '.2', 'CN': '.3', 'AB': '.1.2', 'AC': '.1.3', 'BC': '.2.3',
                'CNA': '.1', 'ANB': '.1.2', 'BNC': '.2.3', 'CA': '.1.3',
            }

            # Definir o valor de tensão baseado em 'ten_nom'
            if ten_nom == 49:
                ten = 13.8
            else:
                ten = 34.5

            rec_fases = mapa_fases.get(fas_con, '')

            # Gerar o comando dependendo do tipo de unidade
            if tip_unid == 56:
                command_linecode = f"""
                               ! Linecode-ctmt: {ctmt}
                               New Reactor.{cod_id} Bus1 = {pac_1}{rec_fases} kv = {ten} kVAR = {pot_nom} phases = {len(rec_fases)} conn = wye
                                """
            else:
                command_linecode = f"""
                               ! Linecode-ctmt: {ctmt}
                               New Capacitor.{cod_id} Bus1 = {pac_1}{rec_fases} kv = {ten} kVAR = {pot_nom} phases = {len(rec_fases)} conn = wye
                               """

            # Escrever o comando no arquivo .dss
            if file:
                file.write(command_linecode)

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

    db_query = DatabaseQuery(host, port, dbname, user, password)
    db_query.connect()
    db_query.lines()
    db_query.close()
