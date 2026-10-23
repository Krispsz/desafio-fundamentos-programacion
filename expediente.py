"""Estructura del expediente y generacion de codigos correlativos."""

ESTADOS = ["Recibido", "En proceso", "Atendido"]

DEPENDENCIAS = ["Mesa de Partes", "Licencias", "Rentas", "Obras", "Secretaria General"]

SEPARADOR_HISTORIAL = ";"

SEPARADOR_ENTRADA = ","


def crear_expediente(codigo, nombre, dni, asunto, fecha,
                     estado="Recibido", dependencia="Mesa de Partes", historial=None):
    """Construye y retorna un expediente como diccionario.

    El historial es una lista de diccionarios {"fecha", "estado", "usuario"}.
    Si no se envia, empieza con una sola entrada: Recibido por "sistema".
    """
    if historial is None:
        historial = [{"fecha": fecha, "estado": "Recibido", "usuario": "sistema"}]
    return {
        "codigo": codigo,
        "nombre": nombre,
        "dni": dni,
        "asunto": asunto,
        "fecha": fecha,
        "estado": estado,
        "dependencia": dependencia,
        "historial": historial,
    }


def historial_a_texto(historial):
    """Convierte el historial en texto para el archivo.

    Ejemplo: 2026-10-22,Recibido,admin;2026-10-23,En proceso,jmesa
    """
    entradas = []
    for entrada in historial:
        entradas.append(entrada["fecha"] + SEPARADOR_ENTRADA + entrada["estado"]
                        + SEPARADOR_ENTRADA + entrada["usuario"])
    return SEPARADOR_HISTORIAL.join(entradas)


def texto_a_historial(texto):
    """Convierte el texto del archivo en la lista de entradas del historial.

    Las entradas que no tienen exactamente 3 partes se ignoran.
    """
    historial = []
    for parte in texto.split(SEPARADOR_HISTORIAL):
        campos = parte.split(SEPARADOR_ENTRADA)
        if len(campos) == 3:
            historial.append({"fecha": campos[0], "estado": campos[1], "usuario": campos[2]})
    return historial


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
