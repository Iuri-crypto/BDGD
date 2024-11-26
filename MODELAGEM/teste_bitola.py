import pandas as pd

# Função para ler o arquivo Excel e criar o dicionário de bitolas
def criar_dicionario_bitolas_fases(caminho_arquivo):
    # Ler o arquivo Excel
    df = pd.read_excel(caminho_arquivo)

    # Verificar as colunas do DataFrame para garantir que estão corretas
    print("Colunas encontradas no arquivo:", df.columns)

    # Criar o dicionário de Bitola -> Fase (usando as colunas corretas: 'Codigo' e 'mm2')
    dicionario = pd.Series(df['mm2'].values, index=df['Codigo']).to_dict()
    return dicionario

# Função para buscar o valor de Fase para a Bitola fornecida
def obter_fase_por_bitola(dicionario, Codigo):
    return dicionario.get(Codigo, 'Bitola não encontrada')

# Caminho do arquivo Excel
caminho_arquivo = r"C:\area_seccao_fio_awg_bdgd_2023.xlsx"

# Criar o dicionário de bitolas e fases
dicionario_bitolas_fases = criar_dicionario_bitolas_fases(caminho_arquivo)

# Solicitar ao usuário o valor da bitola e buscar a fase correspondente
while True:
    Codigo = input("Digite o valor da Bitola (ou 'sair' para encerrar): ")
    if Codigo.lower() == 'sair':
        print("Encerrando o programa.")
        break
    try:
        Codigo = int(Codigo)  # Converte a entrada para número inteiro
        mm2 = obter_fase_por_bitola(dicionario_bitolas_fases, Codigo)
        print(f"Para a Bitola {Codigo}, o valor da Fase é: {mm2}")
    except ValueError:
        print("Por favor, insira um número válido para a Bitola.")
