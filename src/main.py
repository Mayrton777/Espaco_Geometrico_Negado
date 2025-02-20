from sinr.Calcular_SINR import Calcular_SINR
from mapa.Criar_Mapa import Criar_Mapa
from poligono.gerar_poligono import gerar_poligono
from folium import Map
import pandas as pd
import configparser
import os


def carregar_antenas(caminho_arquivo):
    # Carrega os dados do arquivo CSV.
    try:
        antenas = pd.read_csv(caminho_arquivo)
        df = pd.DataFrame(antenas)
        return df
    except FileNotFoundError:
        print(f"Erro: O arquivo {caminho_arquivo} não foi encontrado.")
        return None


if __name__ == '__main__':
    # Lê o arquivo de configuração
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Obtém os valores do arquivo de configuração
    arquivo_antenas = config['PATHS']['arquivo_antenas']
    print(arquivo_antenas)

    # Carrega os dados do arquivo CSV
    df = carregar_antenas(arquivo_antenas)

    if df is not None:
        # Obtém os valores únicos de NumEstacao
        numeros_estacoes = df['NumEstacao'].unique()
        print("Números de estação disponíveis:")
        for i, num in enumerate(numeros_estacoes, start=1):
            print(f"{i}. {num}")

        # Solicita ao usuário que escolha o índice da estação
        while True:
            try:
                indice_escolhido = int(input("Escolha o índice do número da estação a ser analisada (ou 0 para padrão): "))
                if indice_escolhido == 0:
                    antena_analisada = int(config['DEFAULT']['antena_analisada'])
                    break
                elif 1 <= indice_escolhido <= len(numeros_estacoes):
                    antena_analisada = numeros_estacoes[indice_escolhido - 1]
                    break
                else:
                    print("Índice inválido. Tente novamente.")
            except ValueError:
                print("Entrada inválida. Por favor, insira um número válido.")

        print(f"Estação selecionada: {antena_analisada}")

        # Filtra os dados para a antena escolhida
        dados_filtrados = df[df['NumEstacao'] == antena_analisada][['Azimute', 'AnguloElevacao']]

        # Pega a primeira Latitude e Longitude
        lat_mapa, lon_mapa = df.loc[df['NumEstacao'] == antena_analisada, ['Latitude', 'Longitude']].iloc[0]

        print(lat_mapa, lon_mapa)
        input()

        # Lat e Lon de referência para o mapa
        LATITUDE = float(df['Latitude'][0])
        LONGITUDE = float(df['Longitude'][0])

        # Cria uma lista de tuplas de Azimute e AnguloElevacao
        chaves = list(zip(dados_filtrados['Azimute'], dados_filtrados['AnguloElevacao']))

        # Remove duplicatas
        chaves_unicas = list(set(chaves))

        # Ordena a lista pelo Azimute do menor ao maior
        chaves_ordenadas = sorted(chaves_unicas, key=lambda x: x[0])

        df_result = []

        # Loop para calcular o SINR para cada azimute
        for az, el in chaves_ordenadas:
            distancia = 5
            az_ini = 0
            valor = True
            while valor:
                # Cria a instância da classe Calcular_SINR para cada par de azimute e elevação
                calcular_sinr = Calcular_SINR(antena_analisada, az, el, df)

                # Chama o método de cálculo de SINR
                resultado = calcular_sinr.calculo_SINR(distancia, az_ini)

                # Acesso ao valor de SINR a partir do dicionário
                sinr_value = resultado['SINR']

                # Condição para aumentar a distância caso o SINR seja maior que 0
                if sinr_value <= 0:
                    df_result.append(resultado)
                    distancia = 5
                    az_ini += 10
                    # Verifica se todos os ângulos foram calculados
                    if az_ini >= 360:
                        valor = False
                        break
                    else:
                        continue
                else:
                    distancia += 5

        df_result = pd.DataFrame(df_result)

        area_poli = gerar_poligono(antena_analisada, df_result)
        print('KML salvo com sucesso!!!')

        df_result['Area_Coberta'] = area_poli

        df_result = df_result[['Area_Coberta'] + [col for col in df_result.columns if col != 'Area_Coberta']]

        df_result['NumEstacao'] = antena_analisada

        df_result = df_result[['NumEstacao'] + [col for col in df_result.columns if col != 'NumEstacao']]

        # Cria o mapa
        mapa = Map(location=[LATITUDE, LONGITUDE], zoom_start=17, max_zoom=22)

        mapa_process = Criar_Mapa(mapa, df, df_result)
        mapa_result = mapa_process.processar_resultados()

        nome_arquivo_saida_mapa = f'mapa_SINR_{antena_analisada}.html'

        # Caminho para salvar o mapa
        mapa_nome = os.path.join("dados", "mapas", "saida", nome_arquivo_saida_mapa)

        # Salva o mapa
        mapa.save(mapa_nome)
        print('Mapa salvo com sucesso!!!')

        # Renomeando as colunas
        df_result = df_result.rename(columns={
            'NumEstacao': 'Número da Estação',
            'Area_Coberta': 'Área de Cobertura (m²)',
            'SINR': 'SINR (dB)',
            'SNR': 'SNR (dB)',
            'Sinal': 'Sinal (dBm)',
            'Interferencia': 'Interferência (dBm)',
            'Ruido': 'Ruído (dBm)',
            'Distancia': 'Distância (m)',
            'Azimute_Antena': 'Azimute da Antena (°)',
            'Azimute_Movel': 'Azimute do Móvel (°)',
            'Elevacao_Antena': 'Elevacao da Antena (°)',
            'Elevacao_Movel': 'Elevacao do Móvel (°)',
            'EIRP': 'EIRP (dBm/Hz)',
            'Free_Space': 'Perda no Espaço (dB)',
            'Frequencia': 'Frequência (MHz)',
            'Potencia': 'Potencia (W)',
            'Ganho': 'Ganho (dBi)',
            'Largura_Faixa': 'Largura da Faixa (Hz)',
            'Altura': 'Altura da Antena (m)',
            'Latitude': 'Latitude do Móvel',
            'Longitude': 'Longitude do Móvel',
            'Altitude_Antena': 'Altitude da Antena (m)',
            'Altitude_Movel': 'Altitude do Móvel (m)'
        })

        # Define o nome do arquivo de saída com base em antena_analisada e arquivo_antenas
        nome_arquivo_base = os.path.basename(arquivo_antenas)
        sufixo_nome = nome_arquivo_base.split('_')[-1]
        nome_arquivo_saida = f"{antena_analisada}_{sufixo_nome}"

        # Caminho completo para salvar o arquivo
        caminho_saida = os.path.join('dados/antenas/saida/', nome_arquivo_saida)

        # Garante que o diretório de saída existe
        os.makedirs('dados/antenas/saida/', exist_ok=True)

        # Salva o DataFrame como CSV
        df_result.to_csv(caminho_saida, index=False)

        print("Dados salvo com sucesso!!!")
