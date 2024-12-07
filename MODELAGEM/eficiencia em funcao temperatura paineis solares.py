import numpy as np
import matplotlib.pyplot as plt

# Definindo os parâmetros
potencia_referencia = 300  # Potência do painel solar a 25°C em W
gamma = -0.004  # Coeficiente de temperatura do painel solar (em %/°C)
eficiencia_maxima_inversor = 0.98  # Eficiência máxima do inversor (98%)
alpha = 0.001  # Coeficiente de variação da eficiência do inversor (em %/°C)
temperatura_referencia = 25  # Temperatura de referência para os cálculos (25°C)

# Definindo a faixa de temperaturas
temperaturas = np.linspace(25, 60, 100)  # Temperaturas de 25°C a 60°C

# Calculando a potência corrigida do painel solar em função da temperatura
potencia_corrigida = potencia_referencia * (1 + gamma * (temperaturas - temperatura_referencia))

# Calculando a eficiência do inversor em função da temperatura
eficiencia_inversor = eficiencia_maxima_inversor - alpha * (temperaturas - temperatura_referencia)

# Calculando a potência final gerada considerando a eficiência do inversor
potencia_final = potencia_corrigida * eficiencia_inversor

# Criando o gráfico
plt.figure(figsize=(10, 6))

# Subgráfico para a potência corrigida dos painéis solares
plt.subplot(2, 1, 1)
plt.plot(temperaturas, potencia_corrigida, color='blue', label='Potência Corrigida do Painel Solar')
plt.title('Potência Corrigida do Painel Solar e Eficiência do Inversor em Função da Temperatura')
plt.xlabel('Temperatura (°C)')
plt.ylabel('Potência (W)')
plt.grid(True)
plt.legend()

# Subgráfico para a eficiência do inversor
plt.subplot(2, 1, 2)
plt.plot(temperaturas, eficiencia_inversor * 100, color='red', label='Eficiência do Inversor', linestyle='--')
plt.title('Eficiência do Inversor em Função da Temperatura')
plt.xlabel('Temperatura (°C)')
plt.ylabel('Eficiência (%)')
plt.grid(True)
plt.legend()

# Exibindo o gráfico
plt.tight_layout()
plt.show()
