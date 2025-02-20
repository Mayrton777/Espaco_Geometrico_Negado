from math import log10
import re

# Converte MHz para Hz
def khz_to_hz(freq):
    return freq * 1e3


# Converte MHz para Hz
def mhz_to_hz(freq):
    return freq * 1e6


# Converte MHz para Hz
def ghz_to_hz(freq):
    return freq * 1e9


# Converte dB para W (Watts)
def dB_to_watts(dB):
    return 10 ** ((dB - 30) / 10)


# Converte dBm para W (Watts)
def dBm_to_watts(dBm):
    return 10**(dBm / 10) * 10**-3


# Converte dBm para mW (Miliwatt)
def dBm_to_mW(dBm):
    return 10**(dBm/10)


# Converte Watts para dBm
def watts_to_dBm(w):
    return 10 * log10(w) + 30


# Converter mW para dBm
def mW_to_dBm(mW):
    return 10 * log10(mW)


# Converter mW para W
def mW_to_watts(mW):
    return mW / 1000


# Converter W para mW
def watts_to_mW(w):
    return w * 1000


# Transformando EIRP dBm em EIRP dBm/Hz
def eirp_to_hz(eirp):
    return eirp + 10 * log10(1 / 100000000)


def largura_canal_hz(entrada):
    """
    Converte uma string com sufixo 'k', 'm' ou 'g' para um número float.

    Args:
        entrada: String de entrada.

    Returns:
        float: Valor convertido, ou a entrada original se não for possível converter.
    """

    # Converter para minúsculas e extrair os quatro primeiros caracteres
    entrada_min = entrada[:4].lower()

    # Expressão regular para encontrar 'k', 'm' ou 'g' nos quatro primeiros caracteres
    padrao = r"[kmg]"
    match = re.search(padrao, entrada_min)

    if match:
        # Substituir a letra por ponto e converter para float
        indice_letra = match.start()
        novo_valor = float(entrada_min.replace(entrada_min[indice_letra], "."))
        if entrada_min[indice_letra] == 'k':
            return khz_to_hz(novo_valor)
        elif entrada_min[indice_letra] == 'm':
            return mhz_to_hz(novo_valor)
        else:
            return ghz_to_hz(novo_valor)
    else:
        # Se não encontrar 'k', 'm' ou 'g', retornar a entrada original
        return entrada
