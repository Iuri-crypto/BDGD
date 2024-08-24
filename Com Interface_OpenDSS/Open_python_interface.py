# coding: utf-8

import win32com.client
from pylab import *

class DSS():

    def __init__(self, end_modelo_DSS):
        self.end_modelo_DSS = end_modelo_DSS
        # criar a conexão entre python e OpenDSS
        self.dssObj = win32com.client.Dispatch("OpenDSSEngine.DSS")

        # iniciar o Objeto DSS
        if self.dssObj.start(0) == False:
            print("Problemas em inciar o OpenDSS")
        else:
            # Criar varíaveis para as pricipais interfaces
            self.dssText = self.dssObj.Text
            self.dssCircuit = self.dssObj.ActiveCircuit
            self.dssSolution = self.dssCircuit.Solution
            self.dssCktElement = self.dssCircuit.ActiveCktElement
            self.dssBus = self.dssCircuit.ActiveBus
            self.dssLines = self.dssCircuit.Lines
            self.dssTransformes = self.dssCircuit.Transformers

    def versao_DSS(self):
        return self.dssObj.Version

    def compila_DSS(self):
        # Limpar informações da ultima simulação
        self.dssObj.ClearAll()
        self.dssText.Command = "compile " + self.end_modelo_DSS

    def solve_DSS_snapshot(self, multiplicador_carga):
        # Configurações
        self.dssText.Command = "set mode=snapShot"
        self.dssText.Command = "set controlMode=Static"
        # Multiplicador o valor nominal das cargas pelo valor do multiplicador carga
        self.dssSolution.LoadMult = multiplicador_carga
        # Resolver o Fluxo de Carga
        self.dssSolution.Solve()

    def get_resultados_potencia(self):
        self.dssText.command = "show powers kva elements"

    def get_nome_circuit(self):
        return self.dssCircuit.Name

    def get_potencias_circuit(self):
        p = -self.dssCircuit.TotalPower[0]
        q = -self.dssCircuit.TotalPower[1]
        return p, q

    def ativa_barra(self, nome_barra):
        self.dssCircuit.SetActiveBus(nome_barra)
        return self.dssBus.Name

    def get_distancia_barra(self):
        return self.dssBus.Distance

    def get_kvbase_barra(self):
        return self.dssBus.kVBase

    def get_VMagAng_barra(self):
        return self.dssBus.VMagAngle

    def ativa_element(self, nome_elemento):
        self.dssCircuit.SetActiveElement(nome_elemento)
        return self.dssCktElement.Name

    def get_barras_element(self):
        barras = self.dssCktElement.busNames
        barra1 = barras[0]
        barra2 = barras[1]
        return barra1, barra2

    def get_tensoes_element(self):
        return self.dssCktElement.VoltagesmagAng

    def ativa_linha(self, nome_linha):
        self.dssCircuit.SetActiveElement(nome_linha)
        return self.dssLines.Name

    def get_potencias_element(self):
        return self.dssCktElement.powers

    def get_nome_linha(self):
        return self.dssLines.Name

    def get_tamanho_linha(self):
        return self.dssLines.Length

    def set_tamanho_linha(self, tamanho):
        self.dssLines.Length = tamanho


    def get_nome_trafo(self):
        return self.dssTransformes.Name
    #return self.dssTransformes.kV
    def get_tensao_terminal_trafo(self, terminal):
        # Ativar um dos terminais do transformador
        self.dssTransformes.Wdg = terminal
        return self.dssTransformes.kV

    def get_name_e_tamanho_linhas(self):
        # Definindo duas listas
        nome_linha_lista=[]
        tamanho_linha_lista=[]
        # Seleciona a primeira linha
        self.dssLines.First

        for i in range(self.dssLines.Count):
            print("Teste elemento ativo: " + self.dssCktElement.Name)
            print("tensão do elemento ativo: " + str(self.dssCktElement.VoltagesmagAng))
            nome_linha_lista.append(self.dssLines.Name)
            tamanho_linha_lista.append(self.dssLines.Length)
            self.dssLines.Next
        return nome_linha_lista, tamanho_linha_lista


if __name__== "__main__":

    # Criar um Objeto da classe DSS
    objeto = DSS("C:\OpenDss\simulacao\OpenDSS_e_Interface_COM_Tutorial\circuito_utilizado02.dss")

    objeto.versao_DSS()

    print(" Versão do OpenDSS:" + objeto.versao_DSS() + "\n")

    # Resolver o Fluxo de Potência
    objeto.compila_DSS()
    objeto.solve_DSS_snapshot(1.0)
    ##objeto.get_resultados_potencia()

    # informações do elemento circuit
    p, q = objeto.get_potencias_circuit()
    print("Nosso exeplo apresenta o nome do elemento Circuit: " + objeto.get_nome_circuit())
    print("Fornece Potência Ativa: " + str(p) + " kw")
    print("Fornece Potência Reativa: " + str(q) + " kvar" + "\n")

    # informações de Barra escolhida
    print("Barra Ativa: " + objeto.ativa_barra("c"))
    print("Distância do EnergyMeter: " + str(objeto.get_distancia_barra()))
    print("Tensão de base da Barra em (kv): " + str(objeto.get_kvbase_barra() * sqrt(3)))
    print("tensôes desta Barra em (kv): " + str(objeto.get_VMagAng_barra()) + "\n")

    # Informações do elemento escolhido
    print("Elemento Ativo: " + objeto.ativa_element("Line.Linha1"))
    barra1, barra2 = objeto.get_barras_element()
    print("Esse elemento está conectado entre as barras: " + barra1 +" e " + barra2)
    print("As tensões nodais desse elemento: " + str(objeto.get_tensoes_element()))
    print("As potências desse elemento (kw) e (kvar): " + str(objeto.get_potencias_element()) + "\n")

    # informações dos dados da linha escolhida
    print("Linha Ativa: " + objeto.ativa_linha("Line.Linha1"))
    print("Nome da Linha Ativa: " + objeto.get_nome_linha())
    print("Tamanho da Linha Ativa: " + str(objeto.get_tamanho_linha()))
    print("Alterar o tamanho da linha para 0.4 km")
    objeto.set_tamanho_linha(0.4)
    print("Novo tamanho da linha ativa: " + str(objeto.get_tamanho_linha()) + "\n")

    # Informações do Transformador
    print("Transformador Ativo: " + objeto.ativa_element("Transformer.Trafo"))
    print("Nome do Transformador Ativo: " + objeto.get_nome_trafo())
    print("Tensão Nominal do primario: " + str(objeto.get_tensao_terminal_trafo(1)))
    print("tensão nominal do secundario: " + str(objeto.get_tensao_terminal_trafo(2)))

    # Nome e tamanho de todas as linhas
    nome_linhas, tamanho_linhas = objeto.get_name_e_tamanho_linhas()
    print("Nomes das linhas: " + str(nome_linhas))
    print("Tamanhos das linhas: " + str(tamanho_linhas))


