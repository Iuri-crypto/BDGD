from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
from gera_dados_csv_web import gerar_dados_ficticios  # Supondo que você tenha esta função

# Gerando os dados fictícios
dados_ficticios = gerar_dados_ficticios()

app = Dash(__name__, suppress_callback_exceptions=True)  # Permite múltiplas páginas

# Layout principal com links de navegação
app.layout = html.Div(
    style={
        "backgroundColor": "#FFFFFF",  # Fundo branco estiloso para a página
        "color": "#333333",  # Texto em tom escuro para bom contraste
        "fontFamily": "Arial, sans-serif",
        "minHeight": "100vh",
        "padding": "20px",
        "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",  # Sombra suave para dar destaque
    },
    children=[
        dcc.Location(id="url", refresh=False),  # Controla a URL
        html.Div(
            [
                # Links de navegação para as páginas
                dcc.Link(
                    "Página 1",
                    href="/page-1",
                    style={"padding": "10px", "fontSize": "20px", "color": "#00bcd4", "textDecoration": "none", "fontWeight": "bold"}
                ),
                html.Span(" | ", style={"fontSize": "20px", "color": "#777"}),
                dcc.Link(
                    "Página 2",
                    href="/page-2",
                    style={"padding": "10px", "fontSize": "20px", "color": "#00bcd4", "textDecoration": "none", "fontWeight": "bold"}
                ),
            ],
            style={
                "marginBottom": "20px",
                "fontSize": "25px",
                "fontWeight": "bold",
                "textAlign": "center",
            },
        ),
        html.Div(id="page-content"),  # Aqui o conteúdo da página será renderizado
    ]
)

# Layout e gráfico da Página 1 (gráfico de barras)
page_1_layout = html.Div(
    [
        html.H4("Gráfico de Barras - Página 1", style={"textAlign": "center", "color": "#00bcd4"}),
        dcc.Graph(
            id="graph-1",
            style={
                "width": "100%",
                "height": "90vh",
                "borderRadius": "50px",  # Bordas arredondadas para o gráfico
                "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",  # Sombra suave para o gráfico
            },
            config={"displayModeBar": True, "modeBarButtonsToRemove": ["zoom2d", "pan2d", "select2d"]},
        ),
    ],
    style={
        "backgroundColor": "#FFFFFF",  # Fundo branco para a área do gráfico
        "padding": "20px",
        "borderRadius": "50px",  # Bordas arredondadas no contêiner do gráfico
        "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",  # Sombra suave para destacar o conteúdo
    },
)

# Layout e gráfico da Página 2 (gráfico de barras)
page_2_layout = html.Div(
    [
        html.H4("Gráfico de Barras - Página 2", style={"textAlign": "center", "color": "#00bcd4"}),
        dcc.Graph(
            id="graph-2",
            style={
                "width": "100%",
                "height": "90vh",
                "borderRadius": "50px",  # Bordas arredondadas para o gráfico
                "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",  # Sombra suave para o gráfico
            },
            config={"displayModeBar": True, "modeBarButtonsToRemove": ["zoom2d", "pan2d", "select2d"]},
        ),
    ],
    style={
        "backgroundColor": "#FFFFFF",  # Fundo branco para a área do gráfico
        "padding": "20px",
        "borderRadius": "50px",  # Bordas arredondadas no contêiner do gráfico
        "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",  # Sombra suave para destacar o conteúdo
    },
)

# Callback para renderizar o conteúdo da página com base na URL
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):
    if pathname == "/page-1":
        return page_1_layout
    elif pathname == "/page-2":
        return page_2_layout
    else:
        return "Página não encontrada!"  # Caso a URL não corresponda a nenhuma página


# Função para preparar os dados de medidores
def preparar_dados_medidores(dados_ficticios, dia):
    medidores = list(dados_ficticios.keys())  # Todos os medidores
    kwh_values = []
    kvar_values = []
    losses_kwh_values = []
    losses_kvar_values = []
    for medidor in medidores:
        # Extrair os dados de cada medidor para o dia específico (DO, DU, SA)
        kwh = dados_ficticios[medidor][dia]["zone_kwh"]
        kvar = dados_ficticios[medidor][dia]["zone_kvar"]
        losses_kwh = dados_ficticios[medidor][dia]["zone_losses_kwh"]
        losses_kvar = dados_ficticios[medidor][dia]["zone_losses_kvar"]

        kwh_values.append(kwh)
        kvar_values.append(kvar)
        losses_kwh_values.append(losses_kwh)
        losses_kvar_values.append(losses_kvar)

    return medidores, kwh_values, kvar_values, losses_kwh_values, losses_kvar_values


# Callbacks para atualizar os gráficos em cada página
@app.callback(
    Output("graph-1", "figure"),
    Input("url", "pathname"),
)
def display_bars_page_1(pathname):
    # Preparando os dados para o gráfico da Página 1 (usando dados do dia "DO")
    medidores, kwh_values, kvar_values, losses_kwh_values, losses_kvar_values = preparar_dados_medidores(
        dados_ficticios, "DO")

    # Criando o gráfico de barras para cada medidor
    fig = go.Figure()

    # Usando cores vivas e energéticas para as barras
    fig.add_trace(go.Bar(
        x=medidores,
        y=kwh_values,
        name="Zone KWH",
        marker_color='#FF5733',  # Vermelho intenso
        hovertemplate="%{y} kWh",
        marker_line_width=3,  # Aumenta a espessura do contorno das barras
        marker_line_color='rgba(0,0,0,0.1)',  # Cor do contorno (suave)
    ))
    fig.add_trace(go.Bar(
        x=medidores,
        y=kvar_values,
        name="Zone KVAR",
        marker_color='#FFB933',  # Amarelo dourado
        hovertemplate="%{y} kVar",
        marker_line_width=3,  # Aumenta a espessura do contorno das barras
        marker_line_color='rgba(0,0,0,0.1)',  # Cor do contorno (suave)
    ))
    fig.add_trace(go.Bar(
        x=medidores,
        y=losses_kwh_values,
        name="Losses KWH",
        marker_color='#C70039',  # Vermelho escuro vibrante
        hovertemplate="%{y} kWh",
        marker_line_width=3,  # Aumenta a espessura do contorno das barras
        marker_line_color='rgba(0,0,0,0.1)',  # Cor do contorno (suave)
    ))
    fig.add_trace(go.Bar(
        x=medidores,
        y=losses_kvar_values,
        name="Losses KVAR",
        marker_color='#900C3F',  # Roxo profundo
        hovertemplate="%{y} kVar",
        marker_line_width=3,  # Aumenta a espessura do contorno das barras
        marker_line_color='rgba(0,0,0,0.1)',  # Cor do contorno (suave)
    ))

    # Layout do gráfico
    fig.update_layout(
        title="Gráfico de Barras para os Medidores - Página 1",
        barmode='group',  # Agrupar as barras
        xaxis_title="Medidores",
        yaxis_title="Valor (kWh, kVar, etc.)",
        xaxis_tickangle=-45,
        height=600,
        plot_bgcolor='#FFFFFF',  # Fundo branco para o gráfico
        paper_bgcolor='#FFFFFF',  # Fundo branco
        font=dict(color="#333333"),  # Cor da fonte escura para contraste
        title_font=dict(color="#00bcd4"),  # Cor do título
        showlegend=True,
        hovermode="closest",  # Exibir valor ao passar o mouse
    )

    return fig


@app.callback(
    Output("graph-2", "figure"),
    Input("url", "pathname"),
)
def display_bars_page_2(pathname):
    # Preparando os dados para o gráfico da Página 2 (usando dados do dia "DU")
    medidores, kwh_values, kvar_values, losses_kwh_values, losses_kvar_values = preparar_dados_medidores(
        dados_ficticios, "DU")

    # Criando o gráfico de barras para cada medidor
    fig = go.Figure()

    # Usando cores vivas e energéticas para as barras
    fig.add_trace(go.Bar(
        x=medidores,
        y=kwh_values,
        name="Zone KWH",
        marker_color='#2E3B4E',  # Vermelho intenso
        hovertemplate="%{y} kWh",
        marker_line_width=3,  # Aumenta a espessura do contorno das barras
        marker_line_color='rgba(0,0,0,0.1)',  # Cor do contorno (suave)
    ))
    fig.add_trace(go.Bar(
        x=medidores,
        y=kvar_values,
        name="Zone KVAR",
        marker_color='#4FC3F7',  # Amarelo dourado
        hovertemplate="%{y} kVar",
        marker_line_width=3,  # Aumenta a espessura do contorno das barras
        marker_line_color='rgba(0,0,0,0.1)',  # Cor do contorno (suave)
    ))
    fig.add_trace(go.Bar(
        x=medidores,
        y=losses_kwh_values,
        name="Losses KWH",
        marker_color='#00BFAE',  # Vermelho escuro vibrante
        hovertemplate="%{y} kWh",
        marker_line_width=3,  # Aumenta a espessura do contorno das barras
        marker_line_color='rgba(0,0,0,0.1)',  # Cor do contorno (suave)
    ))
    fig.add_trace(go.Bar(
        x=medidores,
        y=losses_kvar_values,
        name="Losses KVAR",
        marker_color='#FF7043',  # Roxo profundo
        hovertemplate="%{y} kVar",
        marker_line_width=3,  # Aumenta a espessura do contorno das barras
        marker_line_color='rgba(0,0,0,0.1)',  # Cor do contorno (suave)
    ))

    # Layout do gráfico
    fig.update_layout(
        title="Gráfico de Barras para os Medidores - Página 2",
        barmode='group',  # Agrupar as barras
        xaxis_title="Medidores",
        yaxis_title="Valor (kWh, kVar, etc.)",
        xaxis_tickangle=-45,
        height=600,
        plot_bgcolor='#FFFFFF',  # Fundo branco para o gráfico
        paper_bgcolor='#FFFFFF',  # Fundo branco
        font=dict(color="#333333"),  # Cor da fonte escura para contraste
        title_font=dict(color="#00bcd4"),  # Cor do título
        showlegend=True,
        hovermode="closest",  # Exibir valor ao passar o mouse
    )

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
