from shapely import wkb

# Dados WKB como strings hexadecimais
wkb1 = bytes.fromhex('010100002042120000780CDFB261E94BC06001BA35DDEE23C0')
wkb2 = bytes.fromhex('0101000000780CDFB261E94BC06001BA35DDEE23C0')

# Converter de WKB para geometria
geom1 = wkb.loads(wkb1)
geom2 = wkb.loads(wkb2)

# Obter latitude e longitude
lon1, lat1 = geom1.x, geom1.y
lon2, lat2 = geom2.x, geom2.y

print(f'Coordenadas 1: Longitude: {lon1}, Latitude: {lat1}')
print(f'Coordenadas 2: Longitude: {lon2}, Latitude: {lat2}')
