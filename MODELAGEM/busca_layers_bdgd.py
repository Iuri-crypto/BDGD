from osgeo import ogr


# Função para buscar camadas e tabelas em um banco de dados GDB e listar as colunas, incluindo a coluna de geometria
def listar_layers_e_tabelas_com_colunas_e_geometria(gdb_path):
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

    # Exibir camadas e suas colunas (incluindo geometria)
    print(f"Camadas (layers) em {gdb_path}:")
    for layer_name in layers_set:
        print(f"  - {layer_name} - camada")
        # Abrir a camada novamente para listar as colunas
        layer = data_source.GetLayerByName(layer_name)
        print("    Colunas:")

        # Listar colunas de atributos
        for i in range(layer.GetLayerDefn().GetFieldCount()):
            field_defn = layer.GetLayerDefn().GetFieldDefn(i)
            print(f"      - {field_defn.GetName()} (Tipo: {field_defn.GetFieldTypeName(field_defn.GetType())})")

        # Verificar e listar a coluna de geometria
        geom_field_index = layer.GetLayerDefn().GetGeomFieldCount() - 1  # Último campo geométrico (se houver)
        if geom_field_index >= 0:
            geom_field_defn = layer.GetLayerDefn().GetGeomFieldDefn(geom_field_index)
            print(
                f"      - {geom_field_defn.GetName()} (Tipo de geometria: {ogr.GeometryTypeToName(layer.GetGeomType())})")
        else:
            print("      - Nenhuma coluna de geometria encontrada.")

    # Exibir tabelas
    print(f"\nTabelas em {gdb_path}:")
    for table_name in tables_set:
        print(f"  - {table_name} - tabela")
        # Como as tabelas não têm geometria, podemos apenas listar as colunas
        layer = data_source.GetLayerByName(table_name)
        print("    Colunas:")
        for i in range(layer.GetLayerDefn().GetFieldCount()):
            field_defn = layer.GetLayerDefn().GetFieldDefn(i)
            print(f"      - {field_defn.GetName()} (Tipo: {field_defn.GetFieldTypeName(field_defn.GetType())})")


# Caminho completo do arquivo GDB
gdb_path = r"C:\Energisa_MT_405_2023-12-31_V11_20240612-1317.gdb"

# Chamar a função para listar as camadas e tabelas com as suas colunas, incluindo geometria
listar_layers_e_tabelas_com_colunas_e_geometria(gdb_path)
