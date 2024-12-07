import matplotlib.pyplot as plt
import pandas as pd
import pvlib
import numpy as np

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

def calcular_energia_gerada_mes(latitude, longitude, energia_desejada, ano, mes,
                                potencia_instalada, potencia_nominal_inversor, eficiencia_maxima_inversor,
                                p_limite)