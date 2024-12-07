
import requests

def obter_coordenadas_google_maps(cep, api_key):
    # Construa a URL para a API do Google Maps
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={cep}&key={api_key}"
    response = requests.get(url)
    dados = response.json()

    # Exibe o retorno completo para depuração
    print(dados)  # Exibe a resposta completa da API

    if dados['status'] == 'OK':
        # Extrai a latitude e longitude do resultado
        latitude = dados['results'][0]['geometry']['location']['lat']
        longitude = dados['results'][0]['geometry']['location']['lng']
        return latitude, longitude
    else:
        print(f"Erro ao buscar coordenadas: {dados['status']}")
        return None, None

# Exemplo de CEP de Cuiabá e chave da API
cep_cuiaba = '78000-000'  # CEP de Cuiabá, Mato Grosso
api_key = 'AIzaSyBBOyKv0SR-l21rbSR03SDVggNaOkZFmfM'

latitude, longitude = obter_coordenadas_google_maps(cep_cuiaba, api_key)

if latitude and longitude:
    print(f"A latitude para o CEP {cep_cuiaba} é: {latitude}")
    print(f"A longitude para o CEP {cep_cuiaba} é: {longitude}")
else:
    print(f"Não foi possível encontrar as coordenadas para o CEP {cep_cuiaba}.")
