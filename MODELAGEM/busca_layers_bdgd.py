from osgeo import ogr


# Função para buscar camadas e tabelas em um banco de dados GDB
def listar_layers_e_tabelas(gdb_path):
    # Abrir o arquivo .gdb
    data_source = ogr.Open(gdb_path)
    if data_source is None:
        print(f"Não foi possível abrir o arquivo: {gdb_path}")
        return

    # Conjuntos para armazenar nomes únicos das camadas e tabelas
    layers_set = set()
    tables_set = set()

    # Iterar sobre todas as camadas e tabelas
    for layer_index in range(data_source.GetLayerCount()):
        layer = data_source.GetLayerByIndex(layer_index)
        layer_name = layer.GetName()

        # Verificar se a camada tem geometria (é uma camada de feição)
        if layer.GetGeomType() != ogr.wkbNone:
            # Adicionar ao conjunto de camadas
            layers_set.add(layer_name)
        else:
            # Caso contrário, é uma tabela (sem geometria)
            tables_set.add(layer_name)

    # Exibir camadas e tabelas
    print(f"Camadas (layers) em {gdb_path}:")
    for layer in layers_set:
        print(f"  - {layer} - camada")

    print(f"\nTabelas em {gdb_path}:")
    for table in tables_set:
        print(f"  - {table} - tabela")


# Solicitar o caminho completo do arquivo GDB
gdb_path = input("Informe o caminho completo do arquivo .gdb: ")

# Chamar a função para listar as camadas e tabelas
listar_layers_e_tabelas(gdb_path)
