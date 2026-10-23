"""Lectura y escritura de los expedientes en un archivo de texto plano."""

from expediente import crear_expediente, historial_a_texto, texto_a_historial

RUTA_ARCHIVO = "expedientes.txt"

SEPARADOR = "|"


def cargar_desde_archivo(ruta=RUTA_ARCHIVO):
    """Lee el archivo y retorna la lista de expedientes reconstruidos.

    Acepta dos formatos de linea:
    - 8 campos: codigo|nombre|dni|asunto|fecha|estado|dependencia|historial
    - 5 campos (formato anterior): codigo|nombre|dni|asunto|fecha; estado,
      dependencia e historial toman sus valores por defecto.
    Si el archivo no existe o no se puede leer, retorna una lista vacia.
    Las lineas vacias o mal formadas se saltan sin detener el programa, y un
    caracter ilegible se reemplaza (errors="replace") para no perder el resto.
    """
    expedientes = []
    try:
        with open(ruta, "r", encoding="utf-8", errors="replace") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if linea == "":
                    continue
                campos = linea.split(SEPARADOR)
                if len(campos) == 8:
                    codigo, nombre, dni, asunto, fecha, estado, dependencia, historial = campos
                    expedientes.append(crear_expediente(codigo, nombre, dni, asunto, fecha,
                                                        estado, dependencia,
                                                        texto_a_historial(historial)))
                elif len(campos) == 5:
                    codigo, nombre, dni, asunto, fecha = campos
                    expedientes.append(crear_expediente(codigo, nombre, dni, asunto, fecha))
    except OSError:
        return []
    return expedientes


def guardar_en_archivo(expedientes, ruta=RUTA_ARCHIVO):
    """Sobrescribe el archivo con todos los expedientes (8 campos por linea).

    Retorna True si se guardo y False si hubo un error de escritura.
    """
    try:
        with open(ruta, "w", encoding="utf-8") as archivo:
            for expediente in expedientes:
                campos = [
                    expediente["codigo"],
                    expediente["nombre"],
                    expediente["dni"],
                    expediente["asunto"],
                    expediente["fecha"],
                    expediente["estado"],
                    expediente["dependencia"],
                    historial_a_texto(expediente["historial"]),
                ]
                archivo.write(SEPARADOR.join(campos) + "\n")
    except OSError:
        return False
    return True
