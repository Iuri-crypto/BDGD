import dash
from dash import dcc, html
import plotly.graph_objs as go
import numpy as np

# Inicializar o aplicativo Dash
app = dash.Dash(__name__)

# Gerar dados aleatórios
np.random.seed(0)
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.sin(x) + np.cos(x)
y4 = np.random.normal(0, 1, size=x.shape)
y5 = np.random.normal(0, 1, size=x.shape)
y6 = np.random.normal(0, 1, size=x.shape)

# Layout do aplicativo
app.layout = html.Div(style={'backgroundColor': '#282828'}, children=[
    html.Header(style={'backgroundColor': '#333333', 'padding': '10px', 'textAlign': 'center'}, children=[
        html.H1("Dashboard de Análise de Dados", style={'color': '#FFFFFF', 'fontSize': 36})
    ]),

    html.Div([
        # Seção Principal dos Gráficos
        html.Div([
            html.Div([
                dcc.Graph(
                    id='area-chart',
                    figure={
                        'data': [
                            go.Scatter(
                                x=x,
                                y=y1,
                                mode='lines',
                                fill='tozeroy',
                                fillcolor='rgba(255, 99, 71, 0.3)',
                                line=dict(color='rgb(255, 99, 71)', width=2),
                                name='Área 1'
                            ),
                            go.Scatter(
                                x=x,
                                y=y2,
                                mode='lines',
                                fill='tonexty',
                                fillcolor='rgba(54, 162, 235, 0.3)',
                                line=dict(color='rgb(54, 162, 235)', width=2),
                                name='Área 2'
                            )
                        ],
                        'layout': go.Layout(
                            title='Gráfico de Área',
                            plot_bgcolor='#1f1f1f',
                            paper_bgcolor='#282828',
                            font=dict(color='#FFFFFF'),
                            xaxis=dict(title='X', color='#FFFFFF'),
                            yaxis=dict(title='Y', color='#FFFFFF'),
                            margin=dict(l=40, r=10, t=40, b=30)
                        )
                    }
                )
            ], style={'width': '48%', 'display': 'inline-block'}),

            html.Div([
                dcc.Graph(
                    id='line-chart',
                    figure={
                        'data': [
                            go.Scatter(
                                x=x,
                                y=y3,
                                mode='lines',
                                name='Linha 1',
                                line=dict(color='rgb(255, 159, 64)', width=3),
                                marker=dict(size=8)
                            ),
                            go.Scatter(
                                x=x,
                                y=y4,
                                mode='lines',
                                name='Linha 2',
                                line=dict(color='rgb(75, 192, 192)', width=3),
                                marker=dict(size=8)
                            ),
                            go.Scatter(
                                x=x,
                                y=y5,
                                mode='lines',
                                name='Linha 3',
                                line=dict(color='rgb(153, 102, 255)', width=3),
                                marker=dict(size=8)
                            ),
                            go.Scatter(
                                x=x,
                                y=y6,
                                mode='lines',
                                name='Linha 4',
                                line=dict(color='rgb(255, 99, 132)', width=3),
                                marker=dict(size=8)
                            )
                        ],
                        'layout': go.Layout(
                            title='Gráfico de Linhas Múltiplas',
                            plot_bgcolor='#1f1f1f',
                            paper_bgcolor='#282828',
                            font=dict(color='#FFFFFF'),
                            xaxis=dict(title='X', color='#FFFFFF'),
                            yaxis=dict(title='Y', color='#FFFFFF'),
                            margin=dict(l=40, r=10, t=40, b=30),
                            legend=dict(orientation='h', xanchor='center', x=0.5, font=dict(size=12))
                        )
                    }
                )
            ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),

        html.Div([
            html.Div([
                dcc.Graph(
                    id='bubble-chart',
                    figure={
                        'data': [
                            go.Scatter(
                                x=np.random.uniform(0, 10, size=100),
                                y=np.random.uniform(0, 10, size=100),
                                mode='markers',
                                marker=dict(
                                    size=np.random.uniform(10, 50, size=100),
                                    color=np.random.uniform(0, 10, size=100),
                                    colorscale='Viridis',
                                    showscale=True
                                ),
                                text=[f'Value: {val:.2f}' for val in np.random.uniform(0, 10, size=100)]
                            )
                        ],
                        'layout': go.Layout(
                            title='Gráfico de Bolhas',
                            plot_bgcolor='#1f1f1f',
                            paper_bgcolor='#282828',
                            font=dict(color='#FFFFFF'),
                            xaxis=dict(title='X', color='#FFFFFF'),
                            yaxis=dict(title='Y', color='#FFFFFF'),
                            margin=dict(l=40, r=10, t=40, b=30)
                        )
                    }
                )
            ], style={'width': '100%'}),
        ]),
    ], style={'padding': '10px'}),

    html.Div([
        # Seção Lateral de Filtros ou Informações
        html.Div([
            html.H2("Filtros e Informações", style={'color': '#FFFFFF'}),
            html.Div([
                html.Label("Filtro 1", style={'color': '#FFFFFF'}),
                dcc.Dropdown(
                    options=[
                        {'label': 'Opção 1', 'value': '1'},
                        {'label': 'Opção 2', 'value': '2'},
                        {'label': 'Opção 3', 'value': '3'}
                    ],
                    value='1',
                    style={'color': '#000000', 'backgroundColor': '#FFFFFF'}
                )
            ], style={'marginBottom': '20px'}),

            html.Div([
                html.Label("Filtro 2", style={'color': '#FFFFFF'}),
                dcc.Slider(
                    min=0,
                    max=100,
                    value=50,
                    marks={i: str(i) for i in range(0, 101, 10)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={'marginBottom': '20px'}),

            html.P("Mais informações podem ser adicionadas aqui.", style={'color': '#FFFFFF'}),
        ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'})
    ], style={'padding': '10px'}),
])

# Rodar o aplicativo
if __name__ == '__main__':
    app.run_server(debug=True)
