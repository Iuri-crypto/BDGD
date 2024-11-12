import psycopg2
import py_dss_interface

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
                SELECT cod_id, pac_1, pac_2, ctmt, fas_con, comp, tip_cnd, shape
                FROM ssdmt;
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

        # Caminho completo do lines.dss no diretorio C:\
        file_path = r'C:\modelagem_linhas\lines.dss'

        # Abrir arquivo dss para escrever os comandos
        with open(file_path, 'w') as f:
            for index, linha in enumerate(dados):
                cod_id = linha[0]
                pac_1 = linha[1]
                pac_2 = linha[2]
                ctmt = linha[3]
                fas_con = linha[4]
                comp = linha[5]
                tip_cnd = linha[6]
                shape = linha[7]

                if fas_con == 'ABC':
                    command_line = f"""
                    ! Lines
                    New line.{index} Phases=3 Bus1={pac_1}.1.2.3 Bus2={pac_2}.1.2.3 Linecode={tip_cnd} Length={comp * 3.28084} units=kft
                    """
                elif fas_con == 'AB':
                    command_line = f"""
                    ! Lines
                    New line.{index} Phases=2 Bus1={pac_1}.1.2 Bus2={pac_2}.1.2 Linecode={tip_cnd} Length={comp * 3.28084} units=kft
                    """
                elif fas_con == 'AC':
                    command_line = f"""
                    ! Lines
                    New line.{index} Phases=2 Bus1={pac_1}.1.3 Bus2={pac_2}.1.3 Linecode={tip_cnd} Length={comp * 3.28084} units=kft
                    """
                elif fas_con == 'BC':
                    command_line = f"""
                    ! Lines
                    New line.{index} Phases=2 Bus1={pac_1}.2.3 Bus2={pac_2}.2.3 Linecode={tip_cnd} Length={comp * 3.28084} units=kft
                    """
                elif fas_con == 'A':
                    command_line = f"""
                    ! Lines
                    New line.{index} Phases=1 Bus1={pac_1}.1 Bus2={pac_2}.1 Linecode={tip_cnd} Length={comp * 3.28084} units=kft
                    """
                elif fas_con == 'B':
                    command_line = f"""
                    ! Lines
                    New line.{index} Phases=1 Bus1={pac_1}.2 Bus2={pac_2}.2 Linecode={tip_cnd} Length={comp * 3.28084} units=kft
                    """
                elif fas_con == 'C':
                    command_line = f"""
                    ! Lines
                    New line.{index} Phases=1 Bus1={pac_1}.3 Bus2={pac_2}.3 Linecode={tip_cnd} Length={comp * 3.28084} units=kft
                    """
                else:
                    continue  # Caso não seja nenhuma das opções, ignora e continua
                # Escrever o comando no arquivo.dss
                f.write(command_line)


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
    dbname = 'bdgd'
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
