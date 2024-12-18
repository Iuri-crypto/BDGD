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
        """ Estabelece a conexão com o banco de dados PostgreSQL """
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
                        ssdbt.ctmt,
                        ssdbt.tip_cnd,
                        ssdbt.fas_con,
                        ssdbt.comp,
                        (SELECT r1 FROM segcon WHERE segcon.cod_id = ssdbt.tip_cnd LIMIT 1) AS r1,
                        (SELECT x1 FROM segcon WHERE segcon.cod_id = ssdbt.tip_cnd LIMIT 1) AS x1,
                        (SELECT cnom FROM segcon WHERE segcon.cod_id = ssdbt.tip_cnd LIMIT 1) AS cnom,
                        (SELECT cmax_renamed FROM segcon WHERE segcon.cod_id = ssdbt.tip_cnd LIMIT 1) AS cmax_renamed
                FROM 
                    ssdbt;       
            """
            # Executa a consulta
            self.cur.execute(query)
            results = self.cur.fetchall()
            return results
        except Exception as e:
            print(f"Erro ao gerar comandos para o OpenDSS: {e}")
            return []

    def linecode_commands(self):
        """Cria comandos no formato desejado para o OpenDSS"""
        dados = self.consulta_banco()

        # Caminho principal para salvar as subpastas
        base_dir = r'C:\MODELAGEM_LINECODES_BAIXA_TENSAO_BDGD_2023_ENERGISA'

        # Dicionário para armazenar os ctmt já processados
        ctmts_processados = {}

        # Iterar sobre os dados e gerar uma subpasta para cada CTMT
        for index, linha in enumerate(dados):
            ctmt = linha[0] # Este é o campo que será utilizado para criar a subpasta
            tip_cnd = linha[1]
            fas_con = linha[2]
            comp = linha[3]
            r1 = linha[4]
            x1 = linha[5]
            cnom = linha[6]
            cmax_renamed = linha[7]

            # Verificar se o ctmt já foi processado
            if ctmt not in ctmts_processados:
                # Se o ctmt não foi processado ainda, criar uma nova pasta para o ctmt
                ctmt_folder = os.path.join(base_dir, str(ctmt))
                os.makedirs(ctmt_folder, exist_ok=True)

                # Criar o novo arquivo .dss para este ctmt
                file_path = os.path.join( ctmt_folder, 'linecodes.dss')
                file = open(file_path, 'w')

                # Adicionar o ctmt ao dicionario de ctmts processados (armazena o arquivo aberto)
                ctmts_processados[ctmt] = file

            else:
                # Se o ctmt já foi processado, usar o arquivo existente e abrir no modo append ('a')
                file = ctmts_processados[ctmt]

            fases_validades = [letra for letra in fas_con if letra in ['A', 'B', 'C']]

            # Gerar o comando para cada linha
            if len(fases_validades) == 3:
                command_linecode = (
               f'! Linecode-ctmt: {ctmt}\n'
                f'New linecode.{tip_cnd} nphases=3 BaseFreq=60\n'
                f'~ r1={r1}\n'
                f'~ x1={x1}\n'
                f'~ c1={0}\n'
                f'~ Normamps = {cnom}\n'
                f'~ Emergamps = {cmax_renamed}\n'
                )
            elif len(fases_validades) == 2:
                command_linecode = (
               f'! Linecode-ctmt: {ctmt}\n'
                f'New linecode.{tip_cnd} nphases=2 BaseFreq=60\n'
                f'~ r1={r1}\n'
                f'~ x1={x1}\n'
                f'~ c1={0}\n'
                f'~ Normamps = {cnom}\n'
                f'~ Emergamps = {cmax_renamed}\n'
                )
            elif len(fases_validades) == 1:
                command_linecode = (
                f'! Linecode-ctmt: {ctmt}\n'
                f'New linecode.{tip_cnd} nphases=1 BaseFreq=60\n'
                f'~ r1={r1}\n'
                f'~ x1={x1}\n'
                f'~ c1={0}\n'
                f'~ Normamps = {cnom}\n'
                f'~ Emergamps = {cmax_renamed}\n'
                )
            else:
                continue  # Caso não seja nenhuma das opções, ignora e continua
            # Escrever o comando no arquivo.dss
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

    # Criar uma instância da classe DatabaseQuery
    db_query = DatabaseQuery(host, port, dbname, user, password)

    # Conectar ao banco de dados
    db_query.connect()

    # Gerar comandos para o OpenDSS
    db_query.linecode_commands()

    # Fechar a conexão com o banco de dados
    db_query.close()
