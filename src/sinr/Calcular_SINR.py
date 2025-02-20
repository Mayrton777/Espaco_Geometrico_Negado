from mapa.Calculos_Mapa import Calculos_Mapa
from mapa.Calcular_Altitude import Calcular_Altitude
from util.converter import mhz_to_hz, eirp_to_hz, watts_to_dBm, largura_canal_hz, dBm_to_mW, mW_to_dBm
from math import log10, pi, nan
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# Caminho para o arquivo .tif
file_path = config['PATHS']['arquivo_altitude']
altitudeCalculator = Calcular_Altitude(file_path)

class Calcular_SINR:
    def __init__(self, antena_analisada, azimute, elevacao, dados):
        self.df = dados
        self.id = antena_analisada
        self.az = azimute
        self.el = elevacao
        indice = self.df[self.df['NumEstacao'] == self.id].index

        # Se o índice não estiver vazio, obtenha os valores correspondentes
        if not indice.empty:
            self.freq = dados['FreqTxMHz'].iloc[indice[0]]
            self.ganho = dados['GanhoAntena'].iloc[indice[0]]
            self.pot = dados['PotenciaTransmissorWatts'].iloc[indice[0]]
            self.alt = dados['AlturaAntena'].iloc[indice[0]]
            self.ang_meia = dados['AnguloMeiaPotenciaAntena'].iloc[indice[0]]
            self.designacao_faixa = dados['DesignacaoEmissao'].iloc[indice[0]] # renomear
            self.lat = dados['Latitude'].iloc[indice[0]]
            self.lon = dados['Longitude'].iloc[indice[0]]
        else:
            # Lida com o caso em que não encontra um índice correspondente
            raise ValueError(f"Estação {antena_analisada} não encontrada no DataFrame")

        self.altura_movel = 1.5  # m

        # Constantes
        self.pi = pi
        self.c = 299_792_458 # m/s

        # Classe com calculos geograficos
        self.calcular_mapa_antena = Calculos_Mapa(self.lat, self.lon, self.az, self.alt)

    
    # Calculo do ganho gaussiano
    def calcular_ganho(self, ganho, az_0, el_0, az, el, ang_meia):
        '''
            Para o calculo foi normalizado os ângulos com o valor de 0° tanto
            para o azimute quanto para a elevação, fazendo um melhor uso
            do modelo gaussiano
        '''
        if az_0 == 0 and el_0 == 0:
            if az > 180:
                az -= 360
            resultado = ganho - 12 * (((el - el_0) / 7)**2 + ((az - az_0) / ang_meia)**2)
            return resultado
        else:
            if az_0 == 0:
                el -= el_0
                el_0 = 0
                if az > 180:
                    az -= 360
                resultado = ganho - 12 * (((el - el_0) / 7)**2 + ((az - az_0) / ang_meia)**2)
                return resultado
            elif el_0 == 0:
                az -= az_0
                az_0 = 0
                if az > 180:
                    az -= 360
                elif az < -180:
                    az += 360
                resultado = ganho - 12 * (((el - el_0) / 7)**2 + ((az - az_0) / ang_meia)**2)
                return resultado
            else:
                az -= az_0
                el -= el_0
                az_0 = 0
                el_0 = 0
                if az > 180:
                    az -= 360
                elif az < -180:
                    az += 360
                resultado = ganho - 12 * (((el - el_0) / 7)**2 + ((az - az_0) / ang_meia)**2)
                return resultado
    

    # Calcula a potência isotrópica radiada equivalente
    def calcular_eirp(self, ganho, pot):
        return eirp_to_hz(watts_to_dBm(pot) + ganho)
    

    # Calcula a perda no espaço livre
    def calcular_perda_no_espaco(self, distancia):
        return 20 * log10((4 * self.pi * mhz_to_hz(self.freq) * distancia)/ self.c)


    # Calcula o ruido da antena
    def calcular_ruido(self):
        return -174 + 10 * log10(largura_canal_hz(self.designacao_faixa)) + 7
    

    # Calcula a interferencia sofrida no determinado ponto
    def calculo_interferencia(self, lat_movel, lon_movel, alt_movel):
        contador_i = 0
        s_i = 0
        for i, row in self.df.iterrows():
            # estaçao ou azimute diferente
            if ((row['Azimute'] != self.az) or ((row['Azimute'] == self.az) and (row['NumEstacao'] != self.id)) and ((row['FreqTxMHz'] == self.freq) and (row['DesignacaoEmissao'] == self.designacao_faixa))):
                latitude_i = row['Latitude']
                longitude_i = row['Longitude']
                potencia_i = row['PotenciaTransmissorWatts']
                ganho_i = row['GanhoAntena']
                altura_i = row['AlturaAntena']
                azimute_i = row['Azimute']
                elevacao_i = row['AnguloElevacao']
                #meia_pot_i = row['AnguloMeiaPotenciaAntena']
                meia_pot_i = 65 # evitando um erro da base de dados

                mapa_antena_i = Calculos_Mapa(latitude_i, longitude_i, azimute_i, altura_i)
                # Calcula a distancia do móvel para a antena
                distancia_para_movel = mapa_antena_i.calcular_distanca_Am(lat_movel, lon_movel)
                
                if distancia_para_movel <= 1000:#and (azimute_direcao_movel > -180 and azimute_direcao_movel < 180)
                    # Calcula a altitude da antena
                    altitude_antena_i = altitudeCalculator.calc_altitude(latitude_i, longitude_i)
                    #altitude_movel = altitudeCalculator.calc_altitude(lat_movel, lon_movel)
                    # Calcula a distancia do móvel até o ponto mais alto da antena
                    distancia_diagonal_movel = mapa_antena_i.calc_hipotenusa((altura_i + altitude_antena_i) - (self.altura_movel + alt_movel), distancia_para_movel)
                    # Calcula o azimute do móvel em relação a antena interferente
                    azimute_direcao_movel = mapa_antena_i.calcular_diferenca_azimute(mapa_antena_i.calcular_azimute(lat_movel, lon_movel))
                    # Calcula a elevação do móvel em relação a antena interferente
                    elevacao_movel_i = mapa_antena_i.calcular_elevacao(distancia_para_movel, distancia_diagonal_movel)
                    # Calcula o ganho gaussiano dBm
                    ganho_gaussiano = self.calcular_ganho(ganho_i, azimute_i, elevacao_i, azimute_direcao_movel, elevacao_movel_i, meia_pot_i)
                    # Calcula o EIRP dBm/Hz
                    eirp_antena = self.calcular_eirp(ganho_gaussiano, potencia_i)
                    # Calcula a perda do espaço livre dB
                    espaco_livre = self.calcular_perda_no_espaco(distancia_diagonal_movel)
                    # Calcula o Sinal dBm
                    sinal = eirp_antena - espaco_livre
                    s_i += dBm_to_mW(sinal)
                    print(f'Torre interferente {contador_i + 1}')
                    contador_i += 1
                else:
                    continue
        # Verificando se realmente existe torres interferentes
        if s_i == 0:
            return 0
        else:
            return mW_to_dBm(s_i)
    

    def calculo_SINR(self, distancia, azimute):
        # Calcula a altitude da antena
        altitude_antena = altitudeCalculator.calc_altitude(self.lat, self.lon)
        # Calcula a lat e lon móvel
        lat_movel, lon_movel = self.calcular_mapa_antena.calcular_lat_lon(azimute, distancia)
        # Calcula a altitude do móvel
        altitude_movel = altitudeCalculator.calc_altitude(lat_movel, lon_movel)
        # Calcula a distancia do móvel até o ponto mais alto da antena
        distancia_diagonal = self.calcular_mapa_antena.calc_hipotenusa((self.alt + altitude_antena) - (self.altura_movel + altitude_movel), distancia)
        # Calcula a elevação do móvel em relação a antena
        elevacao_movel = self.calcular_mapa_antena.calcular_elevacao(distancia, distancia_diagonal)
        
        # Corrigindo margem de erro do modelo gaussiano
        if self.el == 0:
            if elevacao_movel < -8 or distancia < self.alt:
                elevacao_movel_calc = self.el
            else:
                elevacao_movel_calc = elevacao_movel
        else:
            if self.el > 0:
                elevacao_movel_dif = elevacao_movel - self.el
            else:
                elevacao_movel_dif = elevacao_movel + self.el
            
            if elevacao_movel_dif < -8 or distancia < self.alt:
                elevacao_movel_calc = self.el
            else:
                elevacao_movel_calc = elevacao_movel

        # Calcula o ganho gaussiano dBm
        ganho_gaussiano = self.calcular_ganho(self.ganho, self.az, self.el, azimute, elevacao_movel_calc, self.ang_meia)
        # Calcula o EIRP dBm/Hz
        eirp_antena = self.calcular_eirp(ganho_gaussiano, self.pot)
        # Calcula a perda do espaço livre dB
        espaco_livre = self.calcular_perda_no_espaco(distancia)
        # Calcula o Ruido dBm
        ruido = self.calcular_ruido()
        # Calcula o Sinal dBm
        sinal = eirp_antena - espaco_livre
        # Calcula o SNR dB
        snr = sinal - ruido
        # Calcula a interferencia dBm
        inter = self.calculo_interferencia(lat_movel, lon_movel, altitude_movel)
        # Calcula o SINR dB
        if inter == 0: # Casos em que a Antena esta em um ponto isolado sem interferencias de outras antenas
            inter = nan # Retorna Nan para esses casos já que realmente não a interferencia
            sinr = sinal - ruido
        else:
            sinr = sinal - 10 * log10(dBm_to_mW(inter) + dBm_to_mW(ruido))

        # Depuração do código
        print(f'SINR: {sinr:.2f} dB, SNR: {snr:.2f} dB, Sinal: {sinal:.2f} dBm, Interferencia: {inter:.2f} dBm, Ruido: {ruido:.2f} dBm, distancia: {distancia:.2f} m, Azimute Antena: {self.az}°, Azimute Móvel: {azimute}°, Elevação Antena: {self.el}°, Elevação Móvel: {elevacao_movel:.2f}°, altura: {self.alt} m, ganho: {ganho_gaussiano:.2f} dBm')

        # dados que serão retornados
        resultado = {
            'SINR': sinr,
            'SNR': snr,
            'Sinal': sinal,
            'Interferencia': inter,
            'Ruido': ruido,
            'Distancia': distancia,
            'Azimute_Antena': self.az,
            'Azimute_Movel': azimute,
            'Elevacao_Antena': self.el,
            'Elevacao_Movel': elevacao_movel,
            'EIRP': eirp_antena,
            'Free_Space': espaco_livre,
            'Frequencia': self.freq,
            'Potencia': self.pot,
            'Ganho': ganho_gaussiano,
            'Largura_Faixa': largura_canal_hz(self.designacao_faixa),
            'Altura': self.alt,
            'Latitude': lat_movel,
            'Longitude': lon_movel,
            'Altitude_Antena': altitude_antena,
            'Altitude_Movel': altitude_movel
        }

        return resultado
