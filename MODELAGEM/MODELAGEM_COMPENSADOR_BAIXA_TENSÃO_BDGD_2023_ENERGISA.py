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
                    uncrbt.cod_id,
                    uncrbt.fas_con,
                    uncrbt.tip_unid,
                    uncrbt.pot_nom,
                    uncrbt.pac_1,
                    uncrbt.ctmt,
                    uncrbt.tip_unid,
                    ctmt.ten_nom -- Adiciona a coluna ten_nom da tabela ctmt
                FROM 
                    uncrbt
                JOIN 
                    ctmt ON uncrbt.ctmt = ctmt.cod_id; -- Realiza o join com base na coluna ctmt
            """
            self.cur.execute(query_ssmt)
            results_ssmt = self.cur.fetchall()
            return results_ssmt
        except Exception as e:
            print(f"Erro ao executar a consulta SSDMT: {e}")
            return []

    def Compensadores_commands(self):
        """Cria comandos no formato desejado para o OpenDSS, incluindo os valores de tensão"""
        dados_ssmt = self.consulta_banco()  # Dados da consulta SSDMT

        # Caminho principal para salvar as subpastas
        base_dir = r'C:\MODELAGEM_COMPENSADORES_DE_REATIVO_BAIXA_TENSAO_BDGD_2023_ENERGISA'

        # Dicionário para armazenar os ctmt já processados
        ctmts_processados = {}

        # Dicionário para mapear os valores de ten_forn para as tensões correspondentes
        tensoes = {
            '0': 0, '1': 110, '2': 115, '3': 120, '4': 121, '5': 125, '6': 127, '7': 208, '8': 216, '9': 216.5,
            '10': 220, '11': 230, '12': 231, '13': 240, '14': 254, '15': 380, '72': 220, '49': 220
        }


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

            fases = [fas for fas in fas_con if fas in ['A', 'B', 'C']]

            # Verificar se o ten_forn existe no dicionário tensoes
            if ten_nom in tensoes:
                t = tensoes[ten_nom]
            else:
                # Se o ten_forn não estiver no dicionário, usar um valor default ou gerar um erro
                print(f"Atenção: Valor de ten_forn {ten_nom} não encontrado no dicionário!")
                t = 220  # Ou um valor padrão adequado

            rec_fases = mapa_fases.get(fas_con, '')

            # Gerar o comando dependendo do tipo de unidade
            if tip_unid == 56:
                command_linecode = (
                               f'! Linecode-ctmt: {ctmt}\n'
                               f'New Reactor.{cod_id} Bus1 = {pac_1}{rec_fases} kv = {t/1000} kVAR = {pot_nom} phases = {len(fases)} conn = wye\n'
                )
            else:
                command_linecode = (
                               f'! Linecode-ctmt: {ctmt}\n'
                               f'New Capacitor.{cod_id} Bus1 = {pac_1}{rec_fases} kv = {t/1000} kVAR = {pot_nom} phases = {len(fases)} conn = wye\n'
                               )

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
    db_query.Compensadores_commands()
    db_query.close()
