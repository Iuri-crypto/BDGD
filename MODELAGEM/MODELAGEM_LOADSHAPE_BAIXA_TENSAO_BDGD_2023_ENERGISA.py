import psycopg2
import os
import time
import json

def gerar_comandos_para_opendss_2(dbhost, dbport, dbdbname, dbuser, dbpassword):
    """Função que conecta ao banco de dados, gera os comandos no formato desejado e cria os arquivos JSON para o OpenDSS"""

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

    # Consulta ao banco de dados
    try:
        query = """
            SELECT
                ucbt_tab.ene_01, ucbt_tab.ene_02, ucbt_tab.ene_03, ucbt_tab.ene_04, ucbt_tab.ene_05,
                ucbt_tab.ene_06, ucbt_tab.ene_07, ucbt_tab.ene_08, ucbt_tab.ene_09, ucbt_tab.ene_10,
                ucbt_tab.ene_11, ucbt_tab.ene_12, ucbt_tab.tip_cc, ucbt_tab.gru_ten, crvcrg.tip_dia,
                ucbt_tab.pac, ucbt_tab.ctmt, ucbt_tab.fas_con, ucbt_tab.ten_forn,
                crvcrg.pot_01, crvcrg.pot_02, crvcrg.pot_03, crvcrg.pot_04, crvcrg.pot_05, 
                crvcrg.pot_06, crvcrg.pot_07, crvcrg.pot_08, crvcrg.pot_09, crvcrg.pot_10,
                crvcrg.pot_11, crvcrg.pot_12, crvcrg.pot_13, crvcrg.pot_14, crvcrg.pot_15, 
                crvcrg.pot_16, crvcrg.pot_17, crvcrg.pot_18, crvcrg.pot_19, crvcrg.pot_20,
                crvcrg.pot_21, crvcrg.pot_22, crvcrg.pot_23, crvcrg.pot_24, crvcrg.pot_25, 
                crvcrg.pot_26, crvcrg.pot_27, crvcrg.pot_28, crvcrg.pot_29, crvcrg.pot_30, 
                crvcrg.pot_31, crvcrg.pot_32, crvcrg.pot_33, crvcrg.pot_34, crvcrg.pot_35, 
                crvcrg.pot_36, crvcrg.pot_37, crvcrg.pot_38, crvcrg.pot_39, crvcrg.pot_40,
                crvcrg.pot_41, crvcrg.pot_42, crvcrg.pot_43, crvcrg.pot_44, crvcrg.pot_45, 
                crvcrg.pot_46, crvcrg.pot_47, crvcrg.pot_48, crvcrg.pot_49, crvcrg.pot_50, 
                crvcrg.pot_51, crvcrg.pot_52, crvcrg.pot_53, crvcrg.pot_54, crvcrg.pot_55, 
                crvcrg.pot_56, crvcrg.pot_57, crvcrg.pot_58, crvcrg.pot_59, crvcrg.pot_60,
                crvcrg.pot_61, crvcrg.pot_62, crvcrg.pot_63, crvcrg.pot_64, crvcrg.pot_65,
                crvcrg.pot_66, crvcrg.pot_67, crvcrg.pot_68, crvcrg.pot_69, crvcrg.pot_70,
                crvcrg.pot_71, crvcrg.pot_72, crvcrg.pot_73, crvcrg.pot_74, crvcrg.pot_75,
                crvcrg.pot_76, crvcrg.pot_77, crvcrg.pot_78, crvcrg.pot_79, crvcrg.pot_80,
                crvcrg.pot_81, crvcrg.pot_82, crvcrg.pot_83, crvcrg.pot_84, crvcrg.pot_85,
                crvcrg.pot_86, crvcrg.pot_87, crvcrg.pot_88, crvcrg.pot_89, crvcrg.pot_90,
                crvcrg.pot_91, crvcrg.pot_92, crvcrg.pot_93, crvcrg.pot_94, crvcrg.pot_95,
                crvcrg.pot_96, ucbt_tab.cod_id
            FROM 
                ucbt_tab
            JOIN
                crvcrg ON ucbt_tab.tip_cc = crvcrg.cod_id
            WHERE
                ucbt_tab.gru_ten = 'BT'
            ORDER BY ctmt
        """
        cur.execute(query)
        dados = cur.fetchall()

    except Exception as e:
        print(f"Erro ao gerar comandos para o OpenDSS: {e}")
        return

    # Caminho principal para salvar as subpastas
    base_dir = r'C:\MODELAGEM_LOADSHAPES_BAIXA_TENSAO_BDGD_2023_ENERGISA'

    # Dicionário para armazenar os ctmt já processados
    ctmts_processados = {}

    # Iterar sobre os dados e gerar uma subpasta para cada ctmt
    for index, linha in enumerate(dados):
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
                potencias_ajustadas = [f * pot for pot in pot_values]

                # Gerar o conteúdo baseado no tipo de dia
                if tip == 'DU':
                    command_loadshapes = {"LoadShape_dia_util": ', '.join(map(str, potencias_ajustadas))}
                elif tip == 'SA':
                    command_loadshapes = {"LoadShape_sabado": ', '.join(map(str, potencias_ajustadas))}
                elif tip == 'DO':
                    command_loadshapes = {"LoadShape_domingos_e_feriados": ', '.join(map(str, potencias_ajustadas))}

                # Escrever no arquivo JSON
                with open(file_path, 'w') as file:
                    json.dump(command_loadshapes, file, indent=4)

    # Fechar a conexão com o banco de dados
    if cur:
        cur.close()
    if conn:
        conn.close()
    print("Conexão com o banco de dados fechada.")
    print("Arquivos gerados com sucesso.")

# Para executar a função, basta chamar:
# Exemplo de uso
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
