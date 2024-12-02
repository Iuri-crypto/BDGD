import psycopg2
import os
import math
import time


class DataBaseQuery:
    def __init__(self, dbhost, dbport, dbdbname, dbuser, dbpassword):
        """Inicializa os paramêmtros de conexão"""
        self.host = dbhost
        self.port = dbport
        self.dbname = dbdbname
        self.user = dbuser
        self.password = dbpassword
        self.conn = None
        self.cur = None

    def connect(self):
        """ Estabelece a Conexão com o Banco de Dados do PostgreSQL"""
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

    def consulta_banco(self):
        """ Consulta o banco de dados e coleta os dados"""
        try:
            """ Consulta a tabela (untrmt) e coleta os dados das colunas:
                 wkb_geometry, cod_id, pac_1, pac_2 e ctmt

                 Consulta a tabela (eqtrmt) e coleta os dados da colunas:
                 pot_nom, lig, ten_pri, ten_sec, lig_fas_p, lig_fas_s,
                 r, xhl, uni_tr_mt

                 Há a necessidade de cruzar os dados da coluna cod_id
                 da tabela untrmt com a coluna uni_tr_mt da tabela
                 eqtrmt, para pegar todas as informações dos trafos
            """
            query = """
                select
                    ucmt_tab.ene_01,
                    ucmt_tab.ene_02,
                    ucmt_tab.ene_03,
                    ucmt_tab.ene_04,
                    ucmt_tab.ene_05,
                    ucmt_tab.ene_06,
                    ucmt_tab.ene_07,
                    ucmt_tab.ene_08,
                    ucmt_tab.ene_09,
                    ucmt_tab.ene_10,
                    ucmt_tab.ene_11,
                    ucmt_tab.ene_12,
                    ucmt_tab.tip_cc,
                    ucmt_tab.gru_ten,
                    crvcrg.tip_dia,
                    ucmt_tab.pac,
                    ucmt_tab.ctmt,
                    ucmt_tab.fas_con,
                    ucmt_tab.ten_forn,
                    crvcrg.pot_01,
                    crvcrg.pot_02,
                    crvcrg.pot_03,
                    crvcrg.pot_04,
                    crvcrg.pot_05,
                    crvcrg.pot_06,
                    crvcrg.pot_07,
                    crvcrg.pot_08,
                    crvcrg.pot_09,
                    crvcrg.pot_10,
                    crvcrg.pot_11,
                    crvcrg.pot_12,
                    crvcrg.pot_13,
                    crvcrg.pot_14,
                    crvcrg.pot_15,
                    crvcrg.pot_16,
                    crvcrg.pot_17,
                    crvcrg.pot_18,
                    crvcrg.pot_19,
                    crvcrg.pot_20,
                    crvcrg.pot_21,
                    crvcrg.pot_22,
                    crvcrg.pot_23,
                    crvcrg.pot_24,
                    crvcrg.pot_25,
                    crvcrg.pot_26,
                    crvcrg.pot_27,
                    crvcrg.pot_28,
                    crvcrg.pot_29,
                    crvcrg.pot_30,
                    crvcrg.pot_31,
                    crvcrg.pot_32,
                    crvcrg.pot_33,
                    crvcrg.pot_34,
                    crvcrg.pot_35,
                    crvcrg.pot_36,
                    crvcrg.pot_37,
                    crvcrg.pot_38,
                    crvcrg.pot_39,
                    crvcrg.pot_40,
                    crvcrg.pot_41,
                    crvcrg.pot_42,
                    crvcrg.pot_43,
                    crvcrg.pot_44,
                    crvcrg.pot_45,
                    crvcrg.pot_46,
                    crvcrg.pot_47,
                    crvcrg.pot_48,
                    crvcrg.pot_49,
                    crvcrg.pot_50,
                    crvcrg.pot_51,
                    crvcrg.pot_52,
                    crvcrg.pot_53,
                    crvcrg.pot_54,
                    crvcrg.pot_55,
                    crvcrg.pot_56,
                    crvcrg.pot_57,
                    crvcrg.pot_58,
                    crvcrg.pot_59,
                    crvcrg.pot_60,
                    crvcrg.pot_61,
                    crvcrg.pot_62,
                    crvcrg.pot_63,
                    crvcrg.pot_64,
                    crvcrg.pot_65,
                    crvcrg.pot_66,
                    crvcrg.pot_67,
                    crvcrg.pot_68,
                    crvcrg.pot_69,
                    crvcrg.pot_70,
                    crvcrg.pot_71,
                    crvcrg.pot_72,
                    crvcrg.pot_73,
                    crvcrg.pot_74,
                    crvcrg.pot_75,
                    crvcrg.pot_76,
                    crvcrg.pot_77,
                    crvcrg.pot_78,
                    crvcrg.pot_79,
                    crvcrg.pot_80,
                    crvcrg.pot_81,
                    crvcrg.pot_82,
                    crvcrg.pot_83,
                    crvcrg.pot_84,
                    crvcrg.pot_85,
                    crvcrg.pot_86,
                    crvcrg.pot_87,
                    crvcrg.pot_88,
                    crvcrg.pot_89,
                    crvcrg.pot_90,
                    crvcrg.pot_91,
                    crvcrg.pot_92,
                    crvcrg.pot_93,
                    crvcrg.pot_94,
                    crvcrg.pot_95,
                    crvcrg.pot_96,
                    ucmt_tab.cod_id
                FROM 
                    ucmt_tab
                JOIN
                    crvcrg ON ucmt_tab.tip_cc = crvcrg.cod_id
                WHERE
                    ucmt_tab.gru_ten = 'MT'
            
            """
            # Executa a consulta
            self.cur.execute(query)
            results = self.cur.fetchall()
            return results
        except Exception as e:
            print(f"Erro ao gerar comandos para o OpenDSS: {e}")
            return []

    def loads(self):
        """Cria comandos no formato arquivo.dss (bloco de notas) para o OpenDSS"""
        dados = self.consulta_banco()

        # Caminho principal para salvar as subpastas
        base_dir = r'C:\MODELAGEM_CARGAS_TENSÃO_BDGD_2023_ENERGISA'

        # Dicionário para armazenar os ctmt já processados
        ctmts_processados = {}

        # Iterar sobre os dados e gerar uma subpasta para cada ctmt
        for index, linha in enumerate(dados):
            ene_01 = linha[0]
            ene_02 = linha[1]
            ene_03 = linha[2]
            ene_04 = linha[3]
            ene_05 = linha[4]
            ene_06 = linha[5]
            ene_07 = linha[6]
            ene_08 = linha[7]
            ene_09 = linha[8]
            ene_10 = linha[9]
            ene_11 = linha[10]
            ene_12 = linha[11]
            tip_cc = linha[12]
            gru_ten = linha[13]
            tip_dia = linha[14]
            pac = linha[15]
            ctmt = linha[16]
            fas_con = linha[17]
            ten_forn = linha[18]
            pot_01 = linha[19]
            pot_02 = linha[20]
            pot_03 = linha[21]
            pot_04 = linha[22]
            pot_05 = linha[23]
            pot_06 = linha[24]
            pot_07 = linha[25]
            pot_08 = linha[26]
            pot_09 = linha[27]
            pot_10 = linha[28]
            pot_11 = linha[29]
            pot_12 = linha[30]
            pot_13 = linha[31]
            pot_14 = linha[32]
            pot_15 = linha[33]
            pot_16 = linha[34]
            pot_17 = linha[35]
            pot_18 = linha[36]
            pot_19 = linha[37]
            pot_20 = linha[38]
            pot_21 = linha[39]
            pot_22 = linha[40]
            pot_23 = linha[41]
            pot_24 = linha[42]
            pot_25 = linha[43]
            pot_26 = linha[44]
            pot_27 = linha[45]
            pot_28 = linha[46]
            pot_29 = linha[47]
            pot_30 = linha[48]
            pot_31 = linha[49]
            pot_32 = linha[50]
            pot_33 = linha[51]
            pot_34 = linha[52]
            pot_35 = linha[53]
            pot_36 = linha[54]
            pot_37 = linha[55]
            pot_38 = linha[56]
            pot_39 = linha[57]
            pot_40 = linha[58]
            pot_41 = linha[59]
            pot_42 = linha[60]
            pot_43 = linha[61]
            pot_44 = linha[62]
            pot_45 = linha[63]
            pot_46 = linha[64]
            pot_47 = linha[65]
            pot_48 = linha[66]
            pot_49 = linha[67]
            pot_50 = linha[68]
            pot_51 = linha[69]
            pot_52 = linha[70]
            pot_53 = linha[71]
            pot_54 = linha[72]
            pot_55 = linha[73]
            pot_56 = linha[74]
            pot_57 = linha[75]
            pot_58 = linha[76]
            pot_59 = linha[77]
            pot_60 = linha[78]
            pot_61 = linha[79]
            pot_62 = linha[80]
            pot_63 = linha[81]
            pot_64 = linha[82]
            pot_65 = linha[83]
            pot_66 = linha[84]
            pot_67 = linha[85]
            pot_68 = linha[86]
            pot_69 = linha[87]
            pot_70 = linha[88]
            pot_71 = linha[89]
            pot_72 = linha[90]
            pot_73 = linha[91]
            pot_74 = linha[92]
            pot_75 = linha[93]
            pot_76 = linha[94]
            pot_77 = linha[95]
            pot_78 = linha[96]
            pot_79 = linha[97]
            pot_80 = linha[98]
            pot_81 = linha[99]
            pot_82 = linha[100]
            pot_83 = linha[101]
            pot_84 = linha[102]
            pot_85 = linha[103]
            pot_86 = linha[104]
            pot_87 = linha[105]
            pot_88 = linha[106]
            pot_89 = linha[107]
            pot_90 = linha[108]
            pot_91 = linha[109]
            pot_92 = linha[110]
            pot_93 = linha[111]
            pot_94 = linha[112]
            pot_95 = linha[113]
            pot_96 = linha[114]
            cod_id = linha[115]
            # Verificar se o ctmt já foi processado
            if ctmt not in ctmts_processados:
                # Se o ctmt não foi processado ainda, criar uma nova pasta para o ctmt
                ctmt_folder = os.path.join(base_dir, str(ctmt))
                os.makedirs(ctmt_folder, exist_ok=True)

                # Criar o novo arquivo .dss para este ctmt
                file_path = os.path.join(ctmt_folder, 'LOADS.dss')
                file = open(file_path, 'w')

                # Adicionar o ctmt ao dicionario de ctmts processados (armazena o arquivo aberto)
                ctmts_processados[ctmt] = file


            else:
                # Se o ctmt já foi processado, usar o arquivo existente e abrir no modo append ('a')
                file = ctmts_processados[ctmt]

            # Fator de Ajuste para a curva de carga


            mapa_fases = {
                'ABC': '.1.2.3', 'ACB': '.1.3.2', 'BAC': '.1.2.3', 'BCA': '.1.2.3', 'CAB': '.1.2.3', 'CBA': '.1.2.3',
                'ABCN': '.1.2.3', 'ACBN': '.1.2.3', 'BACN': '.1.2.3', 'BCAN': '.1.2.3', 'CABN': '.1.2.3',
                'CBAN': '.1.2.3',
                'ABN': '.1.2', 'ACN': '.1.3', 'BAN': '.1.2', 'CAN': '.1.3', 'A': '.1', 'B': '.2', 'C': '.3', 'AN': '.1',
                'BA': '.1.2', 'BN': '.2', 'CN': '.3', 'AB': '.1.2', 'AC': '.1.3', 'BC': '.2.3',
                'CNA': '.1', 'ANB': '.1.2', 'BNC': '.2.3', 'CA': '.1.3',
            }
            rec_fases = mapa_fases[fas_con]

            command_transformers = f"""
            ! load-ctmt: {ctmt}
            New Load.{cod_id} Bus1 = {pac}{rec_fases} Phases = {len(fas_con)} Conn = Delta Model = 1 Kv = {ten_forn} Kw = {1} Kvar = 0
            """

            if file:
                file.write(command_transformers)

            # Fechar todos os arquivos antes de terminar o loop
        for file in ctmts_processados.values():
            file.close()

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

    # Criar uma instância da classe DatabaseQuery
    db_query = DataBaseQuery(host, port, dbname, user, password)

    # Conectar ao banco de dados
    db_query.connect()

    # Gerar comandos para o OpenDSS
    db_query.loads()

    # Fechar a conexão com o banco de dados
    db_query.close()

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"O tempo de execução foi de {execution_time} segundos.")

    # tem 200 valores de trafos nao conectados a ssdmt porqeu nao tem chave