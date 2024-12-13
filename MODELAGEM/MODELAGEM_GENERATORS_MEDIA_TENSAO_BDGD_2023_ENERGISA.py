import os
import psycopg2


class DatabaseQuery:
    """
    Classe para realizar consultas no banco de dados PostgreSQL e gerar comandos para o OpenDSS.
    """
    def __init__(self, dbhost, dbport, dbname, dbuser, dbpassword):
        """Inicializa os parâmetros de conexão ao banco de dados."""
        self.host = dbhost
        self.port = dbport
        self.dbname = dbname
        self.user = dbuser
        self.password = dbpassword
        self.conn = None
        self.cur = None

    def connect(self):
        """Estabelece a conexão com o banco de dados."""
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cur = self.conn.cursor()
            print("Conexão estabelecida com sucesso.")
        except psycopg2.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def execute_query(self, query):
        """Executa uma consulta no banco de dados e retorna os resultados."""
        try:
            self.cur.execute(query)
            return self.cur.fetchall()
        except psycopg2.Error as e:
            print(f"Erro ao executar consulta: {e}")
            return []

    def fetch_data(self):
        """Busca os dados necessários no banco de dados."""
        query = """
        SELECT 
            cod_id, pac, ctmt, fas_con, ten_con, pot_inst, cep, ceg_gd
        FROM 
            ugmt_tab;
        """
        return self.execute_query(query)

    def generate_commands(self):
        """Gera os comandos para o OpenDSS a partir dos dados obtidos."""
        dados = self.fetch_data()

        # Configuração do diretório base
        base_dir = r'C:\MODELAGEM_GERADORES_MÉDIA_TENSÃO_BDGD_2023_ENERGISA'
        os.makedirs(base_dir, exist_ok=True)

        # Dicionário para rastrear CTMTs processados
        ctmts_processados = {}

        # Mapa de fases para o OpenDSS
        mapa_fases = {
            'ABC': '.1.2.3', 'ACB': '.1.3.2', 'BAC': '.1.2.3', 'BCA': '.1.2.3',
            'CAB': '.1.2.3', 'CBA': '.1.2.3', 'ABCN': '.1.2.3', 'ACBN': '.1.2.3',
            'BACN': '.1.2.3', 'BCAN': '.1.2.3', 'CABN': '.1.2.3', 'CBAN': '.1.2.3',
            'ABN': '.1.2', 'ACN': '.1.3', 'BAN': '.1.2', 'CAN': '.1.3',
            'A': '.1', 'B': '.2', 'C': '.3', 'AN': '.1', 'BA': '.1.2', 'BN': '.2',
            'CN': '.3', 'AB': '.1.2', 'AC': '.1.3', 'BC': '.2.3',
            'CNA': '.1', 'ANB': '.1.2', 'BNC': '.2.3', 'CA': '.1.3'
        }

        for linha in dados:
            cod_id, pac, ctmt, fas_con, ten_con, pot_inst, cep, ceg_gd = linha

            if not ceg_gd.startswith(('GD', 'UFV')):
                # Remove espaços extras ou caracteres inválidos de `ctmt`
                ctmt = str(ctmt).strip()

                if not ctmt:  # Ignorar se `ctmt` for vazio
                    print(f"CTMT inválido encontrado para linha: {linha}")
                    continue

                # Define o diretório e cria a pasta do CTMT
                if ctmt not in ctmts_processados:
                    ctmt_folder = os.path.join(base_dir, ctmt)
                    os.makedirs(ctmt_folder, exist_ok=True)
                    ctmts_processados[ctmt] = open(os.path.join(ctmt_folder, 'Generators.dss'), 'a')

                # Define a tensão em função do código ten_con
                ten = 13.8 if ten_con == 49 else 34.5 if ten_con == 72 else None

                # Recupera o formato das fases
                rec_fases = mapa_fases.get(fas_con, '.1.2.3')

                # Gera o comando do gerador
                command = (
                    f"! CTMT - {ctmt}\n"
                    f"New Generator.{cod_id} Bus1={pac}{rec_fases} KW={pot_inst} Model=1 PF=1 "
                    f"KVA={pot_inst} KV={ten} Xdp=0.27 xdpp=0.20 H=2\n"
                    f"~ Conn=Delta\n"
                )

                # Escreve no arquivo correspondente
                ctmts_processados[ctmt].write(command + '\n')

        # Fecha todos os arquivos abertos
        for file in ctmts_processados.values():
            file.close()

    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        print("Conexão com o banco de dados fechada.")


if __name__ == "__main__":
    # Parâmetros de conexão
    db_config = {
        'dbhost': 'localhost',
        'dbport': '5432',
        'dbname': 'BDGD_2023_ENERGISA',
        'dbuser': 'iuri',
        'dbpassword': 'aa11bb22'
    }

    # Cria e utiliza a classe DatabaseQuery
    db_query = DatabaseQuery(**db_config)

    try:
        db_query.connect()
        db_query.generate_commands()
    finally:
        db_query.close()
