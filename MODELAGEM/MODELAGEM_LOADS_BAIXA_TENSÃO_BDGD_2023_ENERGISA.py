import psycopg2
import os
import time


class DataBaseQuery:
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
        """Estabelece a conexão com o Banco de Dados do PostgreSQL"""
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cur = self.conn.cursor()
            print("Conexão Estabelecida com Sucesso.")
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def consulta_banco(self, offset=0, limit=100000):
        """Consulta o banco de dados e coleta os dados em batches"""
        if self.cur is None:
            print("Erro: O cursor não foi inicializado. Verifique a conexão.")
            return []

        try:
            query = f"""
                SELECT DISTINCT  ucbt_tab.cod_id,
                    ucbt_tab.tip_cc, 
                    ucbt_tab.pac, ucbt_tab.ctmt, ucbt_tab.fas_con, ucbt_tab.ten_forn
                FROM 
                    ucbt_tab
                WHERE ucbt_tab.gru_ten = 'BT'
                LIMIT {limit} OFFSET {offset};
            """
            self.cur.execute(query)
            while True:
                rows = self.cur.fetchmany(500)  # Coletando os dados em pequenos lotes
                if not rows:
                    break
                for linha in rows:
                    yield linha  # Retorna uma linha de cada vez
        except Exception as e:
            print(f"Erro ao gerar comandos para o OpenDSS: {e}")
            return []

    def loads(self, total_rows=1960246):
        """Cria comandos no formato arquivo.dss (bloco de notas) para o OpenDSS"""
        base_dir = r'C:\MODELAGEM_CARGAS_BAIXA_TENSAO_BDGD_2023_ENERGISA'

        # Dicionário para armazenar os ctmt já processados
        ctmts_processados = {}

        # Definir o total de linhas que desejamos percorrer
        limit = 100000  # Limite de registros por vez
        processed_rows = 0  # Contador para monitorar as linhas processadas

        for offset in range(0, total_rows, limit):
            dados = self.consulta_banco(offset=offset, limit=limit)

            # Iterar sobre os dados e gerar uma subpasta para cada ctmt
            for index, linha in enumerate(dados):
                # Verificar se já alcançou o total de linhas que você deseja processar
                if processed_rows >= total_rows:
                    print(f"Total de {total_rows} linhas processadas.")
                    return

                cod_id = linha[0]
                tip_cc = linha[1]
                pac = linha[2]
                ctmt = linha[3]
                fas_con = linha[4]
                ten_forn = linha[5]


                # Verificar se o ctmt já foi processado
                if ctmt not in ctmts_processados:
                    # Se o ctmt não foi processado ainda, criar uma nova pasta para o ctmt
                    ctmt_folder = os.path.join(base_dir, str(ctmt))
                    os.makedirs(ctmt_folder, exist_ok=True)

                    # Criar o novo arquivo .dss para este ctmt
                    file_path = os.path.join(ctmt_folder, 'loads.dss')
                    file = open(file_path, 'w')

                    # Adicionar o ctmt ao dicionário de ctmts processados (armazena o arquivo aberto)
                    ctmts_processados[ctmt] = file
                else:
                    # Se o ctmt já foi processado, usar o arquivo existente e abrir no modo append ('a')
                    file = ctmts_processados[ctmt]

                # Fator de Ajuste para a curva de carga
                mapa_fases = {
                    'ABC': '.1.2.3', 'ACB': '.1.3.2', 'BAC': '.1.2.3', 'BCA': '.1.2.3', 'CAB': '.1.2.3', 'CBA': '.1.2.3',
                    'ABCN': '.1.2.3', 'ACBN': '.1.2.3', 'BACN': '.1.2.3', 'BCAN': '.1.2.3', 'CABN': '.1.2.3',
                    'CBAN': '.1.2.3',
                    'ABN': '.1.2', 'ACN': '.1.3', 'BAN': '.1.2', 'CAN': '.1.3', 'A': '.1', 'B': '.2', 'C': '.3', 'AN': '.1',
                    'BA': '.1.2', 'BN': '.2', 'CN': '.3', 'AB': '.1.2', 'AC': '.1.3', 'BC': '.2.3',
                    'CNA': '.1', 'ANB': '.1.2', 'BNC': '.2.3', 'CA': '.1.3', 'N': '.0', 'BCN': '.2.3.0'
                }
                rec_fases = mapa_fases.get(fas_con, '.1.2.3')

                fases = [fas for fas in fas_con if fas in ['A', 'B', 'C']]



                command_transformers = (
                    f'! load-ctmt: {ctmt}\n'
                    f'New Load.{cod_id} Bus1 = {pac}{rec_fases} Phases = {len(fases)} Conn = Delta Model = 1 Kv = {ten_forn} Kw = {1} Kvar = 0 !tip_cc = {tip_cc}\n'
                )

                if file:
                    file.write(command_transformers)

                # Incrementar o contador de linhas processadas
                processed_rows += 1

            # Se o número de linhas processadas atingir o total desejado, encerra o loop
            if processed_rows >= total_rows:
                print(f"Total de {total_rows} linhas processadas.")
                break

        # Fechar todos os arquivos após o término
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
    db_query = DataBaseQuery(host, port, dbname, user, password)

    # Conectar ao banco de dados
    db_query.connect()

    # Gerar comandos para o OpenDSS (processar até 1960246 linhas)
    db_query.loads(total_rows=1960246)

    # Fechar a conexão com o banco de dados
    db_query.close()

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"O tempo de execução foi de {execution_time} segundos.")
