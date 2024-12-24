import random
import os
import json
from collections import defaultdict

# Função para gerar dados fictícios
def gerar_dados_ficticios():
    # Definindo os dias da semana e o número de pontos de simulação
    dias = ["DO", "DU", "SA"]
    pontos_simulacao = 96  # Presumindo que há 96 pontos de simulação (um para cada intervalo de 15 minutos em 24 horas)

    # Definindo a estrutura do dicionário para armazenar os dados
    dados_ficticios = defaultdict(lambda: defaultdict(dict))

    # Nomes das cargas fictícias (simulando as cargas do sistema)
    cargas_ficticias = [f"meter_{i}" for i in range(1, 6)]  # Exemplo com 5 cargas fictícias

    # Caminhos fictícios para os arquivos JSON (sem usar realmente o sistema de arquivos, mas mantendo a estrutura)
    d_baixa = "baixa_tensao"
    d_media = "media_tensao"

    # Gerar dados fictícios para cada carga e cada dia da semana
    for dia in dias:
        for ponto_simulacao_idx in range(pontos_simulacao):
            # Gerando dados fictícios para cada carga
            for load in cargas_ficticias:
                # Simulando os caminhos dos arquivos JSON
                baixa_tensao = os.path.join(d_baixa, f"{load}_{dia}.json")
                media_tensao = os.path.join(d_media, f"{load}_{dia}.json")

                # Gerando um valor fictício para o ponto de carga (exemplo: um valor entre 0 e 10 kW)
                valor_carga = round(random.uniform(0, 10), 2)  # Potência em kW (exemplo de valor aleatório)

                # Criando o conteúdo fictício do JSON para a curva de carga
                curva_carga_ficticia = {
                    "loadshape": [round(random.uniform(0, 10), 2) for _ in range(pontos_simulacao)]  # Simulando 96 pontos de carga
                }

                # Acessando o ponto da curva de carga fictícia (este seria o "ponto_simulacao")
                ponto = curva_carga_ficticia["loadshape"][ponto_simulacao_idx]

                # Atualizando os dados no dicionário conforme o código original
                dados_ficticios[load][dia]["ponto_simulacao"] = ponto

                # Simulando a coleta de dados dos EnergyMeters (energia consumida e perdas)
                zone_kwh = round(random.uniform(0, 1000), 2)  # Energia consumida em kWh (valor aleatório)
                zone_kvar = round(random.uniform(0, 1000), 2)  # Energia consumida em kVAR (valor aleatório)
                zone_losses_kwh = round(random.uniform(0, 50), 2)  # Energia perdida em kWh (valor aleatório)
                zone_losses_kvar = round(random.uniform(0, 50), 2)  # Energia perdida em kVAR (valor aleatório)

                # Armazenando as informações nos dicionários fictícios
                dados_ficticios[load][dia]["zone_kwh"] = zone_kwh
                dados_ficticios[load][dia]["zone_kvar"] = zone_kvar
                dados_ficticios[load][dia]["zone_losses_kwh"] = zone_losses_kwh
                dados_ficticios[load][dia]["zone_losses_kvar"] = zone_losses_kvar

    # Salvar os dados fictícios em um arquivo JSON (opcional)
    with open("dados_ficticios.json", "w") as f:
        json.dump(dados_ficticios, f, indent=4)

    return dados_ficticios


# Gerar os dados fictícios
#dados_ficticios = gerar_dados_ficticios()

# Exibir os dados gerados (apenas uma amostra)
#print(json.dumps(dados_ficticios, indent=4))
