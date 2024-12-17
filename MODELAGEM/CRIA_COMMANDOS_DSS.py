import os
import numpy as np
import py_dss_interface

dss = py_dss_interface.DSSDLL()


class Fluxo_Potencia:
    """ Classe para calcular o fluxo de potência nos alimentadores """

    def __init__(self, alimentadores_recebidos, caminhos_model, circuito_pu, loads_mult):
        """ Inicializa a classe Fluxo Potencia """
        self.alimentadores_recebidos = alimentadores_recebidos
        self.caminhos_model = caminhos_model
        self.circuito_pu = circuito_pu
        self.loads_mult = loads_mult


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


    def busca_pastas(self):
        """ Esta função envia comandos de compile para o OpenDSS """
        pastas = self.listar_pastas()

        for nome in pastas:
            """ Percorre cada diretório para procurar as pastas """
            for path in self.caminhos_model:

                """ Define o caminho completo da pasta """
                caminho = os.path.join(path, nome)

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
                            caminho_arquivo = caminho_arquivo.replace('\\', '\\\\')

                            """ GERANDO COMANDOS PARA O OPENDSS COMPILAR """
                            dss.text(f'Compile [{caminho_arquivo}]')


            """ Chama função para executar outros comandos necessários do OpenDSS """
            self.envia_comandos_opendss()


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
        voltages_v = dss.circuit_all_bus_vmag()
        voltages_pu = dss.circuit_all_bus_vmag_pu()

        v_max_pu = max(dss.circuit_all_bus_vmag_pu())
        v_min_pu = min(dss.circuit_all_bus_vmag_pu())



    def total_power(self):
        """ Esta função encontra as potência ativas e reativas que estão fluindo
            pelo alimentador.ATENÇÃO: por padrão no OpenDSS tais valores são positivos se
            estiverem entrando no elemento e negativos se estiverem saindo do
            elemento
        """
        kW_alimentador = dss.circuit_total_power()[0]
        kVar_alimentador = dss.circuit_total_power()[1]


    def adiciona_paineis_fotovoltaicos(self):




    def envia_comandos_opendss(self):
        """ Esta função envia todos os comandos necessários ao OpenDSS """

        dss.text('Clear')

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
        self.total_power()

        """ Chamado para inserir paineis fotovoltaicos no circuito """
        self.adiciona_paineis_fotovoltaicos()


        """ Resolve o circuito """
        dss.solution_solve()























if __name__ == "__main__":

    alimentadores = r"C:\MODELAGEM_BARRA_SLACK_MÉDIA_TENSÃO_BDGD_2023_ENERGISA"

    """ Propositalmente a barra slack será a primeira da lista para 
    definir primeiro no elemento circuit """
    caminhos_modelagens = [
        r"C:\MODELAGEM_BARRA_SLACK_MÉDIA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_CARGAS_BAIXA_TENSÃO_BDGD_2023_ENERGISA_PRIMEIRO",
        r"C:\MODELAGEM_CARGAS_MEDIA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_CHAVES_SECCIONADORAS_BAIXA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_CHAVES_SECCIONADORAS_MÉDIA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_COMPENSADORES_DE_REATIVO_BAIXA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_COMPENSADORES_DE_REATIVO_MÉDIA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_GERADORES_MÉDIA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_LINECODES_BAIXA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_LINECODES_MEDIA_TENSAO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_LINHAS_BAIXA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_LINHAS_MÉDIA_TENSÃO_BDGD_2023_ENERGISA_COMPONENTES",
        r"C:\MODELAGEM_LINHAS_MÉDIA_TENSÃO_BDGD_2023_ENERGISA_GEOMETRIA_POSTES",
        r"C:\MODELAGEM_LOADSHAPES_BAIXA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_LOADSHAPES_MÉDIA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_RAMAIS_BAIXA_TENSAO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_REGULADORES_MÉDIA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_TRANSFORMADORES_MÉDIA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEMs_PAINEIS_FOTOVOLTAICOS_BAIXA_TENSÃO_BDGD_2023_ENERGISA",
        ############################################################### ajustar os que faltam abaixo
        r"C:\MODELAGEM_LOADSHAPES_MÉDIA_TENSÃO_BDGD_2023_ENERGISA"
    ]

    circuit_pu = 1.029
    load_mult = 1

    """ Classe """
    results = Fluxo_Potencia(alimentadores, caminhos_modelagens, circuit_pu,
                             load_mult)

    """ Procura pastas """
    results.listar_pastas()

    """ Busca as pastas nos diretorios  de cada modelagem """
    results.busca_pastas()


