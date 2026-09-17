"""Estructura del expediente y generacion de codigos correlativos."""


def crear_expediente(codigo, nombre, dni, asunto, fecha):
    """Construye y retorna un expediente como diccionario."""
    return {
        "codigo": codigo,
        "nombre": nombre,
        "dni": dni,
        "asunto": asunto,
        "fecha": fecha,
    }


def generar_codigo(expedientes):
    """Genera el siguiente codigo correlativo con formato EXP-0001."""
    numero = len(expedientes) + 1
    return "EXP-" + str(numero).zfill(4)
