import psycopg2
import py_dss_interface
import pandas as pd
import math
import time
import os  # Para manipulação de arquivos e pastas

# Inicializa o objeto do OpenDSS
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
        """Consulta o banco de dados e coleta os dados"""
        try:
            query = """
                SELECT 
                        ssdmt.cod_id,
                        ssdmt.pac_1,
                        ssdmt.pac_2,
                        ssdmt.ctmt,
                        ssdmt.fas_con,
                        ssdmt.comp,
                        ssdmt.tip_cnd,
                        ssdmt.wkb_geometry,
                        segcon.geom_cab,
                        segcon.r1,
                        segcon.x1,
                        segcon.cnom,
                        segcon.cmax_renamed,
                        segcon.bit_fas_1,
                        segcon.bit_fas_2,
                        segcon.bit_fas_3,
                        segcon.bit_neu
                FROM 
                    ssdmt
                LEFT JOIN
                    segcon ON segcon.cod_id = ssdmt.tip_cnd   
            """
            # Executa a consulta
            self.cur.execute(query)
            results = self.cur.fetchall()
            return results
        except Exception as e:
            print(f"Erro ao gerar comandos para o OpenDSS: {e}")
            return []

    def carrega_bitolas_fios_awg_bdgd_2023(self, fas_con, bit_fas_1, bit_fas_2, bit_fas_3, bit_neu):
        """Carrega os dados do xlsx que armazena as bitolas dos fios da média tensão"""

        def criar_dicionario_bitolas_fases():
            df = pd.read_excel(r"C:\area_seccao_fio_awg_bdgd_2023.xlsx")
            dicionario = df.set_index('Codigo')[['mm2', 'RCC(OHMS/KM)']].T.to_dict('dict')
            return dicionario

        def obter_mm2_por_codigo(dicionario, codigo):
            return dicionario.get(codigo)

        # Cria o dicionário de bitolas
        dicionario_mm2_codigo = criar_dicionario_bitolas_fases()

        # Mapeamento das fases
        mapa_codigo = {
            "ABC": bit_fas_1,
            "ABCN": bit_fas_1,
            "AB": bit_fas_1,
            "ABN": bit_fas_1,
            "AC": bit_fas_1,
            "CA": bit_fas_1,
            "ACN": bit_fas_1,
            "BC": bit_fas_1,
            "BCN": bit_fas_1,
            "A": bit_fas_1,
            "AN": bit_fas_1,
            "B": bit_fas_1,
            "BN": bit_fas_1,
            "C": bit_fas_1,
            "CN": bit_fas_1,
        }

        codigo = mapa_codigo.get(fas_con)

        if codigo is None:
            print(f"Erro: 'fas_con' com valor '{fas_con}' não foi encontrado no mapa_codigo.")
            return 0, 0  # Retorna valores padrão se não encontrado no mapa

        # Tenta converter o código para inteiro e buscar a bitola correspondente
        try:
            results = obter_mm2_por_codigo(dicionario_mm2_codigo, int(codigo))
            mm2, RCC = results['mm2'], results['RCC(OHMS/KM)']
        except ValueError:
            print(f"Erro: O valor '{codigo}' não pode ser convertido para inteiro.")
            return 0, 0  # Retorna valores padrão em caso de erro

        if mm2 is None:
            print(f"Erro: Não foi encontrada a bitola para o código {codigo} da fase {fas_con}.")
            return 0, 0  # Retorna valores padrão se não encontrar a bitola

        return mm2, RCC

    def processa_lines(self):
        """Processa uma linha de dados no banco e gera o comando no formato DSS"""
        dados = self.consulta_banco()

        # Caminho principal para salvar as subpastas
        base_dir = r'C:\modelagem_linhas'

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
            geom_cab = linha[8]
            r1 = linha[9]
            x1 = linha[10]
            cnom = linha[11]
            cmax_renamed = linha[12]
            bit_fas_1 = linha[13]
            bit_fas_2 = linha[14]
            bit_fas_3 = linha[15]
            bit_neu = linha[16]

            # Verificar se o ctmt já foi processado
            if ctmt not in ctmts_processados:
                ctmt_folder = os.path.join(base_dir, str(ctmt))
                os.makedirs(ctmt_folder, exist_ok=True)
                file_path = os.path.join(ctmt_folder, 'lines.dss')
                file = open(file_path, 'w')
                ctmts_processados[ctmt] = file
            else:
                file = ctmts_processados[ctmt]

            # Chama a função para obter a bitola
            #area_seccao, RCC = self.carrega_bitolas_fios_awg_bdgd_2023(fas_con, bit_fas_1, bit_fas_2, bit_fas_3, bit_neu)

            # Valor do raio do fio
            #raio = (math.sqrt(area_seccao / math.pi)) / 1000  # Raio em metros

            # Função para contar as fases
            def contar_fases(fas_con):
                fases = {'A', 'B', 'C'}
                fases_presentes = [letra for letra in fas_con if letra in fases]
                return fases_presentes

            fases_presentes = contar_fases(fas_con)

            # Calculo do Raio Geométrico Médio
            #GMR = 0.7788 * raio

            # Gerar configuração para cada condutor de fase
            def gerar_configuracao(fas_con, cod_id):
                condutores = {
                    'A': {'wire': f'{cod_id}_data', 'x': 0, 'h': 10},
                    'B': {'wire': f'{cod_id}_data', 'x': 0.55, 'h': 10},
                    'C': {'wire': f'{cod_id}_data', 'x': 1.1, 'h': 10},
                    'N': {'wire': f'{cod_id}_data', 'x': 1.65, 'h': 10},
                }
                fases_indiv = list(fas_con.upper())
                cond_num = 1
                configuracao = []

                # Adicionar condutores para cada fase fornecida, incluindo o neutro
                for fase in fases_indiv:
                    cond = condutores[fase]
                    configuracao.append(
                        f"~ cond = {cond_num} wire = {cond['wire']} x = {cond['x']} h = {cond['h']} units = m")
                    cond_num += 1
                return '\n'.join(configuracao)

            configuracao = gerar_configuracao(fas_con, cod_id)

            # Gerar o comando no formato desejado
            command_line = f"""
            ! Lines-ctmt: {ctmt}
            New WireData.{cod_id}_data GMR = {0} DIAM = {0} RCC = {0} 
            ~ NormAmps = {cnom} Runits = km radunits = m gmrunits = m
    
            New LineGeometry.{cod_id}_Geometry nconds = {len(fas_con)} nphases = {len(fases_presentes)}
            {configuracao}
    
            New Line.{cod_id} Bus1 = {pac_1} Bus_2 = {pac_2} 
            ~ Geometry = {cod_id}_Geometry
            ~ Lenght = {comp} units = m
            ~ EmergAmps = {cmax_renamed}
            """

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
