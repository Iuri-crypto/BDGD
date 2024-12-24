import psycopg2
import os
import time

def gerar_comandos_para_opendss_1(dbhost, dbport, dbdbname, dbuser, dbpassword):
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

    try:
        query = """
            SELECT
                ucmt_tab.ene_01, ucmt_tab.ene_02, ucmt_tab.ene_03, ucmt_tab.ene_04, ucmt_tab.ene_05,
                ucmt_tab.ene_06, ucmt_tab.ene_07, ucmt_tab.ene_08, ucmt_tab.ene_09, ucmt_tab.ene_10,
                ucmt_tab.ene_11, ucmt_tab.ene_12, ucmt_tab.tip_cc, ucmt_tab.gru_ten, crvcrg.tip_dia,
                ucmt_tab.pac, ucmt_tab.ctmt, ucmt_tab.fas_con, ucmt_tab.ten_forn,
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
                crvcrg.pot_96, ucmt_tab.cod_id
            FROM 
                ucmt_tab
            JOIN
                crvcrg ON ucmt_tab.tip_cc = crvcrg.cod_id
            WHERE
                ucmt_tab.gru_ten = 'MT'
            ORDER BY ctmt
        """
        cur.execute(query)
        dados = cur.fetchall()
    except Exception as e:
        print(f"Erro ao gerar comandos para o OpenDSS: {e}")
        return

    base_dir = r'C:\MODELAGEM_LOADSHAPES_MEDIA_TENSAO_BDGD_2023_ENERGISA'
    ctmts_processados = {}

    def gerar_arquivo_txt(ene_index, ene_values, pot_values, cod_id, ctmt_folder, tip_dia):
        ene_folder = os.path.join(ctmt_folder, str(ene_index + 1))
        os.makedirs(ene_folder, exist_ok=True)
        txt_file_path = os.path.join(ene_folder, f"mes_{ene_index + 1}_{tip_dia}.txt")
        energia_curva_de_carga = sum(pot_values) * 0.25
        f = (int(ene_values[ene_index]) / 30) / energia_curva_de_carga
        potencias_ajustadas = [round(f * pot, 2) for pot in pot_values]
        with open(txt_file_path, 'a') as file:
            file.write(f"{cod_id}_{tip_dia}: {potencias_ajustadas}\n")

    for index, linha in enumerate(dados):
        ene_values = linha[:12]
        tip_cc = linha[12]
        gru_ten = linha[13]
        tip_dia = linha[14]
        pac = linha[15]
        ctmt = linha[16]
        pot_values = linha[19:115]
        cod_id = linha[115]

        if ctmt not in ctmts_processados:
            ctmt_folder = os.path.join(base_dir, str(ctmt))
            os.makedirs(ctmt_folder, exist_ok=True)
            ctmts_processados[ctmt] = ctmt_folder

        for ene_index, ene in enumerate(ene_values):
            gerar_arquivo_txt(ene_index, ene_values, pot_values, cod_id, ctmts_processados[ctmt], tip_dia)

    if cur:
        cur.close()
    if conn:
        conn.close()
    print("Conexão com o banco de dados fechada.")
    print("Arquivos gerados com sucesso.")

if __name__ == "__main__":
    host = 'localhost'
    port = '5432'
    dbname = 'BDGD_2023_ENERGISA'
    user = 'iuri'
    password = 'aa11bb22'

    start_time = time.time()
    gerar_comandos_para_opendss_1(host, port, dbname, user, password)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"O tempo de execução foi de {execution_time} segundos.")
