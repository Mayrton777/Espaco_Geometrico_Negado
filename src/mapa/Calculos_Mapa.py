from math import sqrt, radians, asin, sin, cos, atan2, degrees, acos

class Calculos_Mapa:
    """
    Classe para realizar cálculos relacionados a mapas, como determinação de 
    coordenadas geográficas, azimute, distância e elevação com base em dados de entrada.
    """
    def __init__(self, latitude, longitude, azimute, altura):
        self.lat = latitude
        self.lon = longitude
        self.az = azimute
        self.alt = altura

        # Constante
        self.RAIO_TERRA = 6371000
    

    def calc_hipotenusa(self, altura, distancia):
        return sqrt(altura**2 + distancia**2)
    

    def calcular_elevacao(self, distancia_horizontal, distancia_vertical):
        angulo = acos(distancia_horizontal / distancia_vertical)
        return -(degrees(angulo))
    
        
    # Função para calcular a latitude e longitude do móvel
    def calcular_lat_lon(self, azimute, distancia):
        # Converter latitude e longitude para radianos
        lat = radians(self.lat)
        lon = radians(self.lon)
        
        # Converter azimute para radianos
        azimute = radians(azimute)
        
        # Calcular a nova latitude
        lat_1 = asin(sin(lat) * cos(distancia / self.RAIO_TERRA) +
                    cos(lat) * sin(distancia / self.RAIO_TERRA) * cos(azimute))
        
        # Calcular a nova longitude
        lon_1 = lon + atan2(sin(azimute) * sin(distancia / self.RAIO_TERRA) * cos(lat_1),
                            cos(distancia / self.RAIO_TERRA) - sin(lat) * sin(lat_1))
        
        # Converter de volta para graus
        lat_graus = degrees(lat_1)
        lon_graus = degrees(lon_1)
        
        return lat_graus, lon_graus
    

    # Função para calcular a distancia da antena para móvel
    def calcular_distanca_Am(self, lat2, lon2):
    # Converter as latitudes e longitudes de graus para radianos
        lat1 = radians(self.lat)
        lon1 = radians(self.lon)
        lat2 = radians(lat2)
        lon2 = radians(lon2)
        
        # Diferenças entre as coordenadas
        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1
        
        # Aplicar a fórmula de Haversine
        a = sin(delta_lat / 2)**2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        # Distância em metros
        antena_movel = self.RAIO_TERRA * c
        
        return antena_movel
    

    # Gera o azimute correspondente ao móvel
    def calcular_azimute(self, lat, lon):
        d_lon = radians(lon - self.lon)
        lat_antena = radians(self.lat)
        lat_movel = radians(lat)

        x = sin(d_lon) * cos(lat_movel)
        y = cos(lat_antena) * sin(lat_movel) - sin(lat_antena) * cos(lat_movel) * cos(d_lon)
        azimute = atan2(x, y)

        return degrees(azimute)
    

    def calcular_diferenca_azimute(self, az):
        # Calcula as duas possibilidades de diferença
        result1 = az - self.az
        result2 = (az + 360) - self.az
        
        # Verifica qual resultado está mais próximo de zero
        if abs(result1) < abs(result2):
            return result1
        else:
            return result2

    
    # Gera uma reta na direção do azimute
    def calcular_reta(self, distancia_metros=100):
        R = 6378137  #Raio da Terra em metros
        distancia_rad = distancia_metros / R

        azimute_rad = radians(self.az)
        lat_rad = radians(self.lat)
        lon_rad = radians(self.lon)

        nova_lat = asin(sin(lat_rad) * cos(distancia_rad) +
                            cos(lat_rad) * sin(distancia_rad) * cos(azimute_rad))
        nova_lon = lon_rad + atan2(sin(azimute_rad) * sin(distancia_rad) * cos(lat_rad),
                                        cos(distancia_rad) - sin(lat_rad) * sin(nova_lat))

        return degrees(nova_lat), degrees(nova_lon)





