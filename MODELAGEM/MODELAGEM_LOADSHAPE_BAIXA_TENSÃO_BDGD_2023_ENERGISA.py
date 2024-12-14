import psycopg2
import os
import time

class DataBaseQuery:
    def __init__(self, dbhost, dbport, dbdbname, dbuser, dbpassword):
        """Inicializa os parâmetros de conexão"""
        self.host = dbhost
        self.port = dbport
        self.dbname = dbdbname
        self.user = dbuser
        self.password = dbpassword
        self.conn = None
        self.cur = None

    def connect(self):
        """Estabelece a conexão com o Banco de Dados do PostgreSQL"""
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cur = self.conn.cursor()
            print("Conexão Estabelecida com Sucesso.")
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def consulta_banco_por_ctmt(self, ctmt):
        """Consulta o banco de dados e coleta os dados de um único CTMT de cada vez"""
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
                    ucbt_tab.gru_ten = 'BT' AND ucbt_tab.ctmt = %s
            """
            # Executa a consulta para o ctmt específico
            self.cur.execute(query, (ctmt,))
            results = self.cur.fetchall()
            return results
        except Exception as e:
            print(f"Erro ao gerar comandos para o OpenDSS: {e}")
            return []

    def loads(self):
        """Cria comandos no formato arquivo.dss (bloco de notas) para o OpenDSS"""
        # Caminho principal para salvar as subpastas
        base_dir = r'C:\MODELAGEM_LOADSHAPES_BAIXA_TENSÃO_BDGD_2023_ENERGISA_teste01'

        # Dicionário para armazenar os ctmt já processados
        ctmts_processados = {}

        # Consultar todos os CTMTs únicos
        try:
            self.cur.execute("SELECT DISTINCT ctmt FROM ucbt_tab WHERE gru_ten = 'BT'")
            ctmts = self.cur.fetchall()
        except Exception as e:
            print(f"Erro ao buscar os CTMTs: {e}")
            return

        print(f"Processando {len(ctmts)} CTMTs...")

        # Iterar sobre os CTMTs
        for ctmt_row in ctmts:
            ctmt = ctmt_row[0]
            print(f"Processando CTMT: {ctmt}...")  # Mensagem para exibir o nome do CTMT em execução

            # Consultar dados para o CTMT específico
            dados = self.consulta_banco_por_ctmt(ctmt)

            if not dados:  # Se não houver dados, continuar para o próximo CTMT
                print(f"Nenhum dado encontrado para o CTMT {ctmt}.")
                continue

            # Dicionário para armazenar os ctmt já processados
            if ctmt not in ctmts_processados:
                ctmts_processados[ctmt] = True

                # Criar pasta para o ctmt, se não existir
                ctmt_folder = os.path.join(base_dir, str(ctmt))
                os.makedirs(ctmt_folder, exist_ok=True)

            # Processar os dados para este CTMT
            for linha in dados:
                ene_values = linha[:12]  # ene_01 a ene_12
                tip_cc = linha[12]
                gru_ten = linha[13]
                tip_dia = linha[14]
                pac = linha[15]
                ctmt = linha[16]
                pot_values = linha[19:115]  # pot_01 a pot_96
                cod_id = linha[115]

                # Processar apenas o primeiro mês (ene_01) e verificar se já foi processado o ctmt
                ene_index = 0  # Correspondente a ene_01
                ene = ene_values[ene_index]

                # Gerar nome do arquivo para ene_01
                ene_filename = f"LoadShape_ene_01.txt"
                file_path = os.path.join(ctmt_folder, ene_filename)

                # Fator de Ajuste para a curva de carga
                energia_curva_de_carga = sum(pot_values) * 0.25
                f = (int(ene_values[ene_index]) / 30) / energia_curva_de_carga

                # Calcular potências ajustadas
                potencias_ajustadas = [f * pot for pot in pot_values]

                # Abrir e escrever no arquivo correspondente
                with open(file_path, 'a') as file:
                    if tip_dia == 'DU':
                        command_loadshapes = f"LoadShape_dia_util.{cod_id} = {', '.join(map(str, potencias_ajustadas))}\n"
                    elif tip_dia == 'SA':
                        command_loadshapes = f"LoadShape_sabado.{cod_id} = {', '.join(map(str, potencias_ajustadas))}\n"
                    elif tip_dia == 'DO':
                        command_loadshapes = f"LoadShape_domingos_e_feriados.{cod_id} = {', '.join(map(str, potencias_ajustadas))}\n"

                    # Escrever o comando no arquivo
                    file.write(command_loadshapes + "\n")

        print("Arquivos gerados com sucesso.")

    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        print("Conexão com o banco de dados fechada.")


# Uso da classe
if __name__ == "__main__":
    # Parâmetros de conexão
    host = 'localhost'
    port = '5432'
    dbname = 'BDGD_2023_ENERGISA'
    user = 'iuri'
    password = 'aa11bb22'

    start_time = time.time()

    # Criar uma instância da classe DataBaseQuery
    db_query = DataBaseQuery(host, port, dbname, user, password)

    # Conectar ao banco de dados
    db_query.connect()

    # Gerar comandos para o OpenDSS
    db_query.loads()

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"O tempo de execução foi de {execution_time} segundos.")
