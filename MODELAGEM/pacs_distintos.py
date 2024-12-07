import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pvlib import location


# Função para estimar a temperatura para cada hora do dia (ajustada para variação mais realista)
def estimar_temperatura(hora, latitude, cidade):
    """
    Estimativa de temperatura baseada na hora do dia, latitude e cidade.
    :param hora: hora do dia (0-23)
    :param latitude: latitude do local (usada para calcular variação diurna simples)
    :param cidade: nome da cidade para ajustar a temperatura base
    :return: temperatura estimada (°C)
    """
    # Temperatura base média (aproximada para a cidade)
    if cidade == "Campo Grande (MS)":  # Cidade mais quente
        temperatura_base = 30  # Maior temperatura média base
    elif cidade == "São Joaquim (SC)":  # Cidade mais fria
        temperatura_base = 10  # Temperatura base mais baixa
    else:
        temperatura_base = 25  # Para cidades padrão, temperatura base média

    # Variação diurna (máximo em torno das 12h, mínimo ao amanhecer)
    variacao_diurna = 12 * (1 - abs(12 - hora) / 12)  # A variação é maior ao meio-dia

    # Ajustar variação para considerar as características da cidade
    if cidade == "Campo Grande (MS)":
        variacao_diurna += 5  # Campo Grande tende a ser mais quente
    elif cidade == "São Joaquim (SC)":
        variacao_diurna -= 5  # São Joaquim tende a ser mais frio

    return temperatura_base + variacao_diurna


# Função para calcular a temperatura ao longo de um dia específico
def calcular_temperatura_por_dia(latitude, dia, cidade):
    """
    Calcular a temperatura hora a hora para um dia específico.
    :param latitude: latitude do local
    :param dia: data do dia específico no formato 'YYYY-MM-DD'
    :param cidade: nome da cidade para o título do gráfico
    :return: gráfico com a temperatura ao longo do dia
    """
    # Gerar intervalo de horas (0h até 23h) para o dia fornecido
    times = pd.date_range(f'{dia} 00:00', f'{dia} 23:59', freq='1H', tz='America/Sao_Paulo')

    # Calcular a temperatura para cada hora
    temperatura = [estimar_temperatura(hora.hour, latitude, cidade) for hora in times]

    # Criar um novo gráfico para a cidade atual
    plt.figure(figsize=(10, 6))
    plt.plot(times, temperatura, label=f'Temperatura Estimada - {cidade} (°C)')
    plt.xlabel('Hora do Dia')
    plt.ylabel('Temperatura (°C)')
    plt.title(f'Temperatura Estimada para o dia {dia} em {cidade}')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()


# Definir as coordenadas de duas cidades: mais quente e mais fria do Brasil
# Coordenadas da cidade mais quente (Campo Grande, MS)
latitude_quente = -20.4697  # Latitude de Campo Grande
longitude_quente = -54.6201  # Longitude de Campo Grande

# Coordenadas da cidade mais fria (São Joaquim, SC)
latitude_fria = -28.2760  # Latitude de São Joaquim
longitude_fria = -49.9209  # Longitude de São Joaquim

# Escolha de um dia específico (exemplo: 1 de janeiro de 2023)
dia = '2023-01-01'

# Chamar a função para calcular e plotar a temperatura para a cidade mais quente
calcular_temperatura_por_dia(latitude_quente, dia, "Campo Grande (MS)")

# Chamar a função para calcular e plotar a temperatura para a cidade mais fria
calcular_temperatura_por_dia(latitude_fria, dia, "São Joaquim (SC)")

# Exibir o gráfico com as duas cidades
plt.suptitle(f'Temperatura Estimada para o dia {dia}')
plt.show()
