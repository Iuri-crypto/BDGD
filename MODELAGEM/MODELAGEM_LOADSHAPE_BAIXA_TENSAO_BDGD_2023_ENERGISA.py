import psycopg2
import os
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed


def gerar_comandos_para_opendss_2(dbhost, dbport, dbdbname, dbuser, dbpassword, batch_size=100000):
    """Função que conecta ao banco de dados, gera os comandos no formato desejado e cria os arquivos JSON para o OpenDSS em lotes."""

    # Função para processar os dados de uma tabela
    def processar_tabela(tabela, cur, base_dir):
        """Processa os dados da tabela fornecida e gera arquivos JSON."""

        ctmts_processados = {}
        linhas_processadas = 0
        offset = 0

        while True:
            # Consulta com LIMIT e OFFSET, ajustando para pegar lotes de 100.000 linhas
            query = f"""
                SELECT
                    {', '.join([f"baixa_{tabela}.ene_{i:02d}" for i in range(1, 13)])},
                    baixa_{tabela}.tip_cc, baixa_{tabela}.gru_ten, baixa_{tabela}.tip_dia,
                    baixa_{tabela}.pac, baixa_{tabela}.ctmt, baixa_{tabela}.fas_con,
                    baixa_{tabela}.ten_forn,
                    {', '.join([f"baixa_{tabela}.pot_{i:02d}" for i in range(1, 97)])},
                    baixa_{tabela}.cod_id
                FROM
                    baixa_{tabela}
                LIMIT {batch_size} OFFSET {offset}
            """

            try:
                cur.execute(query)
                dados = cur.fetchall()

                if not dados:
                    break  # Se não houver mais dados, sai do loop
            except Exception as e:
                print(f"Erro ao consultar dados da tabela {tabela}: {e}")
                break

            # Processar os dados de cada linha em paralelo
            with ThreadPoolExecutor() as executor:
                futures = []
                for linha in dados:
                    futures.append(executor.submit(processar_linha, linha, ctmts_processados, base_dir))

                # Aguardar o término de todas as tarefas
                for future in as_completed(futures):
                    future.result()  # Espera a conclusão de cada tarefa

            # Atualizar o offset para o próximo lote
            offset += batch_size

        print(f"Processamento concluído para a tabela {tabela}.")

    def processar_linha(linha, ctmts_processados, base_dir):
        """Processa uma linha de dados e gera o arquivo JSON correspondente."""

        ene_values = linha[:12]  # ene_01 a ene_12
        tip_cc = linha[12]
        gru_ten = linha[13]
        tip_dia = linha[14]
        pac = linha[15]
        ctmt = linha[16]
        pot_values = linha[19:115]  # pot_01 a pot_96
        cod_id = linha[115]

        # Verificar se o ctmt já foi processado
        if ctmt not in ctmts_processados:
            # Se o ctmt não foi processado ainda, criar uma nova pasta para o ctmt
            ctmt_folder = os.path.join(base_dir, str(ctmt))
            os.makedirs(ctmt_folder, exist_ok=True)

        for ene_index, ene in enumerate(ene_values):
            ene_folder = os.path.join(ctmt_folder, str(ene_index + 1))
            os.makedirs(ene_folder, exist_ok=True)

            # Criar um arquivo JSON para cada cod_id para os 3 tipos de dia
            for tip in ['DU', 'SA', 'DO']:
                file_name = f"{cod_id}_{tip}.json"
                file_path = os.path.join(ene_folder, file_name)

                # Calcular o fator de ajuste e as potências ajustadas
                energia_curva_de_carga = sum(pot_values) * 0.25
                f = (int(ene_values[ene_index]) / 30) / energia_curva_de_carga
                potencias_ajustadas = [round(f * pot, 2) for pot in pot_values]

                # Gerar o conteúdo baseado no tipo de dia
                command_loadshapes = {"loadshape": potencias_ajustadas}

                # Escrever no arquivo JSON
                with open(file_path, 'w') as file:
                    json.dump(command_loadshapes, file, indent=4)

    # Estabelecendo a conexão com o banco de dados
    try:
        conn = psycopg2.connect(
            dbname=dbdbname,
            user=dbuser,
            password=dbpassword,
            host=dbhost,
            port=dbport
        )
        cur = conn.cursor()
        print("Conexão Estabelecida com Sucesso.")
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return

    # Caminho principal para salvar as subpastas
    base_dir = r'C:\MODELAGEM_LOADSHAPES_BAIXA_TENSAO_BDGD_2023_ENERGISA'

    # Processar os dados de todas as tabelas em paralelo
    tabelas = ['1', '2', '3', '4', '6', '7']
    with ThreadPoolExecutor() as executor:
        futures = []
        for tabela in tabelas:
            futures.append(executor.submit(processar_tabela, tabela, cur, base_dir))

        # Aguardar a conclusão de todos os processos
        for future in as_completed(futures):
            future.result()

    # Fechar a conexão com o banco de dados
    if cur:
        cur.close()
    if conn:
        conn.close()

    print("Conexão com o banco de dados fechada.")
    print("Arquivos gerados com sucesso.")


# Para executar a função, basta chamar:
if __name__ == "__main__":
    host = 'localhost'
    port = '5432'
    dbname = 'BDGD_2023_ENERGISA'
    user = 'iuri'
    password = 'aa11bb22'

    start_time = time.time()

    # Chama a função para gerar os comandos OpenDSS
    gerar_comandos_para_opendss_2(host, port, dbname, user, password)

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"O tempo de execução foi de {execution_time} segundos.")
