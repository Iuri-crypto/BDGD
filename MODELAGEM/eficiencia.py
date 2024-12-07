import matplotlib.pyplot as plt
import pandas as pd
import pvlib
import numpy as np
from pvlib import location

# Função para calcular a potência gerada com base na irradiância (GHI)
def calcular_potencia_gerada(irradiancia, potencia_instalada_kwp, eficiencia):
    """
    Calcula a potência gerada pelo painel fotovoltaico com base na irradiância e eficiência.
    """
    potencia = potencia_instalada_kwp * (irradiancia / 1000) * eficiencia
    return potencia

# Função para aplicar a saturação do inversor
def aplicar_saturacao_inversor(potencia_gerada, potencia_max_inversor_kw):
    """
    Limita a potência gerada pela capacidade do inversor.
    """
    return np.minimum(potencia_gerada, potencia_max_inversor_kw)

# Função para estimar a temperatura com base na hora do dia
def estimar_temperatura(hora, latitude):
    """
    Estima a temperatura com base na hora do dia e latitude (simulação simples).
    """
    T_max = 30  # Temperatura máxima média ao meio-dia (em °C)
    T_min = 18  # Temperatura mínima média à noite (em °C)
    temperatura = (T_max + T_min) / 2 + (T_max - T_min) / 2 * np.sin(np.pi * (hora - 6) / 12)
    return temperatura

# Função principal para calcular e plotar os parâmetros com base nas coordenadas e dados fornecidos
def calcular_e_plotar_irradiancia_temperatura_e_desempenho(latitude, longitude, altitude, potencia_instalada_kwp, eficiencia, potencia_max_inversor_kw, energia_desejada):
    """
    Função que realiza os cálculos e gera os gráficos com base nas coordenadas e parâmetros fornecidos.
    """
    # Definir a localização com as coordenadas inseridas
    site = location.Location(latitude, longitude, altitude=altitude)

    # Definir o intervalo de tempo para o qual você quer calcular a irradiância
    times = pd.date_range('2024-12-01 00:00:00', '2024-12-01 23:00:00', freq='h', tz='America/Sao_Paulo')

    # Calcular a irradiância global horizontal (GHI), difusa (DHI) e direta (DNI)
    solar_position = site.get_solarposition(times)
    irradiance = site.get_clearsky(times)

    # Estimar a temperatura para cada hora
    temperatura = [estimar_temperatura(hora.hour, latitude) for hora in times]

    # Calcular a potência gerada com base na irradiância (GHI)
    potencia_gerada = calcular_potencia_gerada(irradiance['ghi'], potencia_instalada_kwp, eficiencia)

    # Ajuste da potência gerada para atingir a energia desejada
    energia_total_gerada = potencia_gerada.sum()  # Energia total gerada sem ajuste
    fator_ajuste = energia_desejada / energia_total_gerada  # Fator para ajustar a potência

    # Ajustar a potência gerada para atingir a energia desejada
    potencia_gerada_ajustada = potencia_gerada * fator_ajuste

    # Aplicar a saturação do inversor
    potencia_gerada_limitada = aplicar_saturacao_inversor(potencia_gerada_ajustada, potencia_max_inversor_kw)

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
    plt.plot(times, potencia_gerada_limitada, label=f'Potência Gerada (Ajustada para {energia_desejada} kWh)', color='purple')
    plt.title(f'Potência Gerada pelo Painel Fotovoltaico')
    plt.xlabel('Hora')
    plt.ylabel('Potência Gerada (kW)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()

    # Ajustar layout para melhor visualização
    plt.tight_layout()

    # Exibir o gráfico
    plt.show()

# Função para obter as coordenadas e parâmetros do usuário
def obter_parametros_usuario():
    """
    Função que obtém as coordenadas e parâmetros de entrada do usuário.
    """
    latitude = float(input("Digite a latitude do local: "))
    longitude = float(input("Digite a longitude do local: "))
    altitude = float(input("Digite a altitude do local (em metros): "))
    potencia_instalada_kwp = float(input("Digite a potência instalada do painel fotovoltaico (em kWp): "))
    eficiencia = float(input("Digite a eficiência do painel fotovoltaico (em %): ")) / 100  # Eficiência em % convertida para decimal
    potencia_max_inversor_kw = float(input("Digite a potência máxima do inversor (em kW): "))
    energia_desejada = float(input("Digite a energia desejada para o dia (em kWh): "))

    return latitude, longitude, altitude, potencia_instalada_kwp, eficiencia, potencia_max_inversor_kw, energia_desejada

# Função principal que executa o processo
def main():
    while True:
        print("\nAgora você pode inserir os dados para um novo cálculo.")
        parametros_usuario = obter_parametros_usuario()
        calcular_e_plotar_irradiancia_temperatura_e_desempenho(*parametros_usuario)

        # Perguntar se deseja continuar com novos cálculos
        continuar = input("\nDeseja calcular para outro local? (s/n): ").strip().lower()
        if continuar != 's':
            print("Fim do processo.")
            break

# Chama a função principal para iniciar o programa
if __name__ == "__main__":
    main()
