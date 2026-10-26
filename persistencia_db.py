"""Lectura y escritura de los expedientes en una base de datos SQLite.

Todas las consultas usan parametros con "?": los datos nunca se pegan al texto
del SQL, asi un nombre como O'Brien no rompe la consulta (inyeccion SQL).
"""

import os
import sqlite3

from expediente import crear_expediente

RUTA_DB = "mesa_partes.db"

SQL_TABLA_EXPEDIENTES = """
CREATE TABLE IF NOT EXISTS expedientes (
    codigo      TEXT PRIMARY KEY,
    nombre      TEXT NOT NULL,
    dni         TEXT NOT NULL,
    asunto      TEXT NOT NULL,
    fecha       TEXT NOT NULL,
    estado      TEXT NOT NULL,
    dependencia TEXT NOT NULL
)"""

SQL_TABLA_HISTORIAL = """
CREATE TABLE IF NOT EXISTS historial (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo  TEXT NOT NULL REFERENCES expedientes(codigo),
    fecha   TEXT NOT NULL,
    estado  TEXT NOT NULL,
    usuario TEXT NOT NULL
)"""


def crear_tablas(ruta=None):
    """Crea las tablas expedientes e historial si no existen.

    Retorna True si quedaron creadas y False si hubo un error de SQLite.
    Si no se envia ruta se usa RUTA_DB, leida al llamar a la funcion: un valor
    por defecto ruta=RUTA_DB se fijaria al importar el modulo y no veria los
    cambios posteriores de persistencia_db.RUTA_DB.
    """
    if ruta is None:
        ruta = RUTA_DB
    try:
        with sqlite3.connect(ruta) as conexion:
            conexion.execute(SQL_TABLA_EXPEDIENTES)
            conexion.execute(SQL_TABLA_HISTORIAL)
        conexion.close()
    except sqlite3.Error:
        return False
    return True


def guardar_en_db(expedientes, ruta=None):
    """Reemplaza todo el contenido de la base con la lista de expedientes.

    Igual que el .txt, que se sobrescribe completo: borra las dos tablas y
    vuelve a insertar todo. Se hace en una sola transaccion (el bloque with):
    si algo falla, se deshace y la base queda como estaba.
    Retorna True si se guardo y False si hubo un error.
    Si no se envia ruta se usa RUTA_DB, leida al llamar a la funcion: un valor
    por defecto ruta=RUTA_DB se fijaria al importar el modulo y no veria los
    cambios posteriores de persistencia_db.RUTA_DB.
    """
    if ruta is None:
        ruta = RUTA_DB
    if not crear_tablas(ruta):
        return False
    try:
        with sqlite3.connect(ruta) as conexion:
            conexion.execute("DELETE FROM historial")
            conexion.execute("DELETE FROM expedientes")
            for expediente in expedientes:
                conexion.execute(
                    "INSERT INTO expedientes (codigo, nombre, dni, asunto, fecha, estado, dependencia) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (expediente["codigo"], expediente["nombre"], expediente["dni"],
                     expediente["asunto"], expediente["fecha"], expediente["estado"],
                     expediente["dependencia"]))
                for entrada in expediente["historial"]:
                    conexion.execute(
                        "INSERT INTO historial (codigo, fecha, estado, usuario) VALUES (?, ?, ?, ?)",
                        (expediente["codigo"], entrada["fecha"], entrada["estado"],
                         entrada["usuario"]))
        conexion.close()
    except sqlite3.Error:
        return False
    return True


def cargar_desde_db(ruta=None):
    """Lee la base y retorna la lista de expedientes ordenada por codigo.

    Cada expediente tiene el mismo formato que crear_expediente(), con su
    historial como lista de {"fecha", "estado", "usuario"} en el orden en que
    se guardo (por id). Si la base no existe o hay un error, retorna [].
    Si no se envia ruta se usa RUTA_DB, leida al llamar a la funcion: un valor
    por defecto ruta=RUTA_DB se fijaria al importar el modulo y no veria los
    cambios posteriores de persistencia_db.RUTA_DB.
    """
    if ruta is None:
        ruta = RUTA_DB
    if not os.path.exists(ruta):
        return []
    expedientes = []
    try:
        with sqlite3.connect(ruta) as conexion:
            historiales = {}
            filas = conexion.execute(
                "SELECT codigo, fecha, estado, usuario FROM historial ORDER BY id")
            for codigo, fecha, estado, usuario in filas:
                if codigo not in historiales:
                    historiales[codigo] = []
                historiales[codigo].append({"fecha": fecha, "estado": estado, "usuario": usuario})
            filas = conexion.execute(
                "SELECT codigo, nombre, dni, asunto, fecha, estado, dependencia "
                "FROM expedientes ORDER BY codigo")
            for codigo, nombre, dni, asunto, fecha, estado, dependencia in filas:
                historial = historiales.get(codigo, [])
                expedientes.append(crear_expediente(codigo, nombre, dni, asunto, fecha,
                                                    estado, dependencia, historial))
        conexion.close()
    except sqlite3.Error:
        return []
    return expedientes


def migrar_txt_a_db(ruta_txt, ruta_db=None):
    """Copia los expedientes de expedientes.txt a la base de datos.

    Retorna la cantidad de expedientes migrados, o -1 si el archivo de texto
    no existe o no se pudo guardar en la base.
    Si no se envia ruta_db se usa RUTA_DB, leida al llamar a la funcion: un valor
    por defecto ruta_db=RUTA_DB se fijaria al importar el modulo y no veria los
    cambios posteriores de persistencia_db.RUTA_DB.
    """
    if ruta_db is None:
        ruta_db = RUTA_DB
    # Se importa aqui y no arriba para evitar una importacion circular:
    # persistencia.py tambien importa este modulo.
    from persistencia import cargar_desde_txt
    if not os.path.exists(ruta_txt):
        return -1
    expedientes = cargar_desde_txt(ruta_txt)
    if not guardar_en_db(expedientes, ruta_db):
        return -1
    return len(expedientes)
