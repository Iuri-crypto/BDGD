import time

#from MODELAGEM_LOADSHAPE_MEDIA_TENSAO_BDGD_2023_ENERGISA import gerar_comandos_para_opendss_1
from MODELAGEM_LOADSHAPE_BAIXA_TENSAO_BDGD_2023_ENERGISA import gerar_comandos_para_opendss_2


# Definindo os parâmetros para a conexão com o banco de dados
host = 'localhost'
port = '5432'
dbname = 'BDGD_2023_ENERGISA'
user = 'iuri'
password = 'aa11bb22'

if __name__ == "__main__":
    start_time = time.time()

    # Chama a função que gera os comandos OpenDSS
    #gerar_comandos_para_opendss_1(host, port, dbname, user, password)
    gerar_comandos_para_opendss_2(host, port, dbname, user, password)

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"O tempo de execução foi de {execution_time} segundos.")
