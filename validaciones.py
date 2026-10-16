"""Validaciones de datos de entrada para la Mesa de Partes."""
from persistencia import SEPARADOR


def normalizar_texto(texto):
    """Quita espacios al inicio y al final y reduce los espacios dobles a uno."""
    texto = texto.strip()
    while "  " in texto:
        texto = texto.replace("  ", " ")
    return texto


def validar_datos(nombre, dni, asunto):
    """Retorna True si los datos son validos, False si no.
    Reglas:
    - nombre no vacio y sin el separador '|'
    - dni exactamente 8 digitos numericos
    - asunto no vacio y sin el separador '|'
    """
    if not nombre:
        return False
    if SEPARADOR in nombre:
        return False
    if not (dni.isdigit() and len(dni) == 8):
        return False
    if not asunto:
        return False
    if SEPARADOR in asunto:
        return False
    return True