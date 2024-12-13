import os

class ComandoDSSGenerator:
    def __init__(self, caminho_pasta_1, caminhos_outros, caminho_saida_principal):
        """Inicializa os parâmetros para geração dos arquivos DSS"""
        self.caminho_pasta_1 = caminho_pasta_1
        self.caminhos_outros = caminhos_outros
        self.caminho_saida_principal = caminho_saida_principal

    def criar_comando_dss(self, caminho_pasta_1, caminhos_outros, arquivo_dss):
        """Escreve os comandos no arquivo DSS conforme as pastas encontradas em todos os caminhos."""
        for caminho in caminhos_outros:
            caminho_completo_pasta = os.path.join(caminho, os.path.basename(caminho_pasta_1))
            if os.path.isdir(caminho_completo_pasta):
                # Escrever o comando COMPILE com o caminho da pasta correspondente
                arquivo_dss.write(f'Redirect "{caminho_completo_pasta}"\n')

    def gerar_comandos_dss(self):
        """Gera arquivos DSS com os comandos para todas as pastas correspondentes nos caminhos."""
        try:
            # Cria a pasta principal para armazenar os arquivos DSS
            os.makedirs(self.caminho_saida_principal, exist_ok=True)

            # Percorre todas as subpastas no primeiro caminho
            for pasta_1 in os.listdir(self.caminho_pasta_1):
                caminho_completo_pasta_1 = os.path.join(self.caminho_pasta_1, pasta_1)

                if os.path.isdir(caminho_completo_pasta_1):
                    # Cria a subpasta para cada pasta encontrada em "caminho_pasta_1"
                    caminho_subpasta_saida = os.path.join(self.caminho_saida_principal, pasta_1)
                    os.makedirs(caminho_subpasta_saida, exist_ok=True)

                    # Cria o arquivo DSS dentro da subpasta correspondente
                    caminho_arquivo_dss = os.path.join(caminho_subpasta_saida, f"{pasta_1}.dss")
                    with open(caminho_arquivo_dss, 'w') as arquivo_dss:
                        # Chama a função para gerar os comandos no arquivo DSS
                        self.criar_comando_dss(caminho_completo_pasta_1, self.caminhos_outros, arquivo_dss)

            print(f"Arquivos DSS gerados com sucesso em {self.caminho_saida_principal}.")
        except Exception as e:
            print(f"Erro ao gerar os arquivos DSS: {e}")

if __name__ == "__main__":
    # Caminho para o primeiro diretório
    caminho_pasta_1 = r"C:\MODELAGEM_BARRA_SLACK_MÉDIA_TENSÃO_BDGD_2023_ENERGISA"

    # Outros caminhos para verificar as subpastas
    caminhos_outros = [
        r"C:\MODELAGEM_CARGAS_MEDIA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_CHAVES_SECCIONADORAS_BAIXA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_CHAVES_SECCIONADORAS_MÉDIA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_COMPENSADORES_DE_REATIVO_BAIXA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_COMPENSADORES_DE_REATIVO_MÉDIA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_GERADORES_MÉDIA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_LINECODES_BAIXA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_LINECODES_MEDIA_TENSAO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_LINHAS_BAIXA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_LINHAS_MÉDIA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_LINHAS_MÉDIA_TENSÃO_BDGD_2023_ENERGISA_tradicional",
        r"C:\MODELAGEM_LOADSHAPES_BAIXA_TENSÃO_BDGD_2023_ENERGISA",
        r"C:\MODELAGEM_LOADSHAPES_BAIXA_TENSÃO_BDGD_2023_ENERGISA_PRIMEIRO"
    ]

    # Caminho para salvar a pasta principal onde os arquivos DSS serão armazenados
    caminho_saida_principal = r"C:\comandos_dss"

    # Criar uma instância da classe ComandoDSSGenerator e gerar os arquivos DSS
    dss_generator = ComandoDSSGenerator(caminho_pasta_1, caminhos_outros, caminho_saida_principal)
    dss_generator.gerar_comandos_dss()
