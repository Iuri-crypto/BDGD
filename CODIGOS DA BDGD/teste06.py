from qgis.core import QgsProject, QgsVectorLayer

# Cria uma instância da camada
layer = QgsVectorLayer("path/to/your/layer.shp", "Layer Name", "ogr")

if layer.isValid():
    # Adiciona a camada ao projeto
    QgsProject.instance().addMapLayer(layer)

    # Define a opacidade da camada (0 a 1)
    layer.setOpacity(0.5)  # 50% de transparência

    # Atualiza o projeto
    QgsProject.instance().reload()
else:
    print("Camada inválida.")
