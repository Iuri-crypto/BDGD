import dash
from dash import dcc, html
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
import io
import base64  # Importar o módulo base64 para codificar a imagem

# Configuração do Dash
app = dash.Dash(__name__)


# Função para criar o gráfico com a imagem do transformador
def create_circuit_figure():
    fig, ax = plt.subplots(figsize=(6, 6))

    # Coordenadas dos barramentos
    barramentos = {
        1: (0.2, 0.8),
        5: (0.6, 0.2)
    }

    # Caminho para a imagem do transformador
    image_path = "C:\py_dss_interface_Mini_Curso\IEEE34_BUS_py\download.jpg"

    # Função para adicionar a imagem ao gráfico
    def add_image_to_ax(ax, image_path, xy, zoom=0.1):
        img = mpimg.imread(image_path)
        imagebox = OffsetImage(img, zoom=zoom, resample=True)
        ab = AnnotationBbox(imagebox, xy, frameon=False, pad=0.5)
        ax.add_artist(ab)

    # Exemplo de linhas elétricas entre barramentos
    for (start, end) in [(1, 5)]:
        x_values = [barramentos[start][0], barramentos[end][0]]
        y_values = [barramentos[start][1], barramentos[end][1]]
        ax.plot(x_values, y_values, 'k-')  # Linha preta para o circuito

    # Adicionar os barramentos ao gráfico
    for key, value in barramentos.items():
        ax.plot(value[0], value[1], 'ro')  # Barramentos como pontos vermelhos

    # Adicionar a imagem aos barramentos 1 e 5
    for key in barramentos:
        add_image_to_ax(ax, image_path, barramentos[key])

    # Configurações do gráfico
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.set_xlabel('Coordenada X')
    ax.set_ylabel('Coordenada Y')
    ax.set_title('Circuito IEEE 34 Barramentos com Transformadores')

    # Converter a imagem do gráfico para um formato que o Dash pode usar
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_bytes = buf.getvalue()
    plt.close(fig)

    return img_bytes


# Função para criar o gráfico do perfil de tensão
def create_voltage_profile_figure():
    # Dados fictícios para o exemplo
    distancias = np.linspace(0, 10, 100)
    tensao = np.sin(distancias) + 10

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=distancias, y=tensao, mode='lines+markers', name='Perfil de Tensão'))
    fig.update_layout(
        title='Perfil de Tensão em Relação à Distância',
        xaxis_title='Distância (km)',
        yaxis_title='Tensão (V)',
        template='plotly_dark'
    )

    return fig


# Layout do dashboard
app.layout = html.Div([
    html.Div([
        html.H1("Dashboard de Análise de Circuito Elétrico"),
        html.Div([
            dcc.Graph(
                id='circuit-figure',
                figure={
                    'data': [
                        {
                            'type': 'image',
                            'source': 'data:image/png;base64,' + base64.b64encode(create_circuit_figure()).decode()
                        }
                    ],
                    'layout': go.Layout(
                        title='Circuito IEEE 34 Barramentos com Transformadores',
                        xaxis=dict(showticklabels=False),
                        yaxis=dict(showticklabels=False),
                        template='plotly_dark'
                    )
                }
            )
        ], style={'width': '60%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(
                id='voltage-profile-figure',
                figure=create_voltage_profile_figure()
            )
        ], style={'width': '40%', 'display': 'inline-block'})
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
