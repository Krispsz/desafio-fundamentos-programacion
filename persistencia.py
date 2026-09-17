"""Lectura y escritura de los expedientes en un archivo de texto plano."""

from expediente import crear_expediente

RUTA_ARCHIVO = "expedientes.txt"

SEPARADOR = "|"


def cargar_desde_archivo(ruta=RUTA_ARCHIVO):
    """Lee el archivo y retorna la lista de expedientes reconstruidos."""
    expedientes = []
    try:
        archivo = open(ruta, "r", encoding="utf-8")
    except FileNotFoundError:
        return expedientes

    for linea in archivo:
        linea = linea.strip()
        if linea == "":
            continue
        campos = linea.split(SEPARADOR)
        if len(campos) != 5:
            continue
        codigo, nombre, dni, asunto, fecha = campos
        expedientes.append(crear_expediente(codigo, nombre, dni, asunto, fecha))

    archivo.close()
    return expedientes


def guardar_en_archivo(expedientes, ruta=RUTA_ARCHIVO):
    """Sobrescribe el archivo con todos los expedientes recibidos."""
    archivo = open(ruta, "w", encoding="utf-8")
    for expediente in expedientes:
        campos = [
            expediente["codigo"],
            expediente["nombre"],
            expediente["dni"],
            expediente["asunto"],
            expediente["fecha"],
        ]
        archivo.write(SEPARADOR.join(campos) + "\n")
    archivo.close()
