import matplotlib.pyplot as plt
import pandas as pd
import pvlib
import numpy as np

# Definir a localização
latitude = -15.6010  # Exemplo: Cuiabá
longitude = -56.0979
site = pvlib.location.Location(latitude, longitude)

# Definir o intervalo de tempo (24 horas do dia 1 de dezembro de 2024)
times = pd.date_range('2024-12-01 00:00:00', '2024-12-01 23:00:00', freq='H', tz='America/Sao_Paulo')

# Obter a irradiância solar global (GHI) para o local
irradiance = site.get_clearsky(times)

# Definir parâmetros do painel fotovoltaico e do inversor
potencia_instalada = 5  # Potência instalada do painel em kW
potencia_nominal_inversor = 4.5  # Potência nominal do inversor em kW
eficiencia_maxima_inversor = 0.98  # Eficiência máxima do inversor (98%)
P_limite_inversor = potencia_nominal_inversor * 0.2  # A eficiência começa a saturar abaixo de 70% da potência nominal
k_inversor = 4  # Constante de saturação da eficiência do inversor

# Calcular a potência gerada a cada hora (simplificação)
potencia_gerada = (irradiance['ghi'] / irradiance['ghi'].max()) * potencia_instalada

# Função de eficiência do inversor
def eficiencia_inversor(P_entrada, P_nominal, eta_max, P_limite, k):
    return eta_max / (1 + np.exp(-k * (P_entrada - P_limite))) * 100  # Eficiência em %

# Calcular a eficiência do inversor a cada hora
eficiencia_inversor_valores = eficiencia_inversor(potencia_gerada, potencia_nominal_inversor,
                                                  eficiencia_maxima_inversor, P_limite_inversor, k_inversor)

# Calcular a potência final considerando a eficiência do inversor
potencia_final_com_eficiencia = potencia_gerada * (eficiencia_inversor_valores / 100)

# Plotar os gráficos

# Gráfico da potência gerada ao longo do dia
plt.figure(figsize=(12, 8))

# Gráfico de potência gerada
plt.subplot(2, 1, 1)
plt.plot(times, potencia_gerada, label='Potência Gerada (kW)', color='orange')
plt.title('Potência Gerada pelo Painel Fotovoltaico (1º Dezembro 2024)')
plt.xlabel('Hora')
plt.ylabel('Potência Gerada (kW)')
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()

# Gráfico de potência gerada considerando a eficiência do inversor
plt.subplot(2, 1, 2)
plt.plot(times, potencia_final_com_eficiencia, label='Potência Final (com Eficiência do Inversor)', color='blue')
plt.title('Potência Final Gerada pelo Sistema (com Eficiência do Inversor)')
plt.xlabel('Hora')
plt.ylabel('Potência Final (kW)')
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
