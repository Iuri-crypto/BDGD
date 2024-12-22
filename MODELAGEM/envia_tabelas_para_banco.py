from osgeo import ogr
import os

# Caminho do arquivo GDB
gdb_path = r"C:\Users\muril\OneDrive\Documentos\SEXTO_SEMESTRE\PROJETO_DE_PESQUISA\BDGD 2022 ENERGIZA MT\Energisa_MT_405_2023-12-31_V11_20240612-1317.gdb\Energisa_MT_405_2023-12-31_V11_20240612-1317.gdb"

# Caminho da pasta onde os arquivos SQL serão salvos
output_dir = r"C:\Users\muril\OneDrive\Documentos\SEXTO_SEMESTRE\PROJETO_DE_PESQUISA\BDGD 2022 ENERGIZA MT\output_sql"

# Cria o diretório de saída, se não existir
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Abre o arquivo GDB
gdb = ogr.Open(gdb_path)

# Verifica se o arquivo foi aberto corretamente
if gdb is None:
    print(f"Erro ao abrir o arquivo GDB: {gdb_path}")
    exit(1)

# Obtém o número de camadas no arquivo GDB
layer_count = gdb.GetLayerCount()

if layer_count == 0:
    print(f"O arquivo GDB não contém camadas válidas.")
    exit(1)

# Loop pelas camadas
for i in range(layer_count):
    layer = gdb.GetLayerByIndex(i)  # Obtém a camada pelo índice
    layer_name = layer.GetName()  # Nome da camada

    print(f"Verificando se a camada {layer_name} já foi convertida...")

    # Caminho de saída para o arquivo SQL
    output_sql = os.path.join(output_dir, f"{layer_name}.sql")

    # Verifica se o arquivo SQL já existe no diretório de saída
    if os.path.exists(output_sql):
        print(f"A camada {layer_name} já foi convertida. Pulando a criação.")
        continue  # Pula a camada, caso o arquivo já exista

    print(f"Convertendo camada {layer_name} para SQL...")

    # Configurar o driver para exportação para SQL
    driver = ogr.GetDriverByName("SQLite")  # Usando SQLite como exemplo; pode ser ajustado para outro formato

    if driver is None:
        print(f"Driver não encontrado para a camada {layer_name}.")
        continue

    # Configurar o arquivo de saída
    output_dataset = driver.CreateDataSource(output_sql)

    if output_dataset is None:
        print(f"Não foi possível criar o arquivo SQL para a camada {layer_name}.")
        continue

    # Copiar os dados da camada para o arquivo de saída
    output_dataset.CopyLayer(layer, layer_name)
    print(f"Camada {layer_name} convertida para SQL com sucesso!")

# Fechar o arquivo GDB
gdb = None

print("Conversão concluída.")
