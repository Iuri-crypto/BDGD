import psycopg2
import py_dss_interface
import os  # Para manipulação de arquivos e pastas

dss = py_dss_interface.DSSDLL()


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
                    uncrmt.tip_uni,
                    uncrmt.pot_nom,
                    uncrmt.pac_1,
                    uncrmt.ctmt,
                    uncrmt.tip_unid
                FROM 
                    ssdmt;
            """
            self.cur.execute(query_ssmt)
            results_ssmt = self.cur.fetchall()

            return results_ssmt
        except Exception as e:
            print(f"Erro ao executar a consulta SSDMT: {e}")
            return []

    def consulta_tensao(self):
        """Consulta o banco de dados para obter os valores de `clas_ten` e `valor_tensao`"""
        try:
            # Consulta à tabela para obter os valores de tensões e descrições
            query_tensao = """
                SELECT DISTINCT u.pac_1, 
                                s.cod_id as busca, 
                                e.clas_ten,
                                CASE CAST(e.clas_ten AS INTEGER)
                                    WHEN 0 THEN NULL
                                    WHEN 1 THEN 3800
                                    WHEN 2 THEN 13800
                                    WHEN 3 THEN 14400
                                    WHEN 4 THEN 15000
                                    WHEN 5 THEN 20000
                                    WHEN 6 THEN 23000
                                    WHEN 7 THEN 24000
                                    WHEN 8 THEN 25000
                                    WHEN 9 THEN 34500
                                    WHEN 19 THEN 36200
                                    WHEN 10 THEN 45400
                                    WHEN 11 THEN 69000
                                    WHEN 12 THEN 72500
                                    WHEN 13 THEN 92400
                                    WHEN 14 THEN 138000
                                    WHEN 15 THEN 145000
                                    WHEN 16 THEN 230000
                                    WHEN 17 THEN 242000
                                    WHEN 18 THEN 362000
                                    ELSE NULL
                                END AS valor_tensao
                FROM uncrmt u
                INNER JOIN unsemt s ON u.pac_1 = s.pac_2
                INNER JOIN eqse e ON s.cod_id = e.un_se
                WHERE s.cod_id IN (
                    SELECT e.un_se
                    FROM eqse e
                    WHERE e.un_se IS NOT NULL
                );
            """
            self.cur.execute(query_tensao)
            results_tensao = self.cur.fetchall()
            return results_tensao
        except Exception as e:
            print(f"Erro ao executar a consulta sobre tensões: {e}")
            return []

    def lines(self):
        """Cria comandos no formato desejado para o OpenDSS, incluindo os valores de tensão"""
        dados_ssmt = self.consulta_banco()  # Dados da consulta SSDMT
        dados_tensao = self.consulta_tensao()  # Dados de tensão

        # Caminho principal para salvar as subpastas
        base_dir = r'C:\Compensadores(652)_de_Reativo_BDGD_2023_Energisa'

        # Dicionário para armazenar os ctmt já processados
        ctmts_processados = {}

        # Criar um dicionário para mapear `pac_1` para `valor_tensao`
        mapa_tensao = {}
        for row in dados_tensao:
            pac_1 = row[0]
            valor_tensao = row[3]
            mapa_tensao[pac_1] = valor_tensao

        # Iterar sobre os dados de SSDMT e gerar uma subpasta para cada CTMT
        for index, linha in enumerate(dados_ssmt):
            cod_id = linha[0]
            fas_con = linha[1]
            tip_uni = linha[2]
            pot_nom = linha[3]
            pac_1 = linha[4]
            ctmt = linha[5]
            tip_unid = linha[6]

            # Obter o valor de tensão para o pac_1 correspondente
            valor_tensao = mapa_tensao.get(pac_1, None)

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
            rec_fases = mapa_fases[fas_con]

            if tip_unid == 56:
                command_linecode = f"""
                               ! Linecode-ctmt: {ctmt}
                                New Reactor.{cod_id} Bus1 = {pac_1}{rec_fases} kv = {valor_tensao / 1000} kVAR = {pot_nom} conn = wye
                                """
            else:
                command_linecode = f"""
                              ! Linecode-ctmt: {ctmt}
                               New Capacitor.{cod_id} Bus1 = {pac_1}{rec_fases} kv = {valor_tensao / 1000} kVAR = {pot_nom} conn = wye
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
    user = 'i3e'
    password = 'i3e'

    db_query = DatabaseQuery(host, port, dbname, user, password)
    db_query.connect()
    db_query.lines()
    db_query.close()
