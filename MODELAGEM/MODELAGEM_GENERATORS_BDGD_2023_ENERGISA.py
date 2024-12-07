import psycopg2
import matplotlib.pyplot as plt
import pandas as pd
import pvlib
import numpy as np
import os
from pvlib import location
from geopy.geocoders import Nominatim
import requests

from MODELAGEM.eficiencia import aplicar_saturacao_inversor
from MODELAGEM.expressão_inversor import eficiencia, potencia_max_inversor_kw, energia_desejada, \
    calcular_potencia_gerada


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
                        ugmt.cod_id, ugmt_tab.pac, ugmt_tab.ctmt, ugmt_tab.fas_con,
                        ugmt_tab.ten_con, ugmt_tab.pot_inst, ugmt_tab.cep,
                        ugmt_tab.ceg_gd,
                        ugmt_tab.ene_01, ugmt_tab.ene_02, ugmt_tab.ene_03,
                        ugmt_tab.ene_04, ugmt_tab.ene_05, ugmt_tab.ene_06,
                        ugmt_tab.ene_07, ugmt_tab.ene_08, ugmt_tab.ene_09,
                        ugmt_tab.ene_10, ugmt_tab.ene_11, ugmt_tab.ene_12
           
                FROM 
                    ssdmt;       
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
            energia_desejada = linha[9:20]


            if ctmt not in ctmts_processados:
                ctmt_folder = os.path.join(base_dir, str(ctmt))
                os.makedirs(ctmt_folder, exist_ok=True)

            for index, mensal in enumerate(energia_desejada):
                """ Para cada energia gerada mensalmente criar um arquivo de curva de geração"""
                mensal_filename = f'geração_shape_{index + 1}.txt'
                file_path = os.path.join(ctmt_folder, mensal_filename)

                with open(file_path, 'a') as file:
                    """
                          ESTA FUNÇÃO ESTÁ IMPLEMENTANDO A GERAÇÃO DE PAINÉIS FOTOVOLTAICOS PARA A BDGD_2023 ENERGISA
                          NA MÉDIA E NA BAIXA TENSÃO, CONSIDERANDO O LIQUIDO (GERADO - CONSUMIDO) MEDIDO PELOS 
                          MEDIDORES DE ENERGIA NA MÉDIA E NA BAIXA TENSÃO NOS ALIMENTADORES, DE MODO QUE 
                          A GENERALIZAÇÃO SE DÁ NO MOMENTO EM QUE APROXIMAMOS A CURVA DE GERAÇÃO DISTRIBUIDA A PARTIR DESTE
                          LIQUIDO E NÃO REALMENTE DO GERADO, ESTA SERIA A ÚNICA LIMITAÇÃO.
        
                          A MODELAGEM ABAIXO LEVA EM CONTA A TEMPERATURA MÉDIA DE MATO GROSSO TENDO EM VISTA 
                          QUE NÃO HÁ A NECESSIDADE DE UM RIGOR NESTA QUESTÃO PORQUE A TEMPERATURA AMBIENTE SÓ COMEÇA 
                          A INFLUENCIAR FORTEMENTE A EFICIENCIA DO INVERSOR PARA VARIAÇÕES ENORMES.ADEMAIS, 
                          FORAM CONSIDERADOS IRRADIÂNCIA NA EFICIÊNCIA, POSIÇÃO GEOGRAFICA, HORARIO DO DIA,
                          MÊS, POTENCIA NOMINAL DO INVERSOR E EFICIÊNCIA MÁXIMA
                      """

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
                        t_min = 10
                        temperatura = (t_max + t_min) / 2 + (t_max - t_min) / 2 * np.sin(np.pi * (hora - 6) / 12)
                        return temperatura

                    def calcular_irradianca_temperatura_desempenho(self, latitude, longitude, altitude,
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

                        site = location.Location(latitude, longitude, altitude=altitude)

                        times = pd.date_range(f'2023-01-01', '2023-12-31 23:59', freq='15T', tz='America/Cuiaba')

                        # Calcular a irradiança global horizontal (GHI), difusa (DHI) e direta (DNI)
                        solar_position = site.get_solarposition(times)
                        irradiance = site.get_clearsky(times)

                        # Estimar a temperatura para cada 15 minutos
                        temperatura = [estimar_temperatura(minutos.hour, latitude) for minutos in times]

                        # Calcular a potência gerada com base na irradiância (GHI)
                        potencia_gerada = calcular_potencia_gerada(irradiance['ghi'], potencia_instalada_kwp, eficiencia)

                        # Ajuste da potência gerada para atingir a energia desejada
                        energia_total_gerada = potencia_gerada.sum()
                        fator_ajuste = energia_desejada / energia_total_gerada

                        # Ajustar a potência gerada para atingir a energia desejada
                        potencia_gerada_ajustada = potencia_gerada * fator_ajuste

                        # Aplicar a saturação do inversor
                        potencia_gerada_limitada = aplicar_saturacao_inversor(potencia_gerada_ajustada,
                                                                              potencia_max_inversor_kw)

                        return irradiance, temperatura, potencia_gerada_ajustada

                    # Conversão para latitude e Longitude
                    def obter_coordenadas_por_cep(cep):
                        geolocator = Nominatim(user_agent="geoapiExercises")

                        # O geocoder retorna um objeto com as informações do local
                        location = geolocator.geocode(cep)

                        if location:
                            # Retorna a latitude e Longitude
                            return location.latitude, location.longitude
                        else:
                            return None, None

                    # Cordenadas extraidas
                    latitude, longitude = obter_coordenadas_por_cep(cep)

                    altitude = 400

                    irradiance, temperatura, potencia_gerada_ajustada = calcular_irradianca_temperatura_desempenho(latitude,
                                                                                                        longitude, altitude,
                                                                                         potencia_instalada_kwp, eficiencia,
                                                                                 potencia_max_inversor_kw, energia_desejada)


                    mapa_fases = {
                        'ABC': '.1.2.3', 'ACB': '.1.3.2', 'BAC': '.1.2.3', 'BCA': '.1.2.3', 'CAB': '.1.2.3', 'CBA': '.1.2.3',
                        'ABCN': '.1.2.3', 'ACBN': '.1.2.3', 'BACN': '.1.2.3', 'BCAN': '.1.2.3', 'CABN': '.1.2.3',
                        'CBAN': '.1.2.3',
                        'ABN': '.1.2', 'ACN': '.1.3', 'BAN': '.1.2', 'CAN': '.1.3', 'A': '.1', 'B': '.2', 'C': '.3', 'AN': '.1',
                        'BA': '.1.2', 'BN': '.2', 'CN': '.3', 'AB': '.1.2', 'AC': '.1.3', 'BC': '.2.3',
                        'CNA': '.1', 'ANB': '.1.2', 'BNC': '.2.3', 'CA': '.1.3',
                    }
                    rec_fases = mapa_fases[fas_con]

                    if ten_con == 17:
                        tensao = 440
                    elif ten_con == 15:
                        tensao = 380
                    elif ten_con == 13:
                        tensao = 240
                    elif ten_con == 11:
                        tensao = 230
                    elif ten_con == 10:
                        tensao = 220
                    elif ten_con == 6:
                        tensao = 127

                    # Gerar o comando para o OpenDSS
                    command_pvsystem = f"""
                        New xycurve.mypvst_{cod_id} npts = {} xarray = {} yarray = {} !curva de desempenho do painel em função da temperatura (colocar uma curva constante )
                        New xycurve.myeff_{cod_id} npts = {} xarray = {} yarray = {}  ! eficiência do sistema para diferentes valores de carga
                        New loadshape.myirrad_{cod_id} npts = {} interval = {} mult = {} ! distribui os valores da irradição solar ao longo das 24 horas do dia e noite 
                        New tshape.mytemp_{cod_id} npts = {} interval = {} temp = {}  ! define a temperatura ambiente ao longo das 24 horas
                        New pvsystem.pv_{} phases = {} conn = {} bus1 = {} kv = {} kva = {} pmpp = {} pf = {} %cutin = {} %cutout = {} varfollowinverter = {} effcurve = myeff_{cod_id} p-tcurve = mypvst_{cod_id} daily = myirrad_{cod_id} tdaily = mytemp_{cod_id}
                        """
                    command_pvsystem = f"""
                        ! Generator-ctmt: {ctmt}
                        New Generator.{cod_id} Bus1 = {pac}{rec_fases} kw = {pot_inst} fp = {} kva = {} kv = {int(tensao) / 1000} xdp = {} xdpp = {} h = {}
                        ~ conn = {}
                        """


                    # Escrever o comando no arquivo.dss
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
