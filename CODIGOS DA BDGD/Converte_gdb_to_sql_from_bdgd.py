import subprocess
import os
import time  # Importa o módulo time para medir o tempo

# Caminho do diretório do OSGeo4W
osgeo4w_bin_path = r"C:\OSGeo4W\bin"

# Adiciona o diretório do OSGeo4W ao PATH
os.environ["PATH"] += os.pathsep + osgeo4w_bin_path

# Lista de camadas a serem convertidas
layers = [
    "ARAT", "SEGCON", "BAR", "BASE", "BAY", "BE", "CONJ", "CRVCRG", "CTAT", "CTMT",
    "EP", "EQCR", "EQME", "EQRE", "EQSE", "EQTRAT", "EQTRM", "EQTRMT",
    "PIP", "PNT", "PONNOT", "PT", "RAMLIG", "SSDAT", "SSDBT",
    "SSDMT", "SUB", "UNCRAT", "UNCRBT", "UNCRMT", "UNREAT", "UNREMT",
    "UNSEAT", "UNSEBT", "UNSEMT", "UNTRMT", "UNTRAT", "UCAT", "UCBT",
    "UCMT", "UGAT", "UGBT", "UGMT"
]

# Configurações do banco de dados PostgreSQL
db_params = {
    "host": "localhost",
    "user": "iuri",
    "dbname": "BDGD_2023_ENERGISA",
    "password": "aa11bb22"
}

def convert_layer(layer_name):
    # Tratamento especial para SEGCON
    if layer_name == "SEGCON":
        ogr2ogr_cmd = (
            f'ogr2ogr -f "PostgreSQL" '
            f'PG:"host={db_params["host"]} user={db_params["user"]} dbname={db_params["dbname"]} password={db_params["password"]}" '
            f'"C:\\Energisa_MT_405_2023-12-31_V11_20240612-1317.gdb" '
            f'-nln {layer_name} -lco COLUMN_TYPES=cmax_renamed=Float8 '
            f'-sql "SELECT cod_id, dist, geom_cab, form_cab, mat_fas_1, mat_fas_2, mat_fas_3, mat_neu, iso_fas_1, iso_fas_2, iso_fas_3, iso_neu, cnd_fas, r1, x1, ftrcnv, cnom, cmax AS cmax_renamed, tuc_fas, a1_fas, a2_fas, a3_fas, a4_fas, a5_fas, a6_fas, tuc_neu, a1_neu, a2_neu, a3_neu, a4_neu, a5_neu, a6_neu, descr, bit_fas_1, bit_fas_2, bit_fas_3, bit_neu, r_regul, uar FROM {layer_name}"'
        )
    else:
        # Para as outras camadas, verificamos se há geometria e adicionamos a coluna Shape
        ogr2ogr_cmd = (
            f'ogr2ogr -f "PostgreSQL" '
            f'PG:"host={db_params["host"]} user={db_params["user"]} dbname={db_params["dbname"]} password={db_params["password"]}" '
            f'"C:\\Energisa_MT_405_2022-12-31_V11_20230820-1800.gdb" '  # Substitua pelo caminho correto do seu arquivo GDB
            f'-nln {layer_name} '  # Nome da camada no banco de dados
            f'-lco GEOMETRY_NAME=Shape '  # Nome da coluna de geometria
            f'-lco OVERWRITE=YES '  # Substitui tabelas existentes no PostgreSQL
            f'-lco COLUMN_TYPES=cmax_renamed=Float8 '  # Se necessário, ajusta o tipo de coluna
            f'-sql "SELECT * FROM {layer_name}"'  # Seleciona todos os campos e a geometria
        )

    try:
        print(f'Convertendo camada {layer_name}...')
        result = subprocess.run(ogr2ogr_cmd, shell=True, text=True, capture_output=True)

        if result.returncode != 0:
            print(f'Erro ao converter a camada {layer_name}:')
            print(result.stderr)
        else:
            print(f'Camada {layer_name} convertida com sucesso.')
    except Exception as e:
        print(f'Erro ao executar o comando para a camada {layer_name}: {e}')

# Inicia a contagem do tempo
start_time = time.time()

# Converte todas as camadas
for layer in layers:
    convert_layer(layer)

# Termina a contagem do tempo
end_time = time.time()
elapsed_time = end_time - start_time

print(f"Conversão de todas as camadas concluída em {elapsed_time:.2f} segundos.")

0