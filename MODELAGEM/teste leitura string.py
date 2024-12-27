import struct
import time

# Caminho para salvar o arquivo binário
caminho_arquivo = "C:/Users/muril/OneDrive/Documentos/milhao_linhas.bin"

# Linha de exemplo
linha_exemplo = "53528ec89cabb71f2fa6f78a0e0aa529a87ff91963616fdb0cd2664ed4566a84_DO: [0.4, 0.41, 0.38, 0.38, 0.38, 0.38, 0.38, 0.39, 0.37, 0.36, 0.36, 0.34, 0.32, 0.33, 0.34, 0.32, 0.32, 0.31, 0.3, 0.29, 0.32, 0.33, 0.34, 0.33, 0.29, 0.27, 0.27, 0.28, 0.27, 0.27, 0.28, 0.28, 0.29, 0.28, 0.28, 0.25, 0.23, 0.23, 0.22, 0.22, 0.25, 0.31, 0.26, 0.26, 0.24, 0.24, 0.19, 0.2, 0.24, 0.27, 0.27, 0.3, 0.32, 0.33, 0.34, 0.35, 0.36, 0.42, 0.43, 0.45, 0.4, 0.36, 0.36, 0.37, 0.36, 0.38, 0.3, 0.25, 0.24, 0.25, 0.33, 0.29, 0.26, 0.31, 0.28, 0.25, 0.24, 0.25, 0.29, 0.37, 0.32, 0.34, 0.34, 0.33, 0.34, 0.37, 0.37, 0.35, 0.43, 0.42, 0.41, 0.41, 0.38, 0.38, 0.38, 0.35]"

# Extraindo os valores numéricos da string
valores_str = linha_exemplo.split("_DO: ")[1]
valores = eval(valores_str)  # Converte para lista de floats

inicio = time.time()

# Criando o arquivo binário
with open(caminho_arquivo, "wb") as arquivo:
    for _ in range(2_000_000):
        # Escrevendo o prefixo da linha (como texto UTF-8 fixo de 64 bytes)
        prefixo = linha_exemplo.split("_DO: ")[0]
        prefixo_bin = prefixo.encode('utf-8').ljust(64, b'\x00')  # Preenche até 64 bytes com zeros
        arquivo.write(prefixo_bin)

        # Escrevendo os valores como binário
        arquivo.write(struct.pack(f'{len(valores)}f', *valores))

fim = time.time()
print(f"Arquivo binário gerado em {caminho_arquivo}")
print(f"Tempo total: {fim-inicio}")
