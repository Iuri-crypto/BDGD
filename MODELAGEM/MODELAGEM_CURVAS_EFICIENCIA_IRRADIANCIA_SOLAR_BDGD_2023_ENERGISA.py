import psycopg2
import matplotlib.pyplot as plt
import pandas as pd
import pvlib
import numpy as np
import os
from pvlib import location
from geopy.geocoders import Nominatim
import requests

#from MODELAGEM.MODELAGENS_ERRADAS.modelagem_ctmt_linhas_2 import ctmt_value
#from MODELAGEM.eficiencia import aplicar_saturacao_inversor
#from MODELAGEM.expressão_inversor import eficiencia, potencia_max_inversor_kw, energia_desejada, \
 #   calcular_potencia_gerada


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
            # Consulta a tabela SSDMT para extrair as colunas especificadas
            query = """
                SELECT 
                        ugmt_tab.cod_id, ugmt_tab.pac, ugmt_tab.ctmt, ugmt_tab.fas_con,
                        ugmt_tab.ten_con, ugmt_tab.pot_inst, ugmt_tab.cep,
                        ugmt_tab.ceg_gd,
                        ugmt_tab.ene_01, ugmt_tab.ene_02, ugmt_tab.ene_03,
                        ugmt_tab.ene_04, ugmt_tab.ene_05, ugmt_tab.ene_06,
                        ugmt_tab.ene_07, ugmt_tab.ene_08, ugmt_tab.ene_09,
                        ugmt_tab.ene_10, ugmt_tab.ene_11, ugmt_tab.ene_12,
                        ugmt_tab.dem_cont

                FROM 
                    ugmt_tab;       
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

        # Caminho principal para salvar as subpastas
        base_dir = r'C:\MODELAGEM_GERADORES_MÉDIA_TENSÃO_BDGD_2023_ENERGISA'

        # Dicionário para armazenar os ctmt já processados
        ctmts_processados = {}

        # Iterar sobre os dados e gerar uma subpasta para cada CTMT
        for index, linha in enumerate(dados):
            cod_id = linha[0]
            pac = linha[1]
            ctmt = linha[2]
            fas_con = linha[3]
            ten_con = linha[4]
            potencia_instalada_kwp = linha[5]
            cep = linha[6]
            potencia_max_inversor_kw = linha[5]
            energia_desejada = linha[8:20]
            demanda_contratada = linha[20]

            if ctmt not in ctmts_processados:
                ctmt_folder = os.path.join(base_dir, str(ctmt))
                os.makedirs(ctmt_folder, exist_ok=True)

            for index_mensal, mensal in enumerate(energia_desejada):
                """ Para cada energia gerada mensalmente criar um arquivo de curva de geração"""
                mensal_folder = os.path.join(ctmt_folder, str(f'geração_shape_mes_{index_mensal + 1}'))
                os.makedirs(mensal_folder, exist_ok=True)

                for index_dia in range(30):
                    diario_filename = f'geração_shape_dia_{index_dia + 1}.txt'
                    file_path = os.path.join(mensal_folder, diario_filename)

                    with open(file_path, 'a') as file:
                        """
                              IMPLEMENTAÇÃO DE TODAS AS CURVAS PARA PAINEIS SOLARES
                          """

                        def calcular_potencia_gerada(irradiancia, potencia_instalada_kwp, eficiencia):
                            """
                            :param irradiancia: quantidade em wh/m2 de sol
                            :param potencia_instalada_kwp: potência do inversor solar
                            :param eficiencia: limitações e saturações do inversor
                            :return:
                            """
                            potencia = potencia_instalada_kwp * (irradiancia / 1000) * eficiencia
                            return potencia

                        def aplicar_saturacao_inversor(potencia_gerada, potencia_max_inversor_kw):
                            """
                            :param potencia_gerada: diferência entre a quantidade de potência que entra - perdas, saturações...
                            :param potencia_max_inversor_kw: maior quantidade de potência que o inversor consegue injetar nna rede
                            :return:
                            """
                            return np.minimum(potencia_gerada, potencia_max_inversor_kw)

                        def estimar_temperatura(hora, latitude):
                            """
                            :param hora: hora do dia de simulação do respectivo ano escolhido
                            :param latitude:  a temperatura varia com a latitude (distancia até a linha do Equador)
                            :return:
                            """
                            t_max = 40
                            t_min = 15
                            temperatura = (t_max + t_min) / 2 + (t_max - t_min) / 2 * np.sin(np.pi * (hora - 6) / 12)
                            return temperatura

                        def calcular_irradianca_temperatura_desempenho(latitude, longitude, altitude,
                                                                       potencia_instalada_kwp, eficiencia,
                                                                       potencia_max_inversor_kw, energia_desejada):
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

                            site = location.Location(latitude, longitude, altitude=400)

                            rec_mensal = 0
                            rec_diario = 0
                            if int(index_mensal) < 1:
                                rec_mensal = index_mensal
                                rec_mensal = 1

                            if int(index_dia) < 1:
                                rec_diario = index_dia
                                rec_diario = 1

                            # Ajuste para garantir que rec_diario nunca seja 0
                            index_3 = f'{int(rec_mensal):02d}' if rec_mensal > 0 else '01'  # Garante que o mês não seja 0
                            index_4 = f'{int(rec_diario):02d}' if rec_diario > 0 else '01'  # Garante que o dia não seja 0

                            times = pd.date_range(f'2023-{index_3}-{index_4}', f'2023-{index_3}-{index_4} 23:59', freq='15min', tz='America/Cuiaba')

                            """Calcular a irradiança global horizontal (GHI), difusa (DHI) e direta (DNI)"""
                            solar_position = site.get_solarposition(times)
                            irradiance = site.get_clearsky(times)

                            """ Estimar a temperatura para cada 15 minutos"""
                            temperatura = [estimar_temperatura(minutos.hour, latitude) for minutos in times]

                            """Calcular a potência gerada com base na irradiância (GHI)"""
                            potencia_gerada = calcular_potencia_gerada(irradiance['ghi'], potencia_instalada_kwp,
                                                                       eficiencia)

                            """Ajuste da potência gerada para atingir a energia desejada"""
                            energia_total_gerada = potencia_gerada.sum()
                            fator_ajuste = (energia_desejada[index_mensal] / 30) / energia_total_gerada

                            """Ajustar a potência gerada para atingir a energia desejada"""
                            potencia_gerada_ajustada = potencia_gerada * fator_ajuste

                            """Aplicar a saturação do inversor"""
                            potencia_gerada_limitada = aplicar_saturacao_inversor(potencia_gerada_ajustada,
                                                                                  potencia_max_inversor_kw)

                            return irradiance['ghi'].tolist(), temperatura, potencia_gerada_ajustada.tolist(), potencia_gerada_limitada.tolist()

                        # """Conversão para latitude e Longitude"""
                        # def obter_coordenadas_por_cep(cep):
                        #     geolocator = Nominatim(user_agent="meu_script_de_geolocalizacao_2023")
                        #
                        #     """O geocoder retorna um objeto com as informações do local"""
                        #     location = geolocator.geocode(cep, timeout=10)
                        #
                        #     if location:
                        #         # Retorna a latitude e Longitude
                        #         return location.latitude, location.longitude
                        #     else:
                        #         return None, None

                        """ As coordenadas foram baseadas em Cuiaba para os calculos"""
                        latitude = -15.59583
                        longitude = -56.09694
                        altitude = 400
                        """ Eficiencia media de uma painel fotovoltaico """
                        eficiencia = 0.18

                        irradiance, temperatura, potencia_gerada_ajustada, potencia_gerada_limitada  = calcular_irradianca_temperatura_desempenho(
                            latitude,
                            longitude, altitude,
                            potencia_instalada_kwp, eficiencia,
                            potencia_max_inversor_kw, energia_desejada)

                        """ Cálculo da eficiência em função da temperatura para os inversores solares """
                        gamma = -0.004                                   # Coeficiente de temperatura do painel (em %/°C)
                        alpha = 0.002                                    # Coeficiente de variação da eficiência do inversor em (em %/°C)
                        eficiencia_maxima_inversor = 0.98
                        temperatura_referencia = [25 for _ in range(96)]
                        potencia_corrigida = [p_g_l * (1 + gamma * (t - t_r))
                                              for t, t_r, p_g_l in zip(temperatura, temperatura_referencia, potencia_gerada_limitada)]

                        """ Calculando a eficiencia do inversor em função da temperatura """
                        eficiencia_inversor = [eficiencia_maxima_inversor - alpha * (t - t_r)
                                               for t, t_r in zip(temperatura, temperatura_referencia)]


                        """ """

                        # command_pvsystem = f"""
                        #     eficiencia_vs_temperatura = {}
                        #     eficiencia_vs_potencia_inversor = {}
                        #     valores_irradianca_intervalos_15m_diario = {}
                        #     valores_temperatura_intervalos_15m_diario = {}

                        #   """
                        potencia_pu = [
                            pot_limitada / pot_ajustada if pot_ajustada != 0 else 0
                            for pot_limitada, pot_ajustada in zip(potencia_gerada_limitada, potencia_gerada_ajustada)
                        ]
                        ten = 13.8
                        if ten_con == 49:
                            ten = 13.8
                        if ten_con == 72:
                            ten = 34.5
                        command_pvsystem = f"""
                            New xycurve.mypvst_{cod_id} npts = {96} xarray = {[temperatura]} yarray = {[eficiencia_inversor]} !curva de desempenho do painel em função da temperatura (colocar uma curva constante )
                            New xycurve.myeff_{cod_id} npts = {96} xarray = {[potencia_pu]} yarray = {[eficiencia_inversor]}  ! eficiência do sistema para diferentes valores de carga
                            New loadshape.myirrad_{cod_id} npts = {96} interval = 15min mult = {[irradiance]} ! distribui os valores da irradição solar ao longo das 24 horas do dia e noite
                            New tshape.mytemp_{cod_id} npts = {96} interval = 15min temp = {[temperatura]}  ! define a temperatura ambiente ao longo das 24 horas
                            New pvsystem.pv_{cod_id} phases = {len(fas_con)} conn = estrela bus1 = {pac} kv = {ten} kva = {max(potencia_gerada_ajustada)} pmpp = {max(potencia_gerada_ajustada)} pf = {1} %cutin = {0.00005} %cutout = {0.00005} varfollowinverter = Yes effcurve = myeff_{cod_id} p-tcurve = mypvst_{cod_id} daily = myirrad_{cod_id} tdaily = mytemp_{cod_id}
                            """

                        file.write(command_pvsystem + "\n")

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
    db_query.lines()

    # Fechar a conexão com o banco de dados
    db_query.close()
