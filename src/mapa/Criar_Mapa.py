import folium
import geojson
from folium import CustomIcon
from collections import deque
from mapa.Calculos_Mapa import Calculos_Mapa

class Criar_Mapa():
    """
    Classe para criação e manipulação de um mapa interativo com antenas, 
    pontos móveis e polígonos, utilizando a biblioteca Folium. Permite 
    adicionar marcadores, desenhar polígonos e linhas com base em dados 
    de antenas e SINR.
    """
    def __init__(self, mapa, dados_antena, dados_sinr):
        self.df_antena = dados_antena
        self.df_sinr = dados_sinr
        self.mp = mapa
        self.azimute_cores = {}  # Dicionário para armazenar azimutes e suas cores
        self.cores_disponiveis = deque(['red', 'green', 'blue', 'orange', 'purple', 'gray'])  # Fila circular de cores

        # Caminho para o ícone
        self.icon_1 = 'dados/img/antena.png'
        self.icon_2 = 'dados/img/celular.png'


    def get_color(self, azimute):
        # Se o azimute já tiver uma cor atribuída, retorna a cor
        if azimute in self.azimute_cores:
            return self.azimute_cores[azimute]
        
        # Caso contrário, atribui a próxima cor disponível da fila
        cor = self.cores_disponiveis[0]
        # Muda para a próxima cor apenas se a cor já foi usada pelo azimute atual
        while cor in self.azimute_cores.values():
            self.cores_disponiveis.rotate(-1)  # Move a cor usada para o final da fila
            cor = self.cores_disponiveis[0]
        
        # Atribui a cor ao azimute atual e retorna
        self.azimute_cores[azimute] = cor
        return cor
    

    def add_polygon_to_map(self, dados, color):
        # Se houver dados, cria o polígono
        if dados:
            polygon_geojson = geojson.Feature(
                geometry=geojson.Polygon([
                    [(p['Longitude'], p['Latitude']) for p in dados]
                ])
            )
            
            folium.GeoJson(
                polygon_geojson,
                style={
                    'color': color,
                    'fillColor': color,
                    'fillOpacity': 0.5,
                    'weight': 2
                }
            ).add_to(self.mp)
    

    def adicionar_antenas(self):
        # Dicionário para armazenar os azimutes por estação
        azimutes_por_estacao = {}

        # Primeiro, itere sobre o DataFrame para agrupar os azimutes por estação
        for i, row in self.df_antena.iterrows():
            num_estacao = row['NumEstacao']
            
            # Se a estação já existir no dicionário, adicione o azimute à lista
            if num_estacao in azimutes_por_estacao:
                azimutes_por_estacao[num_estacao].append(f"{row['Azimute']}°")
            else:
                # Caso contrário, inicialize uma nova lista com o primeiro azimute
                azimutes_por_estacao[num_estacao] = [f"{row['Azimute']}°"]

        # Agora itere novamente para adicionar os marcadores ao mapa com os azimutes agrupados
        coordenadas_adicionadas = set()  # Para evitar duplicatas de coordenadas

        for i, row in self.df_antena.iterrows():
            coordenada_atual = (row['Latitude'], row['Longitude'])
            num_estacao = row['NumEstacao']

            # Pega todos os azimutes associados à estação atual e concatena em uma string
            saida_azimutes = ", ".join(azimutes_por_estacao[num_estacao])

            # Verificar se a coordenada já foi adicionada
            if coordenada_atual not in coordenadas_adicionadas:
                if row['FreqTxMHz'] == self.df_sinr['Frequencia'][0]:
                    popup_content = (f"""
                    <b>Nome da Estação:</b> {row['NomeEntidade']}<br>
                    <b>Latitude:</b> {row['Latitude']}<br>
                    <b>Longitude:</b> {row['Longitude']}<br>
                    <b>Designação:</b> {row['DesignacaoEmissao']}<br>
                    <b>Número da Torre:</b> {row['NumEstacao']}<br>
                    <b>Frequência:</b> {row['FreqTxMHz']} MHz<br>
                    <b>Potência do Transmissor:</b> {row['PotenciaTransmissorWatts']} W<br>
                    <b>Ganho da Antena:</b> {row['GanhoAntena']} dBi<br>
                    <b>Altura da Antena:</b> {row['AlturaAntena']} m<br>
                    <b>Azimute:</b> {saida_azimutes}<br>
                    <b>Ângulo de Elevação:</b> {row['AnguloElevacao']}°<br>
                    <b>Ângulo de Meia Potência:</b> {row['AnguloMeiaPotenciaAntena']}°
                    """)

                    # Adiciona o marcador no mapa com os azimutes da estação
                    folium.Marker(
                        location=[row['Latitude'], row['Longitude']],
                        popup=folium.Popup(popup_content, max_width=300),  # Exibe o número da estação ao clicar no ponto
                        tooltip=popup_content,
                        icon=CustomIcon(self.icon_1, (50, 50))  # Ícone personalizado
                    ).add_to(self.mp)
                    
                    # Adicionar a coordenada ao conjunto para evitar duplicatas
                    coordenadas_adicionadas.add(coordenada_atual)


    def adicionar_retas_az_antena(self):
        # Iterar sobre as linhas do DataFrame `antenas_df`
        for i, row in self.df_antena.iterrows():
            # Calculos para o mapa
            self.calc_mapa = Calculos_Mapa(self.df_sinr['Latitude'][i], self.df_sinr['Longitude'][i], self.df_sinr['Azimute_Antena'][i], self.df_sinr['Altura'][i])
            # Filtra `df` para verificar se a estação e a frequência correspondem aos valores em `antenas_df`
            filtro = (self.df_sinr['NumEstacao'] == row['NumEstacao']) & (self.df_sinr['Frequencia'] == row['FreqTxMHz'])
            if filtro.any():  # Verifica se há alguma linha correspondente
                # Calcula a reta para o azimute da antena
                reta_latitude, reta_longitude = self.calc_mapa.calcular_reta()
                
                # Desenha a linha (reta) apontando para o azimute
                folium.PolyLine(
                    locations=[(row['Latitude'], row['Longitude']), (reta_latitude, reta_longitude)],
                    color="orange",
                    weight=2.5
                ).add_to(self.mp)

    # Adiciona os celulares com informações para análise
    def adicionar_pontos_moveis(self):
        for i, ponto in self.df_sinr.iterrows():
            popup_movel = (f"""
            <b>SINR</b>: {ponto['SINR']:.2f} dB <br>
            <b>Azimute da Antena</b>: {ponto['Azimute_Antena']}° <br>
            <b>Azimute Móvel</b>: {ponto['Azimute_Movel']}° <br>
            <b>Distância</b>: {ponto['Distancia']} m
            """)
            if ponto['Distancia'] > 20:
                folium.Marker(
                    location=[ponto['Latitude'], ponto['Longitude']],
                    popup=folium.Popup(popup_movel, max_width=300),
                    tooltip=popup_movel,
                    icon=CustomIcon(self.icon_2, (20, 20))
                ).add_to(self.mp)
            else:
                folium.Marker(
                    location=[ponto['Latitude'], ponto['Longitude']],
                    popup=folium.Popup(popup_movel, max_width=300),
                    tooltip=popup_movel,
                    icon=CustomIcon(self.icon_2, (10, 10))
                ).add_to(self.mp)

    # Função responsavel por adicionar os polígonos e cores no mapa
    def processar_azimutes(self):
        dados_por_azimute = {}
        for i, ponto in self.df_sinr.iterrows():
            azimute = ponto['Azimute_Antena']
            if azimute not in dados_por_azimute:
                dados_por_azimute[azimute] = []
            dados_por_azimute[azimute].append(ponto)
        
        for azimute, dados in dados_por_azimute.items():
            cor = self.get_color(azimute)
            self.add_polygon_to_map(dados, cor)


    def processar_resultados(self):
        self.adicionar_pontos_moveis()
        self.adicionar_antenas()
        self.processar_azimutes()

