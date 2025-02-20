# ESPAÇO GEOMÉTRICO NEGADO

## Resumo do Projeto
O projeto **Sinal Interferência Ruído - SINR** tem como objetivo calcular o sinal que chega a um ponto específico, considerando a interferência e o ruído provenientes de diferentes antenas de telecomunicação, e com isso determinar onde seria a borda da celula da antena transmissora, e, com isso, determinar a borda da célula da antena transmissora. Utilizando dados de antenas e de altitude do terreno, o código desenvolvido em Python calcula esses parâmetros e gera dois outputs principais:
1. **Arquivo CSV**, contem os dados como:
    * SINR (dB)
    * SNR (dB)
    * Sinal (dBm)
    * Ruído (dBm)
    * Interferência (dBm)
    * Coordenadas de latitude e longitude para formar os pontos do polígono  

O objetivo deste arquivo é fornecer uma visão clara do sinal que chega a cada ponto. É importante lembrar que os dados de Azimute do Móvel e Azimute da Antena são medidos em relação ao norte verdadeiro da Terra. A Elevação do Móvel é considerada em relação à elevação da antena; caso o móvel esteja abaixo da antena, teremos -90°, caso esteja acima, 90°, e, se estiver alinhado horizontalmente com o ponto de transmissão da antena, 0°. Para as considerações de elevação, também é levada em conta a altitude do terreno.  

2. **Mapa HTML**: Exibe a antena com sua respectiva célula de cobertura.
* O objetivo deste arquivo é oferecer uma visualização do polígono gerado, com uma divisão clara de cada setor da antena.
* O código utiliza bibliotecas como `pandas`, `folium` e outras para processar os dados e gerar os resultados de forma visual e interativa.

3. **Arquivo KML**: Exibe um polígono contendo a área de cobertura da antena.
* O objetivo deste arquivo é oferecer uma visualização do polígono gerado, que pode ser aplicado em qualquer mapa, como no Google Earth.

## Como Executar
### 1. Instalar as Dependências
Para rodar o projeto, primeiro, é necessário instalar as bibliotecas necessárias. Para isso, siga os seguintes passos:
1. Clone o repositório para sua máquina local.
2. Crie e ative um ambiente virtual (opcional, mas recomendado):
    ```bash
    python -m venv env
    source env/bin/activate  # Para Linux/macOS
    .\env\Scripts\activate   # Para Windows
    ```
3. Instale as dependências com o comando:
    ```bash
    pip install -r requirements.txt
    ```
4. Após instalar as dependências, copie o arquivo `config.template.ini` e renomeie para `config.ini`, mantendo os caminhos fornecidos.

5. Execute o código com o comando:
    ```bash
    python setup.py
    ```
### 2. Instruções
- Ao executar o setup, o sistema solicitará os arquivos de dados. Se você for um usuário iniciante, escolha a opção `0` para utilizar os arquivos padrão.
- Para testar diferentes configurações, é necessário selecionar os arquivos corretos de acordo com o estado desejado.
**NOTA**:Caso seja a primeira vez utilizando o projeto, recomendo utilizar os arquivos padrões. Para isso, selecione a opção `0` no menu de configuração. Caso deseje testar outras configurações, lembre-se de sempre escolher os documentos do mesmo estado.
### 3. Arquivos de configuração
- Neste projeto, foram utilizados dois tipos de arquivos. Um deles contém dados das antenas fornecidos pelo Mosaico. Como referência, temos os arquivos `antenas_DF.csv` e `antenas_SE.csv`, que incluem diversas informações sobre as antenas necessárias para o cálculo do SINR.
- Outro arquivo contém informações geográficas de altitudes do terreno, como os exemplos `DF_Heights.tif` e `SE_Heights.tif`.
- Caso deseje testar outros dados, será necessário fornecer informações das antenas de uma determinada região e as altitudes do terreno da mesma região.
- **Observação**: Em caso de dúvidas, consulte o guia de uso localizado na pasta `docs`.
## Desenvolvedor
- **Mayrton Eduardo**