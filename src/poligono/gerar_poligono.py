import os
import simplekml
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from pyproj import Transformer

def gerar_poligono(antena, dados):
    # ID da antena
    antena_analisada = antena
    # Lista para armazenar os polígonos shapely
    poligonos = []

    # Configurar o transformador para projeção UTM (Zona 23S para Brasília, ajustável conforme a região)
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32723", always_xy=True)  # De WGS84 (graus) para UTM (metros)

    # Garantir que o campo 'Azimute_Antena' está presente
    if 'Azimute_Antena' not in dados.columns:
        raise ValueError("O campo 'Azimute_Antena' não está presente no arquivo CSV.")

    # Iterar por cada azimute único
    azimutes_unicos = dados['Azimute_Antena'].unique()

    for azimute in azimutes_unicos:
        # Filtrar os dados pelo azimute atual
        df_setor = dados[dados['Azimute_Antena'] == azimute]

        # Obter as coordenadas de latitude e longitude
        coords = df_setor[['Longitude', 'Latitude']].values

        # Verificar se há pontos suficientes para o fecho convexo
        if len(coords) < 3:
            print(f"Azimute {azimute} possui menos de 3 pontos. Fecho convexo não será criado.")
            continue

        # Calcular o fecho convexo
        hull = ConvexHull(coords)
        bordas = hull.vertices  # Índices dos pontos que formam o fecho convexo

        # Transformar as coordenadas para UTM e criar o polígono shapely
        poligono_coords = [transformer.transform(coords[i][0], coords[i][1]) for i in bordas]
        poligono = Polygon(poligono_coords)

        # Adicionar o polígono à lista
        poligonos.append(poligono)
    
    # Mesclar os polígonos usando a união geométrica
    poligono_unico = unary_union(poligonos)

    # Criar o objeto KML
    kml = simplekml.Kml()

    # Adicionar o polígono mesclado ao KML
    if isinstance(poligono_unico, Polygon):  # Caso seja um único polígono
        kml_poligono = kml.newpolygon(name="Área Total")
        # Reverter as coordenadas para WGS84 para exibir no KML
        kml_poligono.outerboundaryis = [transformer.transform(x, y, direction="INVERSE") for x, y in poligono_unico.exterior.coords]
        # Estilizar o polígono
        kml_poligono.style.polystyle.color = simplekml.Color.changealpha('cc', simplekml.Color.blue)  # Verde transparente
        kml_poligono.style.polystyle.outline = 1  # Mostrar borda
    elif isinstance(poligono_unico, MultiPolygon):  # Caso haja múltiplos polígonos
        for i, poly in enumerate(poligono_unico):
            kml_poligono = kml.newpolygon(name=f"Área Total - Parte {i+1}")
            # Reverter as coordenadas para WGS84 para exibir no KML
            kml_poligono.outerboundaryis = [transformer.transform(x, y, direction="INVERSE") for x, y in poly.exterior.coords]
            # Estilizar cada polígono
            kml_poligono.style.polystyle.color = simplekml.Color.changealpha('cc', simplekml.Color.green)  # Verde transparente
            kml_poligono.style.polystyle.outline = 1  # Mostrar borda

    # Calcular e exibir a área do polígono em metros quadrados
    area_total = poligono_unico.area

    nome_arquivo_saida_kml = f'antena_{antena_analisada}.kml'

    # Caminho para salvar o mapa
    caminho_kml = os.path.join("dados", "kml", nome_arquivo_saida_kml)

    # Salvar o arquivo KML
    kml.save(caminho_kml)

    return area_total
