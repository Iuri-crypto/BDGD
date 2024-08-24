import dash
from dash import dcc, html
import plotly.graph_objs as go
import numpy as np
import pandas as pd

# Inicializar o aplicativo Dash
app = dash.Dash(__name__)

# Gerar dados fictícios para análise
np.random.seed(0)
time = np.linspace(0, 24, 100)  # Tempo em horas
voltages = [np.sin(time / 2 + i) + 1.05 for i in range(3)]  # Variação de tensão para diferentes barramentos
currents = [np.cos(time / 3 + i) + 0.5 for i in range(3)]  # Variação de corrente para diferentes barramentos
potencies = [currents[i] * (voltages[i] + 0.1) for i in range(3)]  # Potência calculada

# Dados para o gráfico de corrente vs. potência
current_power = [currents[i] for i in range(2)]  # Usar apenas os primeiros dois barramentos para simplicidade
power = [potencies[i] for i in range(2)]
labels = ['Barramento 1', 'Barramento 2']

# Dados para o gráfico de mapa de rede
nodes = np.array([
    [0, 0], [1, 0], [2, 0], [3, 0], [4, 0],
    [0, 1], [1, 1], [2, 1], [3, 1], [4, 1],
    [0, 2], [1, 2], [2, 2], [3, 2], [4, 2]
])
edges = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (5, 6), (6, 7), (7, 8), (8, 9),
    (10, 11), (11, 12), (12, 13), (13, 14),
    (0, 5), (1, 6), (2, 7), (3, 8), (4, 9),
    (5, 10), (6, 11), (7, 12), (8, 13), (9, 14)
]
node_labels = [f'Bus {i + 1}' for i in range(len(nodes))]

# Criar DataFrame para o gráfico de mapa
df_map = pd.DataFrame(nodes, columns=['x', 'y'])
df_map['node'] = node_labels
df_map['voltage'] = np.random.uniform(10, 20, size=len(nodes))  # Tensão nos barramentos
df_map['load'] = np.random.uniform(50, 200, size=len(nodes))  # Carga em diferentes barramentos

# Layout do aplicativo
app.layout = html.Div(style={'backgroundColor': '#202020'}, children=[
    html.Header(style={'backgroundColor': '#1F1F1F', 'padding': '10px', 'textAlign': 'center'}, children=[
        html.H1("Dashboard de Análise de Grandezas Elétricas", style={'color': '#E0E0E0', 'fontSize': 36})
    ]),

    html.Div([
        # Gráfico de Variação de Tensão e Corrente ao Longo do Tempo
        html.Div([
            dcc.Graph(
                id='voltage-current-time',
                figure={
                    'data': [
                                go.Scatter(
                                    x=time,
                                    y=voltage,
                                    mode='lines+markers',
                                    line=dict(width=2),
                                    marker=dict(size=6),
                                    name=f'Tensão Barramento {i + 1}'
                                ) for i, voltage in enumerate(voltages)
                            ] + [
                                go.Scatter(
                                    x=time,
                                    y=current,
                                    mode='lines+markers',
                                    line=dict(dash='dash', width=2),
                                    marker=dict(size=6),
                                    name=f'Corrente Barramento {i + 1}'
                                ) for i, current in enumerate(currents)
                            ],
                    'layout': go.Layout(
                        title='Variação de Tensão e Corrente ao Longo do Tempo',
                        plot_bgcolor='#303030',
                        paper_bgcolor='#202020',
                        font=dict(color='#E0E0E0'),
                        xaxis=dict(title='Tempo (Horas)', color='#E0E0E0'),
                        yaxis=dict(title='Valor', color='#E0E0E0'),
                        margin=dict(l=40, r=10, t=40, b=30)
                    )
                }
            )
        ], style={'width': '48%', 'display': 'inline-block'}),

        # Gráfico de Corrente vs. Potência
        html.Div([
            dcc.Graph(
                id='current-power',
                figure={
                    'data': [
                        go.Scatter(
                            x=current_power[i],
                            y=power[i],
                            mode='markers',
                            marker=dict(
                                size=10,
                                color=power[i],
                                colorscale='Viridis',
                                showscale=True
                            ),
                            text=[f'{current:.2f}, {p:.2f}' for current, p in zip(current_power[i], power[i])],
                            name=f'Corrente vs Potência {labels[i]}'
                        ) for i in range(len(current_power))
                    ],
                    'layout': go.Layout(
                        title='Corrente vs Potência',
                        plot_bgcolor='#303030',
                        paper_bgcolor='#202020',
                        font=dict(color='#E0E0E0'),
                        xaxis=dict(title='Corrente (A)', color='#E0E0E0'),
                        yaxis=dict(title='Potência (kW)', color='#E0E0E0'),
                        margin=dict(l=40, r=10, t=40, b=30),
                        coloraxis_colorbar=dict(title='Potência')
                    )
                }
            )
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),
    ], style={'display': 'flex', 'justifyContent': 'space-between'}),

    # Mapa Interativo com Informações de Carga e Tensões
    html.Div([
        dcc.Graph(
            id='network-map',
            figure={
                'data': [
                    go.Scatter(
                        x=df_map['x'],
                        y=df_map['y'],
                        mode='markers+text',
                        text=df_map['node'],
                        textposition='top right',
                        marker=dict(
                            size=12,
                            color=df_map['voltage'],
                            colorscale='Blues',
                            showscale=True,
                            colorbar=dict(title='Tensão')
                        )
                    ),
                    *[
                        go.Scatter(
                            x=[nodes[edge[0], 0], nodes[edge[1], 0]],
                            y=[nodes[edge[0], 1], nodes[edge[1], 1]],
                            mode='lines',
                            line=dict(color='rgb(150, 150, 150)', width=2),
                            showlegend=False
                        ) for edge in edges
                    ]
                ],
                'layout': go.Layout(
                    title='Mapa da Rede Elétrica com Tensão e Carga',
                    plot_bgcolor='#303030',
                    paper_bgcolor='#202020',
                    font=dict(color='#E0E0E0'),
                    xaxis=dict(title='X', color='#E0E0E0'),
                    yaxis=dict(title='Y', color='#E0E0E0'),
                    margin=dict(l=40, r=10, t=40, b=30),
                    coloraxis_colorbar=dict(title='Tensão')
                )
            }
        )
    ], style={'width': '100%'}),
])

# Rodar o aplicativo
if __name__ == '__main__':
    app.run_server(debug=True)
