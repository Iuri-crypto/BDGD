import pandas as pd

# Caminho para os arquivos
csv_file_1 = r"C:\BDGD\ugbt.csv"  # Arquivo CSV
csv_file_2 = r"C:\BDGD\aneel_fotovoltaico.xls"  # Arquivo Excel no formato .xls

# Ler o primeiro arquivo CSV (separado por vírgulas)
df1 = pd.read_csv(csv_file_1, low_memory=False)

# Ler o segundo arquivo Excel (formato .xls), especificando o motor 'xlrd'
df2 = pd.read_excel(csv_file_2, engine='xlrd')

# Nome das colunas para comparar
coluna_df1 = 'ceg_gd'  # Coluna no arquivo CSV
coluna_df2 = 'CodGeracaoDistribuida'  # Coluna no arquivo Excel

# Verificar se as colunas existem nos dois DataFrames
if coluna_df1 in df1.columns and coluna_df2 in df2.columns:
    # Comparar cada dado de df1[coluna_df1] com cada dado de df2[coluna_df2]

    # Usando a função 'isin' para verificar quais valores da coluna_df1 estão na coluna_df2
    valores_comuns = df1[df1[coluna_df1].isin(df2[coluna_df2])]

    # Exibir os valores comuns
    if not valores_comuns.empty:
        print("Valores comuns encontrados nas duas colunas:")
        print(valores_comuns)
    else:
        print("Não há valores comuns nas duas colunas.")
else:
    print(f"As colunas '{coluna_df1}' ou '{coluna_df2}' não foram encontradas nos arquivos.")
