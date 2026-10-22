"""Login de usuarios de la Mesa de Partes Digital.

Formato de usuarios.txt (un usuario por linea, campos separados por |):
    usuario|hash|rol

El hash es el resumen SHA-256 en hexadecimal de la contrasena en texto plano.
Ninguna funcion de este modulo imprime ni pide datos: solo retornan valores
(True/False y el rol). El bucle de intentos y los mensajes viven en main.py.
"""

import hashlib

RUTA_USUARIOS = "usuarios.txt"

SEPARADOR = "|"


def hash_contrasena(contrasena):
    """Retorna el hash SHA-256 en hexadecimal de la contrasena recibida."""
    return hashlib.sha256(contrasena.encode("utf-8")).hexdigest()


def leer_usuarios(ruta=RUTA_USUARIOS):
    """Lee usuarios.txt con with open y retorna la lista de usuarios.

    Cada usuario es un diccionario con las claves usuario, hash y rol.
    Si el archivo no existe o una linea esta mal formada, se omite esa linea.
    """
    usuarios = []
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if linea == "":
                    continue
                campos = linea.split(SEPARADOR)
                if len(campos) != 3:
                    continue
                usuario, hash_guardado, rol = campos
                usuarios.append({
                    "usuario": usuario,
                    "hash": hash_guardado,
                    "rol": rol,
                })
    except FileNotFoundError:
        return usuarios
    return usuarios


def verificar_login(usuario, contrasena, ruta=RUTA_USUARIOS):
    """Retorna (True, rol) si usuario y contrasena coinciden con usuarios.txt.
    Retorna (False, "") si el usuario no existe o la contrasena es incorrecta.
    El nombre de usuario no distingue mayusculas; la contrasena si."""
    usuario = usuario.strip().lower()
    for registrado in leer_usuarios(ruta):
        if registrado["usuario"].lower() == usuario:
            if registrado["hash"] == hash_contrasena(contrasena):
                return True, registrado["rol"]
            return False, ""
    return False, ""


def usuario_existe(usuario, ruta=RUTA_USUARIOS):
    """Retorna True si el usuario ya esta registrado en usuarios.txt."""
    usuario = usuario.strip().lower()
    for registrado in leer_usuarios(ruta):
        if registrado["usuario"].lower() == usuario:
            return True
    return False


def agregar_usuario(usuario, contrasena, rol, ruta=RUTA_USUARIOS):
    """Agrega un usuario a usuarios.txt guardando el hash de la contrasena.

    Retorna True si se registro; False si los datos son invalidos
    (vacios o con el separador |) o si el usuario ya existia.
    """
    usuario = usuario.strip()
    contrasena = contrasena.strip()
    rol = rol.strip()
    if usuario == "" or contrasena == "" or rol == "":
        return False
    if SEPARADOR in usuario or SEPARADOR in contrasena or SEPARADOR in rol:
        return False
    if usuario_existe(usuario, ruta):
        return False
    with open(ruta, "a", encoding="utf-8") as archivo:
        archivo.write(usuario + SEPARADOR + hash_contrasena(contrasena)
                      + SEPARADOR + rol + "\n")
    return True
