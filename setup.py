import os
import configparser

def listar_arquivos(caminho, extensao=".csv"):
    #Lista arquivos de uma extensão específica no caminho.
    return [f for f in os.listdir(caminho) if f.endswith(extensao)]

def selecionar_arquivo(arquivos, padrao=None):
    #Permite ao usuário selecionar um arquivo entre os disponíveis.
    print("Arquivos disponíveis:")
    for i, arquivo in enumerate(arquivos, 1):
        print(f"{i}. {arquivo}")
    if padrao:
        print("0. Usar configuração padrão")
    
    while True:
        escolha = input("Selecione o número do arquivo desejado (ou 0 para padrão): ")
        if escolha == "0" and padrao:
            print("Usando configuração padrão.")
            return padrao
        elif escolha.isdigit() and 1 <= int(escolha) <= len(arquivos):
            return arquivos[int(escolha) - 1]
        else:
            print("Escolha inválida. Tente novamente.")

def atualizar_config(arquivo_antena, arquivo_altitude, config_path="config.ini"):
    #Atualiza o arquivo de configuração com os arquivos escolhidos.
    config = configparser.ConfigParser()
    config.read(config_path)
    config['DEFAULT']['arquivo_antenas'] = arquivo_antena
    config['DEFAULT']['arquivo_altitude'] = arquivo_altitude
    with open(config_path, 'w') as configfile:
        config.write(configfile)
    print(f"Arquivo de configuração atualizado: {arquivo_antena}, {arquivo_altitude}")

if __name__ == "__main__":
    # Carrega o arquivo de configuração
    config_path = 'config.ini'
    config = configparser.ConfigParser()
    config.read(config_path)
    
    # Obtém os caminhos das pastas e arquivos padrão
    antenas_folder = config['PATHS']['antenas_folder']
    altitudes_folder = config['PATHS']['altitudes_folder']
    padrao_antena = config['DEFAULT']['arquivo_antenas']
    padrao_altitude = config['DEFAULT']['arquivo_altitude']

    # Lista e seleciona arquivo de antenas
    arquivos_antenas = listar_arquivos(antenas_folder, ".csv")
    if not arquivos_antenas:
        print(f"Nenhum arquivo encontrado na pasta {antenas_folder}.")
        arquivo_escolhido_antena = padrao_antena
        print("Usando configuração padrão para antenas.")
    elif len(arquivos_antenas) == 1:
        arquivo_escolhido_antena = arquivos_antenas[0]
        print(f"Apenas um arquivo de antena encontrado: {arquivo_escolhido_antena}")
    else:
        arquivo_escolhido_antena = selecionar_arquivo(arquivos_antenas, padrao=os.path.basename(padrao_antena))

    # Lista e seleciona arquivo de altitudes
    arquivos_altitude = listar_arquivos(altitudes_folder, ".tif")
    if not arquivos_altitude:
        print(f"Nenhum arquivo encontrado na pasta {altitudes_folder}.")
        arquivo_escolhido_altitude = padrao_altitude
        print("Usando configuração padrão para altitudes.")
    elif len(arquivos_altitude) == 1:
        arquivo_escolhido_altitude = arquivos_altitude[0]
        print(f"Apenas um arquivo de altitude encontrado: {arquivo_escolhido_altitude}")
    else:
        arquivo_escolhido_altitude = selecionar_arquivo(arquivos_altitude, padrao=os.path.basename(padrao_altitude))
    
    # Atualiza o arquivo de configuração
    atualizar_config(
        os.path.join(antenas_folder, arquivo_escolhido_antena),
        os.path.join(altitudes_folder, arquivo_escolhido_altitude),
        config_path=config_path
    )
    
    # Direciona para o main.py
    os.system("python src/main.py")
