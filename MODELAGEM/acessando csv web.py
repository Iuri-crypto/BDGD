import pandas as pd

# Caminho do arquivo CSV que foi salvo no servidor
csv_file = "static_files/dados.csv"

# Ler o arquivo CSV diretamente
df = pd.read_csv(csv_file)

# Exibir os dados
print(df.head())
