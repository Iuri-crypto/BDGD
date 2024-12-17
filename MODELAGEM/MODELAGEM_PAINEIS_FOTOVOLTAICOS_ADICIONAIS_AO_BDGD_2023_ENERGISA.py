import psycopg2
import pandas as pd
import numpy as np
import os
from pvlib import location


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

    def lines(self):
        """Cria comandos no formato desejado para o OpenDSS"""
        dados = self.consulta_banco()

        # Caminho principal para salvar as subpastas
        base_dir = r'C:\MODELAGEMs_PAINEIS_FOTOVOLTAICOS_BAIXA_TENSÃO_BDGD_2023_ENERGISA'

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
            ceg_gd = linha[7]

            if ceg_gd[:2] == ('GD' or 'UFV'):
                if ctmt not in ctmts_processados:
                    ctmt_folder = os.path.join(base_dir, str(ctmt))
                    os.makedirs(ctmt_folder, exist_ok=True)

                for index_mensal, mensal in enumerate(energia_desejada):
                    """ Para cada energia gerada mensalmente criar um arquivo de curva de geração"""
                    mensal_folder = os.path.join(ctmt_folder, str(f'geração_shape_mes_{index_mensal + 1}'))
                    os.makedirs(mensal_folder, exist_ok=True)

                    for index_dia in range(1):
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
                                temperatura = (t_max + t_min) / 2 + (t_max - t_min) / 2 * np.sin(
                                    np.pi * (hora - 6) / 12)
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

                                times = pd.date_range(f'2023-{index_3}-{index_4}', f'2023-{index_3}-{index_4} 23:59',
                                                      freq='15min', tz='America/Cuiaba')

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

                                return irradiance[
                                    'ghi'].tolist(), temperatura, potencia_gerada_ajustada.tolist(), potencia_gerada_limitada.tolist()

                            """ As coordenadas foram baseadas em Cuiaba para os calculos"""
                            latitude = -15.59583
                            longitude = -56.09694
                            altitude = 400
                            """ Eficiencia media de uma painel fotovoltaico """
                            eficiencia = 0.18

                            irradiance, temperatura, potencia_gerada_ajustada, potencia_gerada_limitada = calcular_irradianca_temperatura_desempenho(
                                latitude,
                                longitude, altitude,
                                potencia_instalada_kwp, eficiencia,
                                potencia_max_inversor_kw, energia_desejada)

                            """ Cálculo da eficiência em função da temperatura para os inversores solares """
                            gamma = -0.004  # Coeficiente de temperatura do painel (em %/°C)
                            alpha = 0.001  # Coeficiente de variação da eficiência do inversor em (em %/°C)
                            eficiencia_maxima_inversor = 0.98
                            temperatura_referencia = [25 for _ in range(96)]
                            potencia_corrigida = [p_g_l * (1 + gamma * (t - t_r))
                                                  for t, t_r, p_g_l in
                                                  zip(temperatura, temperatura_referencia, potencia_gerada_limitada)]

                            """ Calculando a eficiencia do inversor em função da temperatura """
                            eficiencia_inversor = [eficiencia_maxima_inversor - alpha * (t - t_r)
                                                   for t, t_r in zip(temperatura, temperatura_referencia)]

                            """ """

                            potencia_pu = [
                                pot_limitada / pot_ajustada if pot_ajustada != 0 else 0
                                for pot_limitada, pot_ajustada in
                                zip(potencia_gerada_limitada, potencia_gerada_ajustada)
                            ]

                            # Função de cálculo da eficiência do inversor com base na potência gerada
                            def calcular_eficiencia(potencia_gerada, potencia_gerada_limitada):
                                """
                                Calcula a eficiência do inversor baseada na potência gerada.
                                A eficiência depende de faixas de potência:
                                - < 0.2: 0.85
                                - 0.2 a 0.6: 0.9
                                - 0.6 a 1: 0.98
                                Para valores intermediários, a interpolação é usada para suavizar as transições.
                                """
                                # Normaliza a potência gerada em relação à potência máxima
                                if max(potencia_gerada_limitada) != 0:
                                    fator_potencia = potencia_gerada / max(potencia_gerada_limitada)
                                else:
                                    fator_potencia = 0

                                # Definindo as faixas de potência
                                if fator_potencia < 0.2:
                                    eficiencia = 0.85
                                elif 0.2 <= fator_potencia < 0.6:
                                    # Interpolação linear entre 0.2 e 0.6 para transição suave
                                    eficiencia = 0.85 + (fator_potencia - 0.2) * (0.9 - 0.85) / (0.6 - 0.2)
                                elif 0.6 <= fator_potencia < 1.0:
                                    # Interpolação linear entre 0.6 e 1 para transição suave
                                    eficiencia = 0.9 + (fator_potencia - 0.6) * (0.98 - 0.9) / (1.0 - 0.6)
                                else:
                                    eficiencia = 0.98

                                return eficiencia

                            potencia_gerada_limitada_np = np.array(potencia_gerada_limitada)

                            eficiencia_inversor_pot = []
                            for pot in potencia_gerada_limitada_np:
                                eficiencia_base = calcular_eficiencia(pot, potencia_gerada_limitada)

                                eficiencia_completa = eficiencia_base

                                eficiencia_inversor_pot.append(eficiencia_completa)

                            ten = 13.8 if ten_con == 49 else (34.5 if ten_con == 72 else 13.8)

                            irradiance = [irr / max(irradiance) for irr in irradiance]

                            temperatura = " ".join(str(temp) for temp in temperatura)
                            eficiencia_inversor = " ".join(str(efi) for efi in eficiencia_inversor)
                            potencia_pu = " ".join(str(pot) for pot in potencia_pu)
                            irradiance = " ".join(str(irr) for irr in irradiance)

                            mapa_fases = {
                                'ABC': '.1.2.3', 'ACB': '.1.3.2', 'BAC': '.1.2.3', 'BCA': '.1.2.3', 'CAB': '.1.2.3',
                                'CBA': '.1.2.3',
                                'ABCN': '.1.2.3', 'ACBN': '.1.2.3', 'BACN': '.1.2.3', 'BCAN': '.1.2.3',
                                'CABN': '.1.2.3',
                                'CBAN': '.1.2.3',
                                'ABN': '.1.2', 'ACN': '.1.3', 'BAN': '.1.2', 'CAN': '.1.3', 'A': '.1', 'B': '.2',
                                'C': '.3', 'AN': '.1',
                                'BA': '.1.2', 'BN': '.2', 'CN': '.3', 'AB': '.1.2', 'AC': '.1.3', 'BC': '.2.3',
                                'CNA': '.1', 'ANB': '.1.2', 'BNC': '.2.3', 'CA': '.1.3', 'N': '.0', 'BCN': '.2.3.0'
                            }
                            rec_fases = mapa_fases[fas_con]

                            t = temperatura
                            ef = eficiencia_inversor
                            pote = potencia_pu
                            irr = irradiance

                            command_pvsystem = (
                                f'New xycurve.mypvst_{cod_id} npts = {1} xarray = [{25}] yarray = [{1}]\n '
                                f'New xycurve.myeff_{cod_id} npts = {1} xarray = [{1}] yarray = [{1}]\n  '
                                f'New loadshape.myirrad_{cod_id} npts = {1} interval = 15 mult = [{1}]\n '
                                f'New tshape.mytemp_{cod_id} npts = {1} interval = 15 temp = [{25}]\n  '
                                f'New pvsystem.pv_{cod_id} phases = {len(fas_con)} conn = wye bus1 = {pac}{rec_fases}\n '
                                f'~ kv = {ten} kva = {max(potencia_gerada_ajustada)} pmpp = {max(potencia_gerada_ajustada)}\n '
                                f'~ pf = {1} %cutin = {0.00005} %cutout = {0.00005} varfollowinverter = Yes effcurve = myeff_{cod_id}\n '
                                f'~ p-tcurve = mypvst_{cod_id} daily = myirrad_{cod_id} tdaily = mytemp_{cod_id}'

                            )
                            file.write(command_pvsystem + "\n\n")

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
