import psycopg2
import pandas as pd
import numpy as np
import os
from pvlib import location

from MODELAGEM.teste import eficiencia


class DatabaseQuery:
    def __init__(self, dbhost, dbport, dbdbname, dbuser, dbpassword,
                 dblatitude, dblongitude, dbaltitude, dbeficiencia,
                 dbgamma, dbalpha, dbbase_dir):
        """Inicializa os parâmetros de conexão"""
        self.host = dbhost
        self.port = dbport
        self.dbname = dbdbname
        self.user = dbuser
        self.password = dbpassword
        self.latitude = dblatitude
        self.longitude =  dblongitude
        self.altitude = dbaltitude
        self.eficiencia = dbeficiencia
        self.gamma = dbgamma
        self.alpha = dbalpha
        self.base_dir = dbbase_dir
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
            # Consulta a tabela SSDMT para extrair as colunas especificadas
            query = """
                SELECT 
                        ugbt_tab.cod_id, ugbt_tab.pac, ugbt_tab.ctmt, ugbt_tab.fas_con,
                        ugbt_tab.ten_con, ugbt_tab.pot_inst, ugbt_tab.cep,
                        ugbt_tab.ceg_gd,
                        ugbt_tab.ene_01, ugbt_tab.ene_02, ugbt_tab.ene_03,
                        ugbt_tab.ene_04, ugbt_tab.ene_05, ugbt_tab.ene_06,
                        ugbt_tab.ene_07, ugbt_tab.ene_08, ugbt_tab.ene_09,
                        ugbt_tab.ene_10, ugbt_tab.ene_11, ugbt_tab.ene_12,
                        ugbt_tab.dem_cont

                FROM 
                    ugbt_tab;       
            """
            # Executa a consulta
            self.cur.execute(query)
            results = self.cur.fetchall()
            return results
        except Exception as e:
            print(f"Erro ao gerar comandos para o OpenDSS: {e}")
            return []

    def calcular_potencia_gerada(self, irradiancia, potencia_instalada_kwp, eficiencia):
        """
        :param irradiancia: quantidade em wh/m2 de sol
        :param potencia_instalada_kwp: potência do inversor solar
        :param eficiencia: limitações e saturações do inversor
        :return:
        """
        potencia = potencia_instalada_kwp * (irradiancia / 1000) * eficiencia
        return potencia

    def aplicar_saturacao_inversor(self, potencia_gerada, potencia_max_inversor_kw):
        """
        :param potencia_gerada: diferência entre a quantidade de potência que entra - perdas, saturações...
        :param potencia_max_inversor_kw: maior quantidade de potência que o inversor consegue injetar nna rede
        :return:
        """
        return np.minimum(potencia_gerada, potencia_max_inversor_kw)

    def estimar_temperatura(self, hora, latitude):
        """
        :param hora: hora do dia de simulação do respectivo ano escolhido
        :param latitude:  a temperatura varia com a latitude (distancia até a linha do Equador)
        :return:
        """
        t_max = 40
        t_min = 15
        temperatura = (t_max + t_min) / 2 + (t_max - t_min) / 2 * np.sin(
            np.pi * (hora - 6) / 12)
        return temperatura

    def calcular_irradianca_temperatura_desempenho(self, latitude, longitude, altitude,
                                                   potencia_instalada_kwp, eficiencia,
                                                   potencia_max_inversor_kw, energia_desejada,
                                                   index_mensal):
        """
        :param latitude: distância da linha do Equador
        :param longitude: distância do Grenwich
        :param altitude: altura do ponto escolhido em relação ao nivel do mar
        :param potencia_instalada_kwp: potência do inversor
        :param eficiencia: do inversor
        :param potencia_max_inversor_kw: maior potencia despachada do inversor
        :param energia_desejada: energia calculada horariamente para resultar na energia mensal da BDGD
        :return:
        """

        site = location.Location(latitude, longitude, altitude)

        rec_mensal = 0
        rec_diario = 0
        index_dia = 0
        if int(index_mensal) < 1:
            rec_mensal = index_mensal
            rec_mensal = 1

        if int(index_dia) < 1:
            rec_diario = index_dia
            rec_diario = 1

        # Ajuste para garantir que rec_diario nunca seja 0
        index_3 = f'{int(rec_mensal):02d}' if rec_mensal > 0 else '01'
        index_4 = f'{int(rec_diario):02d}' if rec_diario > 0 else '01'

        times = pd.date_range(f'2023-{index_3}-{index_4}', f'2023-{index_3}-{index_4} 23:59',
                              freq='15min', tz='America/Cuiaba')

        """Calcular a irradiança global horizontal (GHI), difusa (DHI) e direta (DNI)"""
        solar_position = site.get_solarposition(times)
        irradiance = site.get_clearsky(times)

        """ Estimar a temperatura para cada 15 minutos"""
        temperatura = [self.estimar_temperatura(minutos.hour, latitude) for minutos in times]

        """Calcular a potência gerada com base na irradiância (GHI)"""
        potencia_gerada = self.calcular_potencia_gerada(irradiance['ghi'], potencia_instalada_kwp,
                                                   eficiencia)

        """Ajuste da potência gerada para atingir a energia desejada"""
        energia_total_gerada = potencia_gerada.sum()
        fator_ajuste = (energia_desejada[index_mensal] / 30) / energia_total_gerada

        """Ajustar a potência gerada para atingir a energia desejada"""
        potencia_gerada_ajustada = potencia_gerada * fator_ajuste

        """Aplicar a saturação do inversor"""
        potencia_gerada_limitada = self.aplicar_saturacao_inversor(potencia_gerada_ajustada,
                                                              potencia_max_inversor_kw)

        return irradiance[
            'ghi'].tolist(), temperatura, potencia_gerada_ajustada.tolist(), potencia_gerada_limitada.tolist()

    def lines(self):
        """Cria comandos no formato desejado para o OpenDSS"""
        dados = self.consulta_banco()


        ctmts_processados = {}

        for index, coluna in enumerate(dados):
            cod_id = coluna[0]
            pac = coluna[1]
            ctmt = coluna[2]
            fas_con = coluna[3]
            ten_con = coluna[4]
            potencia_instalada_kwp = coluna[5]
            potencia_max_inversor_kw = coluna[5]
            energia_desejada = coluna[8:20]
            ceg_gd = coluna[7]

            ctmt_folder = 0

            if ceg_gd[:2] == ('GD' or 'UFV'):
                if ctmt not in ctmts_processados:
                    ctmt_folder = os.path.join(base_dir, str(ctmt))
                    os.makedirs(ctmt_folder, exist_ok=True)

                for index_mensal, mensal in enumerate(energia_desejada):
                    """ Para cada energia gerada mensalmente criar um arquivo de curva de geração"""

                    mensal_folder = os.path.join(ctmt_folder, str(f'geração_shape_mes_{index_mensal + 1}'))
                    os.makedirs(mensal_folder, exist_ok=True)

                    index_dia = 1
                    diario_filename = f'geração_shape_dia_{1}.txt'
                    file_path = os.path.join(mensal_folder, diario_filename)

                    with open(file_path, 'a') as file:
                        (irradiance, temperatura, potencia_gerada_ajustada, potencia_gerada_limitada) = (
                            self.calcular_irradianca_temperatura_desempenho(
                                self.latitude,
                                self.longitude,
                                self.altitude,
                                potencia_instalada_kwp,
                                self.eficiencia,
                                potencia_max_inversor_kw,
                                energia_desejada,
                                index_mensal
                            ))



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

    base_dir = r'C:\MODELAGEM_PAINEIS_FOTOVOLTAICOS_ADICIONAIS_BAIXA_TENSÃO_BDGD_2023_ENERGISA'
    latitude = -15.59583
    longitude = -56.09694
    altitude = 400
    eficiencia = 0.18
    gamma = -0.004
    alpha = 0.001


    # Criar uma instância da classe DatabaseQuery
    db_query = DatabaseQuery(host, port, dbname, user, password,
                             latitude, longitude, altitude,
                             eficiencia, gamma, alpha, base_dir)

    # Conectar ao banco de dados
    db_query.connect()

    # Gerar comandos para o OpenDSS
    db_query.lines()

    # Fechar a conexão com o banco de dados
    db_query.close()
