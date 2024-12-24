import os
import json
import sqlite3
import time


def gerar_comandos_para_opendss_2_from_sql(output_dir):
    """Função que lê os dados das tabelas UCBT_tab e CRVCRG, gera os comandos no formato desejado e cria os arquivos JSON para o OpenDSS"""

    # Caminho principal para salvar as subpastas
    base_dir = r'C:\MODELAGEM_LOADSHAPES_BAIXA_TENSAO_BDGD_2023_ENERGISA'

    # Dicionário para armazenar os ctmt já processados
    ctmts_processados = {}

    # Caminhos específicos para as tabelas UCBT_tab e CRVCRG
    ucbt_path = os.path.join(output_dir, "UCBT_tab.sql")
    crvcrg_path = os.path.join(output_dir, "CRVCRG.sql")

    # Verificar se os arquivos SQL existem
    if not os.path.exists(ucbt_path) or not os.path.exists(crvcrg_path):
        print("Os arquivos UCBT_tab.sql ou CRVCRG.sql não foram encontrados no diretório.")
        return

    try:
        # Conectar ao banco de dados UCBT_tab
        conn_ucbt = sqlite3.connect(ucbt_path)
        cur_ucbt = conn_ucbt.cursor()

        # Conectar ao banco de dados CRVCRG
        conn_crvcrg = sqlite3.connect(crvcrg_path)
        cur_crvcrg = conn_crvcrg.cursor()

        # Consulta para obter os dados necessários das tabelas
        query = """
            SELECT 
                UCBT_tab.ene_01, UCBT_tab.ene_02, UCBT_tab.ene_03, UCBT_tab.ene_04, UCBT_tab.ene_05, 
                UCBT_tab.ene_06, UCBT_tab.ene_07, UCBT_tab.ene_08, UCBT_tab.ene_09, UCBT_tab.ene_10, 
                UCBT_tab.ene_11, UCBT_tab.ene_12, UCBT_tab.tip_cc, UCBT_tab.gru_ten, CRVCRG.tip_dia, 
                UCBT_tab.pac, UCBT_tab.ctmt, UCBT_tab.fas_con, UCBT_tab.ten_forn,
                CRVCRG.pot_01, CRVCRG.pot_02, CRVCRG.pot_03, CRVCRG.pot_04, CRVCRG.pot_05,
                CRVCRG.pot_06, CRVCRG.pot_07, CRVCRG.pot_08, CRVCRG.pot_09, CRVCRG.pot_10,
                CRVCRG.pot_11, CRVCRG.pot_12, CRVCRG.pot_13, CRVCRG.pot_14, CRVCRG.pot_15, 
                CRVCRG.pot_16, CRVCRG.pot_17, CRVCRG.pot_18, CRVCRG.pot_19, CRVCRG.pot_20,
                CRVCRG.pot_21, CRVCRG.pot_22, CRVCRG.pot_23, CRVCRG.pot_24, CRVCRG.pot_25, 
                CRVCRG.pot_26, CRVCRG.pot_27, CRVCRG.pot_28, CRVCRG.pot_29, CRVCRG.pot_30, 
                CRVCRG.pot_31, CRVCRG.pot_32, CRVCRG.pot_33, CRVCRG.pot_34, CRVCRG.pot_35, 
                CRVCRG.pot_36, CRVCRG.pot_37, CRVCRG.pot_38, CRVCRG.pot_39, CRVCRG.pot_40,
                CRVCRG.pot_41, CRVCRG.pot_42, CRVCRG.pot_43, CRVCRG.pot_44, CRVCRG.pot_45, 
                CRVCRG.pot_46, CRVCRG.pot_47, CRVCRG.pot_48, CRVCRG.pot_49, CRVCRG.pot_50, 
                CRVCRG.pot_51, CRVCRG.pot_52, CRVCRG.pot_53, CRVCRG.pot_54, CRVCRG.pot_55, 
                CRVCRG.pot_56, CRVCRG.pot_57, CRVCRG.pot_58, CRVCRG.pot_59, CRVCRG.pot_60,
                CRVCRG.pot_61, CRVCRG.pot_62, CRVCRG.pot_63, CRVCRG.pot_64, CRVCRG.pot_65,
                CRVCRG.pot_66, CRVCRG.pot_67, CRVCRG.pot_68, CRVCRG.pot_69, CRVCRG.pot_70,
                CRVCRG.pot_71, CRVCRG.pot_72, CRVCRG.pot_73, CRVCRG.pot_74, CRVCRG.pot_75,
                CRVCRG.pot_76, CRVCRG.pot_77, CRVCRG.pot_78, CRVCRG.pot_79, CRVCRG.pot_80,
                CRVCRG.pot_81, CRVCRG.pot_82, CRVCRG.pot_83, CRVCRG.pot_84, CRVCRG.pot_85,
                CRVCRG.pot_86, CRVCRG.pot_87, CRVCRG.pot_88, CRVCRG.pot_89, CRVCRG.pot_90,
                CRVCRG.pot_91, CRVCRG.pot_92, CRVCRG.pot_93, CRVCRG.pot_94, CRVCRG.pot_95,
                CRVCRG.pot_96, UCBT_tab.cod_id
            FROM UCBT_tab
            JOIN CRVCRG ON UCBT_tab.tip_cc = CRVCRG.cod_id
            WHERE UCBT_tab.gru_ten = 'BT'
            ORDER BY UCBT_tab.ctmt
        """

        # Executar consulta
        cur_ucbt.execute(query)
        dados = cur_ucbt.fetchall()

        # Iterar sobre os dados e processar
        for linha in dados:
            ene_values = linha[:12]  # ene_01 a ene_12
            ctmt = linha[16]
            pot_values = linha[19:115]
            cod_id = linha[115]

            # Processar apenas novos ctmt
            if ctmt not in ctmts_processados:
                ctmt_folder = os.path.join(base_dir, str(ctmt))
                os.makedirs(ctmt_folder, exist_ok=True)

            for ene_index, ene in enumerate(ene_values):
                ene_folder = os.path.join(ctmt_folder, str(ene_index + 1))
                os.makedirs(ene_folder, exist_ok=True)

                for tip in ['DU', 'SA', 'DO']:
                    file_name = f"{cod_id}_{tip}.json"
                    file_path = os.path.join(ene_folder, file_name)

                    energia_curva_de_carga = sum(pot_values) * 0.25
                    f = (int(ene_values[ene_index]) / 30) / energia_curva_de_carga
                    potencias_ajustadas = [round(f * pot, 2) for pot in pot_values]

                    command_loadshapes = {"loadshape": potencias_ajustadas}

                    with open(file_path, 'w') as file:
                        json.dump(command_loadshapes, file, indent=4)

        # Fechar conexões
        cur_ucbt.close()
        conn_ucbt.close()

        cur_crvcrg.close()
        conn_crvcrg.close()

        print("Processamento concluído com sucesso.")
    except sqlite3.Error as e:
        print(f"Erro ao acessar os bancos de dados: {e}")


# Para executar a função
if __name__ == "__main__":
    output_dir = r"C:\Users\muril\OneDrive\Documentos\SEXTO_SEMESTRE\PROJETO_DE_PESQUISA\BDGD_ENERGIZA MT\output_sql"

    start_time = time.time()

    gerar_comandos_para_opendss_2_from_sql(output_dir)

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"O tempo de execução foi de {execution_time} segundos.")
