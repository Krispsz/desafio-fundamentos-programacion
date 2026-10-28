"""Lectura y escritura de los expedientes en el almacenamiento configurado.

Es el unico punto de entrada para guardar y cargar: el resto del programa
llama a cargar_desde_archivo() y guardar_en_archivo(), y este modulo decide
si los datos van al archivo de texto o a la base de datos SQLite.
"""

import os

import integridad
import persistencia_db
from expediente import crear_expediente, historial_a_texto, texto_a_historial

# Donde se guardan los expedientes:
# - "txt":    archivo de texto plano expedientes.txt
# - "sqlite": base de datos mesa_partes.db (ver persistencia_db.py)
# Para cambiarlo, edite este valor y vuelva a ejecutar el programa.
ALMACENAMIENTO = "txt"

RUTA_ARCHIVO = "expedientes.txt"

SEPARADOR = "|"


def cargar_desde_txt(ruta=RUTA_ARCHIVO):
    """Lee el archivo de texto y retorna la lista de expedientes integros.

    Acepta dos formatos de linea:
    - 8 campos: codigo|nombre|dni|asunto|fecha|estado|dependencia|historial
    - 5 campos (formato anterior): codigo|nombre|dni|asunto|fecha; estado,
      dependencia e historial toman sus valores por defecto.
    Si el archivo no existe o no se puede leer, retorna una lista vacia.
    Las lineas vacias o mal formadas se saltan sin detener el programa, y un
    caracter ilegible se reemplaza (errors="replace") para no perder el resto.
    Cada expediente pasa ademas por la revision de integridad.
    """
    expedientes, rechazos = cargar_txt_con_informe(ruta)
    return expedientes


def cargar_txt_con_informe(ruta=RUTA_ARCHIVO):
    """Lee el archivo y retorna (expedientes integros, rechazos).

    Cada rechazo es {"codigo", "motivo"}: lineas con otro numero de campos o
    expedientes que no pasan la revision de integridad.py (dni, fecha, estado,
    dependencia, campos vacios o codigo repetido).
    """
    expedientes = []
    rechazos = []
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
                else:
                    rechazos.append({"codigo": campos[0],
                                     "motivo": "campos incompletos"})
    except OSError:
        return [], []
    validos, invalidos = integridad.revisar_lista(expedientes)
    rechazos.extend(invalidos)
    return validos, rechazos


def guardar_en_txt(expedientes, ruta=RUTA_ARCHIVO):
    """Sobrescribe el archivo de texto con todos los expedientes (8 campos por linea).

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


def cargar_desde_archivo(ruta=RUTA_ARCHIVO):
    """Carga los expedientes desde el almacenamiento configurado.

    - Con ALMACENAMIENTO = "txt" lee el archivo de texto ruta.
    - Con ALMACENAMIENTO = "sqlite" lee mesa_partes.db. Si la base todavia no
      existe y el archivo de texto ruta si, primero migra el texto a la base.
    Retorna la lista de expedientes (vacia si no hay datos o no se pueden leer).
    """
    expedientes, rechazos = cargar_con_informe(ruta)
    return expedientes


def cargar_con_informe(ruta=RUTA_ARCHIVO):
    """Carga y retorna (expedientes, rechazos) del almacenamiento configurado.

    Con "txt" revisa la integridad de cada linea; con "sqlite" la base ya
    garantiza las columnas, asi que no hay rechazos que informar.
    """
    if ALMACENAMIENTO == "sqlite":
        if not os.path.exists(persistencia_db.RUTA_DB) and os.path.exists(ruta):
            persistencia_db.migrar_txt_a_db(ruta)
        return persistencia_db.cargar_desde_db(), []
    return cargar_txt_con_informe(ruta)


def guardar_en_archivo(expedientes, ruta=RUTA_ARCHIVO):
    """Guarda todos los expedientes en el almacenamiento configurado.

    - Con ALMACENAMIENTO = "txt" sobrescribe el archivo de texto ruta.
    - Con ALMACENAMIENTO = "sqlite" reemplaza el contenido de mesa_partes.db
      (ruta no se usa).
    Retorna True si se guardo y False si hubo un error.
    """
    if ALMACENAMIENTO == "sqlite":
        return persistencia_db.guardar_en_db(expedientes)
    return guardar_en_txt(expedientes, ruta)
