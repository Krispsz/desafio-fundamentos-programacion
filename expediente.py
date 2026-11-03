"""Estructura del expediente, historial y generacion de codigos correlativos."""

from datetime import date

ESTADOS = ["Recibido", "En proceso", "Atendido"]

DEPENDENCIAS = ["Mesa de Partes", "Licencias", "Rentas", "Obras", "Secretaria General"]

SEPARADOR_HISTORIAL = ";"

SEPARADOR_ENTRADA = ","


def fecha_valida(texto):
    """Retorna True si el texto es una fecha real con formato AAAA-MM-DD."""
    if len(texto) != 10 or texto[4] != "-" or texto[7] != "-":
        return False
    anio, mes, dia = texto[:4], texto[5:7], texto[8:]
    if not (anio.isdigit() and mes.isdigit() and dia.isdigit()):
        return False
    try:
        date(int(anio), int(mes), int(dia))
    except ValueError:
        return False
    return True


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


def agregar_entrada(historial, fecha, estado, usuario):
    """Agrega una entrada al historial conservando todas las anteriores.

    La entrada se inserta en orden cronologico (por fecha). Si la fecha es la
    misma que la de la ultima entrada, queda despues para conservar el orden en
    que ocurrieron los cambios. Retorna True si se agrego y False si algun dato
    no es valido o el historial no es una lista.
    """
    if not isinstance(historial, list):
        return False
    if not fecha_valida(fecha) or estado not in ESTADOS:
        return False
    if not isinstance(usuario, str) or usuario.strip() == "":
        return False
    entrada = {"fecha": fecha, "estado": estado, "usuario": usuario}
    posicion = len(historial)
    for i in range(len(historial)):
        if historial[i].get("fecha", "") > fecha:
            posicion = i
            break
    historial.insert(posicion, entrada)
    return True


def generar_codigo(expedientes):
    """Genera el siguiente codigo correlativo con formato EXP-0001.

    Usa el numero mas alto existente + 1 (no la cantidad de expedientes),
    para no repetir codigos despues de eliminar uno. Los codigos fuera de
    formato (por ejemplo 123-ABC, que la integridad conserva) se ignoran.
    """
    mayor = 0
    for expediente in expedientes:
        codigo = expediente["codigo"]
        if not (codigo.startswith("EXP-") and codigo[4:].isdigit()):
            continue
        numero = int(codigo[4:])
        if numero > mayor:
            mayor = numero
    return "EXP-" + str(mayor + 1).zfill(4)
