from qgis.core import QgsApplication, QgsProject
from qgis.utils import iface
import os
import subprocess
import time

# Inicializa a aplicação QGIS com interface gráfica
QgsApplication.setPrefixPath("C:/OSGEO4W/apps/qgis", True)
qgs = QgsApplication([], True)  # True ativa a interface gráfica
qgs.initQgis()

# Nome do projeto
project_path = r"C:\Meu GitHub\Pesquisa_e_Dia_a_Dia\Pesquisa Perdas Não Técnicas\pythonProject\teste08.qgz"  # Altere o caminho conforme necessário

# Cria um novo projeto QGIS
project = QgsProject.instance()
project.setFileName(project_path)

# Caminho para o executável do QGIS
qgis_path = r"C:\Program Files\QGIS 3.38.2\bin\qgis-bin.exe"  # Altere o caminho conforme necessário

# Verifica se o caminho para o QGIS está correto
if not os.path.isfile(qgis_path):
    print(f"O caminho para o QGIS não está correto: {qgis_path}")
else:
    # Abre o projeto QGIS no QGIS Desktop
    process = subprocess.Popen([qgis_path, project_path])

    # Espera 10 segundos para garantir que o QGIS esteja completamente aberto
    time.sleep(10)

    # Interage com o plugin HCMGIS para adicionar e ativar a camada Google Satellite
    try:
        # Aqui você pode precisar ajustar o código conforme a API do plugin HCMGIS
        from qgis.core import QgsPluginManager

        plugin_manager = QgsPluginManager.instance()
        plugin = plugin_manager.plugin("HCMGIS")

        if plugin is not None:
            # Suponha que o plugin já está carregado e configurado
            plugin_instance = plugin.plugin
            iface.pluginToolBar().addAction(plugin_instance.actionGoogleSatellite)
            print("Plugin HCMGIS e camada Google Satellite ativados.")
        else:
            print("Plugin HCMGIS não encontrado.")

    except Exception as e:
        print(f"Erro ao interagir com o plugin HCMGIS: {e}")

    # Salva o projeto QGIS com a configuração do plugin
    project.write()

    # Loop para manter o script ativo enquanto o QGIS estiver aberto
    while True:
        if process.poll() is not None:
            print("QGIS foi fechado.")
            break
        time.sleep(5)  # Espera por 5 segundos antes de verificar novamente

# Finaliza a aplicação QGIS
qgs.exitQgis()

print("Projeto salvo e QGIS iniciado.")
