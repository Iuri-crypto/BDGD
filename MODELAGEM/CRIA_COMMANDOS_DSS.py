import json
import os
import numpy as np
import py_dss_interface

dss = py_dss_interface.DSSDLL()


class Fluxo_Potencia:
    """ Classe para calcular o fluxo de potência nos alimentadores """

    def __init__(self, alimentadores_recebidos, caminhos_model, circuito_pu, loads_mult, irradiancia_96, feederhead,
                 caminhos_geration_shape_fotovoltaico, medidores_pnt, curva_de_carga_pip,
                 modelagem_curva_carga):
        """ Inicializa a classe Fluxo Potencia """
        self.alimentadores_recebidos = alimentadores_recebidos
        self.caminhos_model = caminhos_model
        self.circuito_pu = circuito_pu
        self.loads_mult = loads_mult
        self.irradiancia_96 = irradiancia_96
        self.feederhead = feederhead
        self.caminhos_geration_shape_fotovoltaico = caminhos_geration_shape_fotovoltaico
        self.medidores = medidores_pnt
        self.curva_de_carga_pip = curva_de_carga_pip
        self.modelagem_curva_carga = modelagem_curva_carga



        """ Chamando a função principal que controla tudo """
        self.envia_comandos_opendss()


    def listar_pastas(self):
        """ Esta função guarda o nome de todos os alimentadores """
        pastas = list()

        """ verifica se o caminho é um diretório """
        if os.path.isdir(self.alimentadores_recebidos):

            """ Lista os itens do diretório """
            for item in os.listdir(self.alimentadores_recebidos):

                """ Cria o caminho do item  """
                caminho = os.path.join(self.alimentadores_recebidos, item)

                """ Verifica se o item é um diretório """
                if os.path.isdir(caminho):
                    pastas.append(item)

        return np.array(pastas)



    def busca_pastas(self, feederhead):
        """ Esta função envia comandos de compile para o OpenDSS """


        """ Percorre cada diretório para procurar as pastas """
        for path in self.caminhos_model:

            """ Define o caminho completo da pasta """
            caminho = os.path.join(path, str(feederhead))

            """ Verifica se a pasta existe no diretório """
            if os.path.isdir(caminho):

                """ Agora pega todos os arquivos dentro desta pasta """
                for arquivo in os.listdir(caminho):
                    caminho_arquivo = os.path.join(caminho, arquivo)

                    """ Verifica se é um arquivo e não uma pasta """
                    if os.path.isfile(caminho_arquivo):

                        """ Substituir barras simples por barras duplas
                        para evitar erros de compilação de diretorios
                        as barras estão duplicadas mas é desta forma que
                        o python entende uma unica barra
                        """
                        caminho_arquivo = caminho_arquivo.replace('/', '\\')

                        """ GERANDO COMANDOS PARA O OPENDSS COMPILAR """
                        dss.text(f'Compile [{caminho_arquivo}]')



    def edit_volt_alimentador(self):
        """ Esta funcão permite a edição da tensão do alimentador para outro valor """
        dss.text(f"edit Vsource.SOURCE pu={self.circuito_pu}")



    def load_mult(self):
        """ Caso queria alterar a potência de todas as cargas
           usa-se o multiplicador de carga. Uma ideia seria usa-lo
           para simular o incremento de carga com o passar dos
           anos no Estado de Mato Grosso
        """
        dss.text(f"Set loadmult = {self.loads_mult}")



    def busca_max_min_voltages(self):
        """ Esta função encontra os valores máximos e minímos das tensões dos nós do circuito """

        v_max_pu = max(dss.circuit_all_bus_vmag_pu())
        v_min_pu = min(dss.circuit_all_bus_vmag_pu())

        return v_max_pu, v_min_pu



    def total_power(self):
        """ Esta função encontra as potência ativas e reativas que estão fluindo
            pelo alimentador.ATENÇÃO: por padrão no OpenDSS tais valores são positivos se
            estiverem entrando no elemento e negativos se estiverem saindo do
            elemento
        """
        kW_alimentador = dss.circuit_total_power()[0]
        kVar_alimentador = dss.circuit_total_power()[1]

        return kW_alimentador, kVar_alimentador



    def adiciona_paineis_fotovoltaicos(self, cod_id, fas_con, bus1, kv, kva, pmpp, pf):
        """ Envia comandos de texto de paineis """

        dss.text(f"New xycurve.mypvst_{cod_id} npts = 4 xarray=[0 25 75 100] yarray=[1.2 1.0 0.8 0.6]")
        dss.text(f"New xycurve.myeff_{cod_id} npts = 4  xarray=[.1 .2 .4 1.0] yarray=[.86 .9 .93 .97]")
        dss.text(f"New loadshape.myirrad_{cod_id} npts = 1 interval = 1 mult = [1]")
        dss.text(f"New tshape.mytemp_{cod_id} npts = 1 interval = 1 temp = [25]")
        dss.text(f"New pvsystem.pv_{cod_id} phases = {len(fas_con)} conn = wye bus1 = {bus1}")
        dss.text(f"~ kv = {kv} kva = {kva} pmpp = {pmpp}")
        dss.text(f"~ pf = {pf} %cutin = 0.00005 %cutout = 0.00005 varfollowinverter = Yes effcurve = myeff_{cod_id}")
        dss.text(f"~ p-tcurve = mypvst_{cod_id} daily = myirrad_{cod_id} tdaily = mytemp_{cod_id}")



    def busca_dados_paineis_fotovoltaicos(self, mes, nome_alimentador):
        """ Esta função adiciona paines fotovoltaicos no alimentador  """


        """ Caminhos de geração da baixa e da media para gd """
        caminho_gd = self.caminhos_geration_shape_fotovoltaico
        for caminho in caminho_gd:

            """ verifica se é um diretório """
            if os.path.isdir(caminho):

                """ Cria um caminho para o alimentador selecionado """
                caminho_create = os.path.join(caminho, str(nome_alimentador))

                """ Verifica se a pasta existe """
                if os.path.isdir(caminho_create):

                    """ Entra na primeira pasta porque simularemos apenas para 1 mes """
                    geracoes_meses = os.listdir(caminho_create)
                    if geracoes_meses:

                        primeiro_mes = os.path.join(caminho_create, str(geracoes_meses[mes]))

                        """ Verifica se a pasta de geração de meses existe """
                        if os.path.isdir(primeiro_mes):

                            """ Agora percorre todos os arquivos json dentro da pasta """
                            for painel in os.listdir(primeiro_mes):

                                """ Garante que é um arquivo json """
                                if painel.endswith('.json'):
                                    caminho_json = os.path.join(primeiro_mes, painel)

                                    """ Lê o arquivo json """
                                    with open(caminho_json, 'r') as f:

                                        """ Carrega o conteúdo do arquivo """
                                        dados = json.load(f)

                                        """ Extração de dados do dicionario """
                                        cod_id = dados.get("cod_id")
                                        fas_con = dados.get("fas_con")
                                        bus1 = dados.get("bus1")
                                        kv = dados.get("kv")
                                        kva = dados.get("kva")
                                        pmpp = dados.get("pmpp")
                                        pf = dados.get("pf")

                                """ Chamado para inserir paineis fotovoltaicos no circuito """
                                self.adiciona_paineis_fotovoltaicos(cod_id, fas_con, bus1, kv, kva, pmpp, pf)



    def inserir_energy_meters(self, respost_a):
        if respost_a == 'não':
            print(f'Não será feito análise de perdas não técnicas no alimentador: {self.feederhead}')
        else:

            """ Percorrendo a lista de medidores """
            for medidor in self.medidores:
                nome_medidor, latitude, longitude, cod_id_linha = medidor

                """ Inserindo os medidores de energia (EnergyMeters) """
                dss.text(f"New Energymeter.{nome_medidor}  Line.{cod_id_linha}  1")




    def aplica_curvas_carga_geracao(self, irradiancia_96):
        """ Esta função vai rodar para cada ponto da curva tanto de geração como de carga """





        """ Este comando faz o OpenDSS conseguir calcular as tensões de todos os 
         barramentos em unidades [PU] ele faz automaticamente o reconhecimento 
         de qual base de tensão usar na hora da divisão """
        dss.text('set VoltageBases = "1" ')
        dss.text('CalcVoltageBases')
        dss.text('set maxiterations=20')

        """ Este comando soluciona o fluxo de potência 
        por padrão o OpenDSS usa o método das correntes """
        dss.solution_solve()

        """ Este comando é para ativar a leitura dos EnergyMeters """
        dss.text('sample')





    def envia_comandos_opendss(self):
        """ Esta função envia todos os comandos necessários ao OpenDSS """

        dss.text('Clear')
        dss.text('Set DefaultBaseFrequency=60')


        """ Chamado para alterar a tensão da barra de referência (substação primária) """
        # self.edit_volt_alimentador()


        """ Caso queria alterar a potência de todas as cargas 
            usa-se o multiplicador de carga. Uma ideia seria usa-lo 
            para simular o incremento de carga com o passar dos 
            anos no Estado de Mato Grosso 
        """
        # self.load_mult()


        """ Chamado para achar tensões máximas e minimas dos nós do circuito """
        # self.busca_max_min_voltages()


        """ Chamado para achar a potência ativa e reativa que flui pelo alimentador """
        # self.total_power()


        """ Esta função guarda o nome de todos os alimentadores """
        pastas = self.listar_pastas()


        """ Selecionando o alimentador a ser simulado - futuramente implementar um loop """
        alimentador_nome = self.feederhead


        """ Compila cada modelagem.dss de um mesmo alimentador """
        self.busca_pastas(alimentador_nome)


        """ Chamado para buscar informações dos paineis fotovoltaicos nos diretorios e envia ao OpenDSS """
        mes = 0 # Estou simulando apenas para o mes de janeiro
        self.busca_dados_paineis_fotovoltaicos(mes, alimentador_nome)



        """ Chamado para inserir EnergyMeters nas linhas do alimentador
        tais medidores separam automaticamente o circuito em zonas de 
        acordo com suas posições. ATENÇÃO não inserir EnergyMeter em 
        nós com mais de duas conexões por que as leituras podem ser 
        duplicadas porque os medidores estaram sobrepondo a zona de 
        medição """
        resposta = input(f'Deseja fazer uma análise de perdas não técnicas no alimentador: {alimentador_nome} ? (sim/não): ')
        self.inserir_energy_meters(resposta)



        """ Esta função aplica as curvas de carga e de geração """
        self.aplica_curvas_carga_geracao(self.irradiancia_96)







if __name__ == "__main__":

    alimentadores = r"C:\MODELAGEM_BARRA_SLACK_MEDIA_TENSÃO_BDGD_2023_ENERGISA"

    """ Propositalmente a barra slack será a primeira da lista para 
    definir primeiro no elemento circuit """
    caminhos_modelagens = [
        r"C:\MODELAGEM_BARRA_SLACK_MEDIA_TENSAO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_LINECODES_MEDIA_TENSAO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_LINECODES_BAIXA_TENSAO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_LINECODES_RAMAIS_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_CARGAS_BAIXA_TENSAO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_CARGAS_MEDIA_TENSAO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_CHAVES_SECCIONADORAS_BAIXA_TENSAO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_CHAVES_SECCIONADORAS_MEDIA_TENSAO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_COMPENSADORES_DE_REATIVO_BAIXA_TENSAO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_COMPENSADORES_DE_REATIVO_MEDIA_TENSAO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_LINHAS_BAIXA_TENSAO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_LINHAS_MEDIA_TENSAO_BDGD_2023_ENERGISA_COMPONENTES",
        r"C:\MODELAGEM_RAMAIS_BAIXA_TENSAO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_REGULADORES_MEDIA_TENSAO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_TRANSFORMADORES_MEDIA_TENSAO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_GERADORES_MEDIA_TENSAO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_PIP_BAIXA_TENSAO_BDGD_2023_ENERGISA"
    ]

    modelagem_curva_carga =  [r"C:\MODELAGEM_LOADSHAPES_BAIXA_TENSAO_BDGD_2023_ENERGISA",
               r"C:\MODELAGEM_LOADSHAPES_MEDIA_TENSAO_BDGD_2023_ENERGISA"
    ]


    modelagem_linhas_media_geometria = [r"C:\MODELAGEM_LINHAS_MEDIA_TENSAO_BDGD_2023_ENERGISA_GEOMETRIA_POSTES"]



    caminho_geration_shape_fotovoltaico = ["C:\MODELAGEM_LOADSHAPE_PAINEIS_FOTOVOLTAICOS_BAIXA_TENSAO_BDGD_2023_ENERGISA",
                                    "C:\MODELAGEM_LOADSHAPE_PAINEIS_FOTOVOLTAICOS_MEDIA_TENSAO_BDGD_2023_ENERGISA"]



    irradiance_96 = [
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0020868143779637777, 0.021658633552047255, 0.06088779031692882,
                    0.11144429816197712, 0.1678906012265873, 0.22728017851691293, 0.28791109647383534, 0.348697510225378,
                    0.40887777758782434, 0.4678735480839848, 0.5252178619662079, 0.580516535826924, 0.6334264811150465,
                    0.6836431225440153, 0.7308929413340143, 0.7749289692720928, 0.815528070392363, 0.852489337281985,
                    0.8856331541734708, 0.914800693562861, 0.9398536947638536, 0.9606743940716865, 0.9771655586384522,
                    0.9892505930749959, 0.9968736923877655, 1.0, 0.9986154081300684, 0.9927260244461611, 0.9823584760554767,
                    0.967560336057828, 0.9484000425869699, 0.9249667302675952, 0.8973701037748086, 0.8657403774791488,
                    0.8302283019851124, 0.7910053139847273, 0.7482639223207957, 0.702218457324121, 0.6531063758122171,
                    0.6011904981929989, 0.5467627269971509, 0.49015018292462936, 0.431725497105491, 0.3719243673385379,
                    0.31127638782044526, 0.2504614665506077, 0.19041815094248057, 0.13256340398061622, 0.07926139827877186,
                    0.03481418344816064, 0.006788902468278367, 3.7708368002252944E-5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
                    ]



    irradiance_24 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.06097221194588083, 0.28831028855538676, 0.5259460826362484, 0.7319063328920882,
                     0.8868610948351382, 0.9785204100427596, 1.0, 0.9497150102689403, 0.8313794231752692, 0.6540119153931088,
                     0.432324089525023, 0.19068216792192622, 0.0067983153604556845, 0.0, 0.0, 0.0, 0.0, 0.0
                     ]



    """ Curva de carga dos postes de iluminação pública """
    curva_de_carga_pip = []

    """ Prencher com 1 de meia-noite até as 6:00 """
    for i in range(96):
        if i < 24:
            curva_de_carga_pip.append(1)

        elif i >= 24 and i < 68:
            curva_de_carga_pip.append(0)

        elif i >= 68 and i < 96:
            curva_de_carga_pip.append(1)


    medidores = [
        ("medidor_00", -15.6267609, -55.9963973, 13729182),
        ("medidor_01", -15.61616826, -56.02164433, 17180042),
        ("medidor_02", -15.61423265, -56.02440233, 13317778),
        ("medidor_03", -15.611004141, -56.024145513, 13573177),
        ("medidor_04", -15.606625420, -56.022536853, 13504348),
        ("medidor_05", -15.609389315, -56.018112887, 13043453)

    ]



    alimentador = 764444
    circuit_pu = 1.029
    load_mult = 1

    """ Classe """
    results = Fluxo_Potencia(alimentadores, caminhos_modelagens, circuit_pu,
                             load_mult, irradiance_96, alimentador,
                             caminho_geration_shape_fotovoltaico, medidores, curva_de_carga_pip,
                             modelagem_curva_carga)


