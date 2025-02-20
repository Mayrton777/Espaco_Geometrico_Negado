import rasterio

class Calcular_Altitude:
    """
    Classe para calcular a altitude de um ponto geográfico utilizando dados de um arquivo raster.

    A classe utiliza a biblioteca rasterio para manipular e acessar os dados raster armazenados
    em um arquivo, permitindo calcular a altitude com base em coordenadas geográficas.
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.src = None

    # Abre o arquivo raster
    def open_raster(self):
        if self.src is None:
            try:
                self.src = rasterio.open(self.file_path)
            except FileNotFoundError:
                raise RuntimeError("ERRO: Arquivo não encontrado")
            except Exception as e:
                raise RuntimeError(f"ERRO inesperado ao abrir o arquivo: {e}")

    # Calcula a altitude de um ponto geográfico
    def calc_altitude(self, lat, lon):
        if self.src is None:
            self.open_raster()

        try:
            # Converte as coordenadas (longitude, latitude) para o sistema de coordenadas do raster
            row, col = self.src.index(lon, lat)

            # Obtém o valor da altitude para as coordenadas
            altitude = self.src.read(1)[row, col]

            return altitude

        except IndexError:
            return "ERRO: Coordenadas fora do alcance do raster"
        except Exception as e:
            return f"ERRO inesperado: {e}"

    # Fecha o arquivo raster
    def close_raster(self):
        if self.src is not None:
            self.src.close()
            self.src = None
