import requests


def obter_coordenadas(cep, chave_api):
    url = f'https://api.opencagedata.com/geocode/v1/json?q={cep}&key={chave_api}&language=pt'
    resposta = requests.get(url)
    dados = resposta.json()

    if dados['results']:
        latitude = dados['results'][0]['geometry']['lat']
        longitude = dados['results'][0]['geometry']['lng']
        return latitude, longitude
    else:
        return None, None


# Exemplo de uso
cep = '01001-000'  # CEP exemplo
chave_api = 'SUA_CHAVE_API_AQUI'  # Substitua pela sua chave da OpenCage
latitude, longitude = obter_coordenadas(cep, chave_api)

print(f"Latitude: {latitude}, Longitude: {longitude}")
