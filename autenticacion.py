"""Login con usuarios.txt: formato usuario|sal|hash|rol (SHA-256 con sal). Solo retorna valores."""

import hashlib
import secrets

RUTA_USUARIOS = "usuarios.txt"

SEPARADOR = "|"


def hash_contrasena(contrasena, sal):
    """SHA-256 en hexadecimal de sal + contrasena."""
    return hashlib.sha256((sal + contrasena).encode("utf-8")).hexdigest()


def leer_usuarios(ruta=RUTA_USUARIOS):
    """Lista de usuarios leidos de usuarios.txt; vacia si el archivo no existe."""
    usuarios = []
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if linea == "":
                    continue
                campos = linea.split(SEPARADOR)
                if len(campos) != 4:
                    continue
                usuario, sal, hash_guardado, rol = campos
                usuarios.append({
                    "usuario": usuario,
                    "sal": sal,
                    "hash": hash_guardado,
                    "rol": rol,
                })
    except FileNotFoundError:
        return usuarios
    return usuarios


def verificar_login(usuario, contrasena, ruta=RUTA_USUARIOS):
    """(True, rol) si el hash de la clave coincide con usuarios.txt; si no, (False, "")."""
    usuario = usuario.strip().lower()
    for registrado in leer_usuarios(ruta):
        if registrado["usuario"].lower() == usuario:
            if registrado["hash"] == hash_contrasena(contrasena, registrado["sal"]):
                return True, registrado["rol"]
            return False, ""
    return False, ""


def usuario_existe(usuario, ruta=RUTA_USUARIOS):
    """True si el usuario esta registrado en usuarios.txt."""
    usuario = usuario.strip().lower()
    for registrado in leer_usuarios(ruta):
        if registrado["usuario"].lower() == usuario:
            return True
    return False


def agregar_usuario(usuario, contrasena, rol, ruta=RUTA_USUARIOS):
    """Agrega a usuarios.txt con sal aleatoria; False si es invalido o ya existia."""
    usuario = usuario.strip()
    rol = rol.strip()
    if usuario == "" or contrasena == "" or rol == "":
        return False
    if SEPARADOR in usuario or SEPARADOR in contrasena or SEPARADOR in rol:
        return False
    if usuario_existe(usuario, ruta):
        return False
    sal = secrets.token_hex(8)
    with open(ruta, "a", encoding="utf-8") as archivo:
        archivo.write(usuario + SEPARADOR + sal + SEPARADOR
                      + hash_contrasena(contrasena, sal) + SEPARADOR + rol + "\n")
    return True
