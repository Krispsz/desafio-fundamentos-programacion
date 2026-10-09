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
    """Genera el siguiente codigo correlativo con formato EXP-0001.

    Usa el numero mas alto existente + 1 (no la cantidad de expedientes),
    para no repetir codigos despues de eliminar uno.
    """
    mayor = 0
    for expediente in expedientes:
        numero = int(expediente["codigo"][4:])
        if numero > mayor:
            mayor = numero
    return "EXP-" + str(mayor + 1).zfill(4)
