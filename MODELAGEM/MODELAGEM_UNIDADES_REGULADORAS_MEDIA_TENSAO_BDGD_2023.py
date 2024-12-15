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
        """Estabelece a Conexão com o Banco de Dados do PostgreSQL"""
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

    def consulta_banco(self):
        """Consulta o banco de dados e coleta os dados"""
        try:
            query = """
                 SELECT 
                    u.cod_id, 
                    u.fas_con, 
                    u.pac_1, 
                    u.pac_2, 
                    u.ctmt,
                    e.pot_nom, 
                    e.lig_fas_p, 
                    e.lig_fas_s, 
                    e.per_fer, 
                    e.per_tot, 
                    e.r, 
                    e.xhl,
                    c.ten_nominal_voltage,
                    e.cor_nom,
                    e.rel_tp,
                    e.rel_tc
            FROM 
                unremt u
            JOIN 
                eqre e ON u.cod_id = e.un_re  
            LEFT JOIN 
                ctmt c ON u.ctmt = c.cod_id   
            WHERE 
                u.ctmt IS NOT NULL
            ORDER BY 
                u.cod_id; 
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
        base_dir = r'C:\MODELAGEM_REGULADORES_MÉDIA_TENSÃO_BDGD_2023_ENERGISA'

        # Dicionário para armazenar os ctmt já processados
        ctmts_processados = {}

        # Iterar sobre os dados e gerar uma subpasta para cada ctmt
        for index, linha in enumerate(dados):
            cod_id = linha[0]
            fas_con = linha[1]
            pac_1 = linha[2]
            pac_2 = linha[3]
            ctmt = linha[4]
            pot_nom = linha[5]
            lig_fas_p = linha[6]
            lig_fas_s = linha[7]
            per_fer = linha[8]
            per_tot = linha[9]
            r = linha[10]
            xhl = linha[11]
            ten_nominal_voltage = linha[12]
            cor_nom = linha[13]
            rel_tp = linha[14]
            rel_tc = linha[15]

            # Verificar se o ctmt já foi processado
            if ctmt not in ctmts_processados:
                # Se o ctmt não foi processado ainda, criar uma nova pasta para o ctmt
                ctmt_folder = os.path.join(base_dir, str(ctmt))
                os.makedirs(ctmt_folder, exist_ok=True)

                # Criar o novo arquivo .dss para este ctmt
                file_path = os.path.join(ctmt_folder, 'Reg_Control.dss')
                file = open(file_path, 'w')

                # Adicionar o ctmt ao dicionário de ctmts processados (armazena o arquivo aberto)
                ctmts_processados[ctmt] = file
            else:
                # Se o ctmt já foi processado, usar o arquivo existente e abrir no modo append ('a')
                file = ctmts_processados[ctmt]

            mapa_fases_p = {
                'ABC': '.1.2.3', 'ACB': '.1.3.2', 'BAC': '.1.2.3', 'BCA': '.1.2.3', 'CAB': '.1.2.3', 'CBA': '.1.2.3',
                'ABCN': '.1.2.3', 'ACBN': '.1.2.3', 'BACN': '.1.2.3', 'BCAN': '.1.2.3', 'CABN': '.1.2.3',
                'CBAN': '.1.2.3',
                'ABN': '.1.2', 'ACN': '.1.3', 'BAN': '.1.2', 'CAN': '.1.3', 'A': '.1', 'B': '.2', 'C': '.3', 'AN': '.1',
                'BA': '.1.2', 'BN': '.2', 'CN': '.3', 'AB': '.1.2', 'AC': '.1.3', 'BC': '.2.3',
                'CNA': '.1', 'ANB': '.1.2', 'BNC': '.2.3', 'CA': '.1.3', 'N': '.0', 'BCN': '.2.3.0'
            }
            rec_fases_p = mapa_fases_p[lig_fas_p]

            mapa_fases_s = {
                'ABC': '.1.2.3', 'ACB': '.1.3.2', 'BAC': '.1.2.3', 'BCA': '.1.2.3', 'CAB': '.1.2.3', 'CBA': '.1.2.3',
                    'ABCN': '.1.2.3', 'ACBN': '.1.2.3', 'BACN': '.1.2.3', 'BCAN': '.1.2.3', 'CABN': '.1.2.3',
                    'CBAN': '.1.2.3',
                    'ABN': '.1.2', 'ACN': '.1.3', 'BAN': '.1.2', 'CAN': '.1.3', 'A': '.1', 'B': '.2', 'C': '.3', 'AN': '.1',
                    'BA': '.1.2', 'BN': '.2', 'CN': '.3', 'AB': '.1.2', 'AC': '.1.3', 'BC': '.2.3',
                    'CNA': '.1', 'ANB': '.1.2', 'BNC': '.2.3', 'CA': '.1.3', 'N': '.0', 'BCN': '.2.3.0'
            }
            rec_fases_s = mapa_fases_s[lig_fas_s]

            # Gerar o comando para cada linha
            command_transformers = f"""
            ! Regulador-ctmt: {ctmt}
            new transformer.reg{lig_fas_p}_{cod_id} phases={len(lig_fas_p)} windings=2 bank={cod_id} buses=({pac_1}{rec_fases_p} {pac_2}{rec_fases_s}) conns='Delta Delta' kvs="{ten_nominal_voltage / 1000} {ten_nominal_voltage / 1000}" kvas="{pot_nom} {pot_nom}" XHL = {xhl}
            new regcontrol.creg{lig_fas_p}_{cod_id} transformer=reg{lig_fas_p}_{cod_id} winding=2 vreg={int(ten_nominal_voltage) / int(rel_tp)} band={cod_id} ptratio={rel_tp} ctprim={cor_nom} 
            """

            if file:
                file.write(command_transformers)

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
    db_query = DataBaseQuery(host, port, dbname, user, password)

    # Conectar ao banco de dados
    db_query.connect()

    # Gerar comandos para o OpenDSS
    db_query.transformers()

    # Fechar a conexão com o banco de dados
    db_query.close()

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"O tempo de execução foi de {execution_time} segundos.")
