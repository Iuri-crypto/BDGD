import pvlib
import pandas as pd
import matplotlib.pyplot as plt

# Define a localização (site) para Cuiabá
latitude = -15.5989
longitude = -56.0962
site = pvlib.location.Location(latitude, longitude)
rec_mensal = 5   # Exemplo: Maio (05)
rec_diario = 7   # Exemplo: 7º dia do mês

# Defina o horário de cálculo da irradiância
index_3 = f'{int(rec_mensal):02d}' if rec_mensal < 10 else str(rec_mensal)
index_4 = f'{int(rec_diario):02d}' if rec_diario < 10 else str(rec_diario)

# Criar o intervalo de tempo a cada 15 minutos
times = pd.date_range(f'2023-{index_3}-{index_4}', f'2023-{index_3}-{index_4} 23:59', freq='15T', tz='America/Cuiaba')

# Calcular a posição solar e a irradiância de céu claro
solar_position = site.get_solarposition(times)
irradiance = site.get_clearsky(times)

# Criar um dicionário com os dados
data_dict = {
    "time": times,
    "apparent_zenith": solar_position["apparent_zenith"],
    "elevation": solar_position["elevation"],
    "ghi": irradiance["ghi"],
    "dni": irradiance["dni"],
    "dhi": irradiance["dhi"]
}

# Mostrar os primeiros dados
for key, value in data_dict.items():
    print(f"{key}:")
    print(value.head(), "\n")

# Criar gráficos para visualização

# Plotando a elevação do sol e o zenith aparente
plt.figure(figsize=(10, 5))
plt.subplot(2, 1, 1)
plt.plot(times, data_dict["elevation"], label='Elevation', color='orange')
plt.plot(times, data_dict["apparent_zenith"], label='Apparent Zenith', color='blue')
plt.title('Solar Elevation and Apparent Zenith')
plt.xlabel('Time')
plt.ylabel('Angle (degrees)')
plt.legend()

# Plotando a irradiância (GHI, DNI, DHI)
plt.subplot(2, 1, 2)
plt.plot(times, data_dict["ghi"], label='Global Horizontal Irradiance (GHI)', color='green')
plt.plot(times, data_dict["dni"], label='Direct Normal Irradiance (DNI)', color='red')
plt.plot(times, data_dict["dhi"], label='Diffuse Horizontal Irradiance (DHI)', color='blue')
plt.title('Irradiance: GHI, DNI, DHI')
plt.xlabel('Time')
plt.ylabel('Irradiance (W/m²)')
plt.legend()

plt.tight_layout()
plt.show()
