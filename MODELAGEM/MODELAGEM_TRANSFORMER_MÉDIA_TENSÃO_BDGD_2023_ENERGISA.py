import psycopg2
import os
import math
import time


class DataBaseQuery:
    def __init__(self, dbhost, dbport, dbdbname, dbuser, dbpassword):
        """Inicializa os paramêmtros de conexão"""
        self.host = dbhost
        self.port = dbport
        self.dbname = dbdbname
        self.user = dbuser
        self.password = dbpassword
        self.conn = None
        self.cur = None

    def connect(self):
        """ Estabelece a Conexão com o Banco de Dados do PostgreSQL"""
        try:
            self.conn = psycopg2.connect(
                dbname = self.dbname,
                user = self.user,
                password = self.password,
                host = self.host,
                port = self.port
            )
            self.cur = self.conn.cursor()
            print("Conexão Estabelecida com Sucesso.")
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def consulta_banco(self):
        """ Consulta o banco de dados e coleta os dados"""
        try:
            """ Consulta a tabela (untrmt) e coleta os dados das colunas:
                 wkb_geometry, cod_id, pac_1, pac_2 e ctmt

                 Consulta a tabela (eqtrmt) e coleta os dados da colunas:
                 pot_nom, lig, ten_pri, ten_sec, lig_fas_p, lig_fas_s,
                 r, xhl, uni_tr_mt

                 Há a necessidade de cruzar os dados da coluna cod_id
                 da tabela untrmt com a coluna uni_tr_mt da tabela
                 eqtrmt, para pegar todas as informações dos trafos
            """
            query = """
                SELECT 
                    untrmt.wkb_geometry,
                    untrmt.cod_id,
                    untrmt.pac_1,
                    untrmt.pac_2,
                    untrmt.ctmt,
                    eqtrmt.pot_nom,
                    eqtrmt.lig,
                    eqtrmt.ten_pri,
                    eqtrmt.ten_sec,
                    eqtrmt.lig_fas_p,
                    eqtrmt.lig_fas_s,
                    eqtrmt.r,
                    eqtrmt.xhl,
                    eqtrmt.ten_pri_voltage,
                    eqtrmt.ten_sec_voltage,
                    eqtrmt.potencia_nominal_kva,
                    eqtrmt.per_fer,
                    eqtrmt.per_tot,
                    eqtrmt.lig
                FROM 
                    untrmt
                LEFT JOIN 
                    eqtrmt ON eqtrmt.uni_tr_mt = untrmt.cod_id
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
        base_dir = r'C:\MODELAGEM_TRANSFORMADORES_MÉDIA_TENSÃO_BDGD_2023_ENERGISA'

        # Dicionário para armazenar os ctmt já processados
        ctmts_processados = {}

        # Iterar sobre os dados e gerar uma subpasta para cada ctmt
        for index, linha in enumerate(dados):
            wkb = linha[0]
            cod_id = linha[1]
            pac_1 = linha[2]
            pac_2 = linha[3]
            ctmt = linha[4]
            pot_nom = linha[5]
            lig = linha[6]
            ten_pri = linha[7]
            ten_sec = linha[8]
            lig_fas_p = linha[9]
            lig_fas_s = linha[10]
            r = linha[11]
            xhl = linha[12]
            ten_pri_voltage = linha[13]
            ten_sec_voltage = linha[14]
            potencia_nominal = linha[15]
            perdas_ferro = linha[16]
            perdas_total = linha[17]
            ligacao = linha[18]

            # Verificar se o ctmt já foi processado
            if ctmt not in ctmts_processados:
                # Se o ctmt não foi processado ainda, criar uma nova pasta para o ctmt
                ctmt_folder = os.path.join(base_dir, str(ctmt))
                os.makedirs(ctmt_folder, exist_ok=True)

                # Criar o novo arquivo .dss para este ctmt
                file_path = os.path.join(ctmt_folder, 'TRANSFORMERS.dss')
                file = open(file_path, 'w')

                # Adicionar o ctmt ao dicionario de ctmts processados (armazena o arquivo aberto)
                ctmts_processados[ctmt] = file

            else:
                # Se o ctmt já foi processado, usar o arquivo existente e abrir no modo append ('a')
                file = ctmts_processados[ctmt]

            mapa_fases_p =  {
                'ABC': '.1.2.3', 'ACB': '.1.3.2', 'BAC': '.1.2.3', 'BCA': '.1.2.3', 'CAB': '.1.2.3', 'CBA': '.1.2.3',
                'ABCN': '.1.2.3', 'ACBN': '.1.2.3', 'BACN': '.1.2.3', 'BCAN': '.1.2.3', 'CABN': '.1.2.3',
                'CBAN': '.1.2.3',
                'ABN': '.1.2', 'ACN': '.1.3', 'BAN': '.1.2', 'CAN': '.1.3', 'A': '.1', 'B': '.2', 'C': '.3', 'AN': '.1',
                'BA': '.1.2', 'BN': '.2', 'CN': '.3', 'AB': '.1.2', 'AC': '.1.3', 'BC': '.2.3',
                'CNA': '.1', 'ANB': '.1.2', 'BNC': '.2.3',  'CA': '.1.3',
            }
            rec_fases_p = mapa_fases_p[lig_fas_p]

            mapa_fases_s =  {
                'ABC': '.1.2.3', 'ACB': '.1.3.2', 'BAC': '.1.2.3', 'BCA': '.1.2.3', 'CAB': '.1.2.3', 'CBA': '.1.2.3',
                'ABCN': '.1.2.3', 'ACBN': '.1.2.3', 'BACN': '.1.2.3', 'BCAN': '.1.2.3', 'CABN': '.1.2.3',
                'CBAN': '.1.2.3',
                'ABN': '.1.2', 'ACN': '.1.3', 'BAN': '.1.2', 'CAN': '.1.3', 'A': '.1', 'B': '.2', 'C': '.3', 'AN': '.1',
                'BA': '.1.2', 'BN': '.2', 'CN': '.3', 'AB': '.1.2', 'AC': '.1.3', 'BC': '.2.3',
                'CNA': '.1', 'ANB': '.1.2', 'BNC': '.2.3',  'CA': '.1.3',
            }
            rec_fases_s = mapa_fases_s[lig_fas_s]

            conn_p = 'delta' if ligacao == 0 or 2 else 'estrela'
            conn_s = 'delta' if ligacao == 11 else 'estrela'

            ten_primario = '{:.2f}'.format(ten_pri_voltage) if len(lig_fas_p) >= 2 else '{:.2f}'.format(
                int(ten_pri_voltage) / math.sqrt(3))
            ten_secundario = '{:.2f}'.format(ten_sec_voltage) if len(lig_fas_s) >= 2 else '{:.2f}'.format(
                int(ten_sec_voltage) / math.sqrt(3))

            # Gerar o comando para cada linha
            """ %r são as perdas no cobre 
                %noloadloss são as perdas no ferro (histerese e correntes de facault)
                %loadloss são as perdas totais do trafo (perdas no ferro + perdas no cobre) não usado porque ja definido o %r
            """
            command_transformers = f"""
            ! Transformer-ctmt: {ctmt}
            New Transformer.{cod_id} Phases={len(lig_fas_p)} Windings=2 xhl={xhl} %noloadloss = {(perdas_ferro / perdas_total) * 100} 
            ~ wdg=1 bus={pac_1}{rec_fases_p} conn={conn_p} kv={ten_primario} Kva={potencia_nominal} %r={r} 
            ~ wdg=2 bus={pac_2}{rec_fases_s} conn={conn_s} kv={ten_secundario} Kva={potencia_nominal} %r={r}
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


    # tem 200 valores de trafos nao conectados a ssdmt porqeu nao tem chave 