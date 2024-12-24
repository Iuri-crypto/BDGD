import sqlite3
import os

# Caminho do diretório onde estão os arquivos .sql
diretorio_sql = r'C:\Users\muril\OneDrive\Documentos\SEXTO_SEMESTRE\PROJETO_DE_PESQUISA\BDGD_ENERGIZA MT\output_sql'

# Caminho para o banco de dados SQLite (será criado se não existir)
caminho_banco = r'C:\Users\muril\OneDrive\Documentos\SEXTO_SEMESTRE\PROJETO_DE_PESQUISA\BDGD_ENERGIZA MT\meu_banco.db'

# Conectar ao banco de dados SQLite (será criado se não existir)
conn = sqlite3.connect(caminho_banco)
cursor = conn.cursor()


# Função para substituir caracteres nulos por '0'
def substituir_caracteres_nulos(script_sql):
    return script_sql.replace('\x00', '0')  # Substitui caracteres nulos por '0'


# Iterar sobre todos os arquivos .sql no diretório especificado
for arquivo in os.listdir(diretorio_sql):
    if arquivo.endswith('.sql'):
        # Caminho completo do arquivo
        caminho_arquivo = os.path.join(diretorio_sql, arquivo)

        try:
            with open(caminho_arquivo, 'r', encoding='latin1') as file:
                sql_script = file.read()

                # Substituir caracteres nulos por '0'
                sql_script = substituir_caracteres_nulos(sql_script)

            # Executar o script SQL no banco de dados
            print(f"Executando o script: {arquivo}")
            cursor.executescript(sql_script)
            print(f"Script {arquivo} executado com sucesso.")

        except sqlite3.OperationalError as e:
            print(f"Erro ao executar o script {arquivo}: {e}")
            print(f"Erro no trecho do SQL: {sql_script[:500]}...")  # Exibe o início do SQL com erro para diagnóstico

        except Exception as e:
            print(f"Erro desconhecido ao executar o script {arquivo}: {e}")

# Confirmar as alterações
conn.commit()

# Fechar a conexão com o banco de dados
conn.close()

print("Todos os scripts foram executados e o banco de dados foi atualizado.")
