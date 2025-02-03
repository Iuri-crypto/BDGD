import subprocess
import time

# Alimentador 001009
alimentador = '001009'

pontos = 96  # Número total de pontos (cada ponto é 15 minutos)
dias = ['SA', 'DO', 'DU']


# ***********************************************************************************************************************
def compilar_codigo(main, db_pontos, resposta):
    """ Executa a simulação de forma sequencial, processando os pontos um de cada vez """

    def executar_script(db_dia, db_ponto_simulacao):
        """ Executa o script usando subprocess """

        # Calcula a hora correspondente ao ponto (15 minutos por ponto)
        hora_total = db_ponto_simulacao * 15  # Cada ponto é 15 minutos
        horas = hora_total // 60
        minutos = hora_total % 60

        # Exibe a hora formatada como HH:MM
        hora_formatada = f"{int(horas):02}:{int(minutos):02}"

        # Exibe o progresso da simulação com a hora
        print(f'Executando: Dia: {db_dia}, Ponto da Simulação: {db_ponto_simulacao}, Hora: {hora_formatada}')

        subprocess.run(f'python {main} {db_dia} {db_ponto_simulacao} {resposta}', shell=True)
        print("\n" + "-" * 50 + "\n")  # Adiciona o espaço entre os blocos

    # Processando os pontos sequencialmente
    for ponto in range(0, db_pontos):
        for dia in dias:
            executar_script(dia, ponto)  # Chama a execução para cada dia e ponto


# ***********************************************************************************************************************
inicio = time.time()

# Perguntar apenas uma vez se o usuário deseja executar
resposta = input(f'\nDeseja fazer uma análise de perdas não técnicas no alimentador: {alimentador} ? (sim/não): \n')

# Chama a função para executar o script
compilar_codigo("COMANDA_OPENDSS_USANDO_PYTHON.py", pontos, resposta)

fim = time.time()

# Tempo total de execução em segundos
tempo_total_segundos = fim - inicio

# Como cada ponto corresponde a 15 minutos, calculamos o tempo total em minutos
tempo_total_minutos = pontos * 15

# Agora convertemos para horas e minutos
horas = tempo_total_minutos // 60
minutos = tempo_total_minutos % 60

print(f"Tempo total de execução: {tempo_total_segundos} segundos")
