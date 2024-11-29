import psycopg2
import pandas as pd
import time
import os
import math


class DatabaseQuery:
    def __init__(self, dbhost, dbport, dbdbname, dbuser, dbpassword):
        """Inicializa os parâmetros de conexão com o banco de dados e carrega o arquivo de bitolas"""
        self.host = dbhost
        self.port = dbport
        self.dbname = dbdbname
        self.user = dbuser
        self.password = dbpassword
        self.conn = None
        self.cur = None

        # Carrega o dicionário com os dados do Excel apenas uma vez
        self.dicionario_mm2_codigo = self.criar_dicionario_bitolas_fases()

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
            print("Conexão estabelecida com sucesso.")
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def consulta_banco(self):
        """Consulta o banco de dados e coleta os dados"""
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
        try:
            self.cur.execute(query)
            results = self.cur.fetchall()
            return results
        except Exception as e:
            print(f"Erro ao consultar o banco de dados: {e}")
            return []

    def consulta_banco_ctmt(self):
        """Consulta o banco de dados e coleta os dados"""
        query = """
                  SELECT 
                      ctmt.pac_ini
                  FROM ctmt
              """
        try:
            self.cur.execute(query)
            results = self.cur.fetchall()
            return results
        except Exception as e:
            print(f"Erro ao consultar o banco de dados: {e}")
            return []


    def criar_dicionario_bitolas_fases(self):
        """Carrega os dados do xlsx e cria o dicionário para busca das bitolas"""
        df = pd.read_excel(r"C:\area_seccao_fio_awg_bdgd_2023.xlsx")
        return df.set_index('Codigo')[['mm2', 'RCC(OHMS/KM)']].T.to_dict('dict')

    def obter_mm2_por_codigo(self, codigo):
        """Obtém a bitola correspondente ao código"""
        return self.dicionario_mm2_codigo.get(codigo)

    def carrega_bitolas_fios_awg_bdgd_2023(self, fas_con, bit_fas_1, bit_fas_2, bit_fas_3, bit_neu):
        """Carrega as bitolas dos fios da média tensão a partir do dicionário carregado"""

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
            results = self.obter_mm2_por_codigo(int(codigo))
            if results:
                return results['mm2'], results['RCC(OHMS/KM)']
            else:
                print(f"Erro: Não foi encontrada a bitola para o código {codigo}.")
                return 0, 0  # Retorna valores padrão se não encontrar a bitola
        except ValueError:
            print(f"Erro: O valor '{codigo}' não pode ser convertido para inteiro.")
            return 0, 0  # Retorna valores padrão em caso de erro

    def processa_linhas_e_gera_comando(self):
        """Consulta os dados no banco e processa cada linha para gerar os comandos DSS diretamente"""
        dados = self.consulta_banco()
        dados_ctmt = self.consulta_banco_ctmt()

        # Caminho principal para salvar as subpastas
        base_dir = r'C:\modelagem_linhas'

        # Processa cada linha sequencialmente
        for linha in dados:
            cod_id, pac_1, pac_2, ctmt, fas_con, comp, tip_cnd, wkb_geometry, geom_cab, r1, x1, cnom, cmax_renamed, bit_fas_1, bit_fas_2, bit_fas_3, bit_neu = linha

            # Verifica se o ctmt já foi processado
            ctmt_folder = os.path.join(base_dir, str(ctmt))
            os.makedirs(ctmt_folder, exist_ok=True)

            file_path = os.path.join(ctmt_folder, 'lines.dss')
            with open(file_path, 'a') as file:
                # Chama a função para obter a bitola
                area_seccao, RCC = self.carrega_bitolas_fios_awg_bdgd_2023(fas_con, bit_fas_1, bit_fas_2, bit_fas_3, bit_neu)

                # Cálculo do raio
                raio = (math.sqrt(area_seccao / math.pi)) / 1000  # Raio em metros

                # Função para contar as fases
                def contar_fases(fas_con):
                    return [letra for letra in fas_con if letra in {'A', 'B', 'C'}]

                fases_presentes = contar_fases(fas_con)
                GMR = 0.7788 * raio

                # Gerar configuração para cada condutor de fase
                def gerar_configuracao(fas_con, cod_id):
                    condutores = {
                        'A': {'wire': f'{cod_id}_data', 'x': 0, 'h': 10},
                        'B': {'wire': f'{cod_id}_data', 'x': 0.55, 'h': 10},
                        'C': {'wire': f'{cod_id}_data', 'x': 1.1, 'h': 10},
                        'N': {'wire': f'{cod_id}_data', 'x': 1.65, 'h': 10},
                    }
                    return '\n'.join(
                        f"~ cond = {i + 1} wire = {condutores[fase]['wire']} x = {condutores[fase]['x']} h = {condutores[fase]['h']} units = m"
                        for i, fase in enumerate(fas_con.upper())
                    )

                configuracao = gerar_configuracao(fas_con, cod_id)

                # Obtendo Barra Slack
                if  str(pac_1) in dados_ctmt:
                    pac_1 = 'SourceBus'

                elif str(pac_2) in dados_ctmt:
                    pac_2 = 'SourceBus'

                # Gerar o comando no formato desejado
                command_line = f"""
                ! Lines-ctmt: {ctmt}
                New WireData.{cod_id}_data GMR = {GMR} DIAM = {2 * raio} RCC = {RCC} 
                ~ NormAmps = {cnom} Runits = km radunits = m gmrunits = m

                New LineGeometry.{cod_id}_Geometry nconds = {len(fas_con)} nphases = {len(fases_presentes)}
                {configuracao}

                New Line.{cod_id} Bus1 = {pac_1} Bus_2 = {pac_2} 
                ~ Geometry = {cod_id}_Geometry
                ~ Lenght = {comp} units = m
                ~ EmergAmps = {cmax_renamed}
                """
                file.write(command_line)

    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        print("Conexão com o banco de dados fechada.")


# Uso da classe
if __name__ == "__main__":
    host = 'localhost'
    port = '5432'
    dbname = 'BDGD_2023_ENERGISA'
    user = 'iuri'
    password = 'aa11bb22'

    start_time = time.time()

    db_query = DatabaseQuery(host, port, dbname, user, password)
    db_query.connect()
    db_query.processa_linhas_e_gera_comando()
    db_query.close()

    end_time = time.time()
    print(f"Tempo de execução: {end_time - start_time} segundos.")
