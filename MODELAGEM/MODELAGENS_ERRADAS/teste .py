import matplotlib.pyplot as plt
import pandas as pd
import pvlib
from datetime import datetime
from pvlib import location
import numpy as np

# Defina uma coordenada genérica para a primeira execução (Cuiabá, Mato Grosso)
latitude_padrao = -15.6010  # Latitude de Cuiabá
longitude_padrao = -56.0979  # Longitude de Cuiabá
altitude_padrao = 165  # Altitude de Cuiabá em metros

# Potência instalada do painel fotovoltaico (em kWp)
potencia_instalada_kwp = 5  # Exemplo: painel de 5 kWp

# Eficiência do painel fotovoltaico (valor típico)
eficiencia = 0.18  # Eficiência de 18%

# Função para calcular a potência gerada com base na irradiância (GHI)
def calcular_potencia_gerada(irradiancia, potencia_instalada_kwp, eficiencia):
    # A irradiância deve estar em W/m², potência instalada em kWp
    return potencia_instalada_kwp * (irradiancia / 1000) * eficiencia

# Função para pedir as coordenadas ao usuário
def obter_coordenadas():
    latitude = float(input("Digite a latitude do local: "))
    longitude = float(input("Digite a longitude do local: "))
    altitude = float(input("Digite a altitude do local (em metros): "))
    return latitude, longitude, altitude

# Função para estimar a temperatura com base na hora do dia
def estimar_temperatura(hora, latitude):
    # Suponha uma variação de temperatura simples ao longo do dia (em °C)
    T_max = 30  # Temperatura máxima média ao meio-dia (em °C)
    T_min = 18  # Temperatura mínima média à noite (em °C)

    # Fórmula simples para variação de temperatura (senoidal)
    temperatura = (T_max + T_min) / 2 + (T_max - T_min) / 2 * np.sin(np.pi * (hora - 6) / 12)
    return temperatura

# Função principal
def calcular_e_plotar_irradiancia_temperatura_e_desempenho(coordenadas):
    latitude, longitude, altitude = coordenadas

    # Definir a localização com as coordenadas inseridas
    site = location.Location(latitude, longitude, altitude=altitude)

    # Definir o intervalo de tempo para o qual você quer calcular a irradiância
    # Vamos pegar o intervalo completo de 24 horas do dia 1 de dezembro de 2024
    times = pd.date_range('2024-12-01 00:00:00', '2024-12-01 23:00:00', freq='h', tz='America/Sao_Paulo')

    # Calcular a irradiância global horizontal (GHI), difusa (DHI) e direta (DNI)
    solar_position = site.get_solarposition(times)
    irradiance = site.get_clearsky(times)

    # Estimar a temperatura para cada hora
    temperatura = [estimar_temperatura(hora.hour, latitude) for hora in times]

    # Calcular a potência gerada com base na irradiância (GHI)
    potencia_gerada = calcular_potencia_gerada(irradiance['ghi'], potencia_instalada_kwp, eficiencia)

    # Plotar os gráficos
    plt.figure(figsize=(12, 10))

    # Subgráfico 1: Irradiância
    plt.subplot(3, 1, 1)  # Primeiro gráfico para irradiâncias
    plt.plot(times, irradiance['ghi'], label='Irradiância Global Horizontal (GHI)', color='orange')
    plt.plot(times, irradiance['dni'], label='Irradiância Direta Normal (DNI)', color='red')
    plt.plot(times, irradiance['dhi'], label='Irradiância Difusa Horizontal (DHI)', color='blue')
    plt.title(f'Curvas de Irradiância - Local ({latitude}, {longitude}) - 1º Dezembro 2024')
    plt.xlabel('Hora')
    plt.ylabel('Irradiância (W/m²)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()

    # Subgráfico 2: Temperatura
    plt.subplot(3, 1, 2)  # Segundo gráfico para temperatura
    plt.plot(times, temperatura, label='Temperatura (°C)', color='green')
    plt.title('Temperatura ao Longo do Dia')
    plt.xlabel('Hora')
    plt.ylabel('Temperatura (°C)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()

    # Subgráfico 3: Potência Gerada
    plt.subplot(3, 1, 3)  # Terceiro gráfico para a potência gerada
    plt.plot(times, potencia_gerada, label='Potência Gerada (kW)', color='purple')
    plt.title('Potência Gerada pelo Painel Fotovoltaico ao Longo do Dia')
    plt.xlabel('Hora')
    plt.ylabel('Potência Gerada (kW)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()

    # Ajustar layout para melhor visualização
    plt.tight_layout()

    # Exibir o gráfico
    plt.show()

# Primeira iteração com a coordenada de Cuiabá
print("Primeira iteração - Coordenada padrão (Cuiabá, MT)")
calcular_e_plotar_irradiancia_temperatura_e_desempenho((latitude_padrao, longitude_padrao, altitude_padrao))

# Segunda iteração e além - pedir ao usuário as coordenadas
while True:
    print("\nPróxima iteração - Agora você pode inserir suas próprias coordenadas.")
    coordenadas_usuario = obter_coordenadas()
    calcular_e_plotar_irradiancia_temperatura_e_desempenho(coordenadas_usuario)

    # Perguntar se deseja continuar com novas coordenadas
    continuar = input("\nDeseja calcular para outro local? (s/n): ").strip().lower()
    if continuar != 's':
        print("Fim do processo.")
        break
