"""Login con usuarios.txt: formato usuario|sal|hash|rol (SHA-256 con sal). Solo retorna valores."""

import hashlib
import secrets

RUTA_USUARIOS = "usuarios.txt"

SEPARADOR = "|"

ROLES = ["administrador", "usuario"]

LONGITUD_MINIMA = 6


def hash_contrasena(contrasena, sal):
    """SHA-256 en hexadecimal de sal + contrasena."""
    return hashlib.sha256((sal + contrasena).encode("utf-8")).hexdigest()


def leer_usuarios(ruta=RUTA_USUARIOS):
    """Lista de usuarios leidos de usuarios.txt; vacia si el archivo no existe."""
    usuarios = []
    try:
        # utf-8-sig acepta el archivo con y sin BOM (el Bloc de notas lo agrega
        # al guardar); pegado al primer usuario, ese usuario no podia entrar.
        with open(ruta, "r", encoding="utf-8-sig") as archivo:
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


def crear_cuenta(usuario, clave, confirmacion, rol, ruta=RUTA_USUARIOS):
    """Valida y crea una cuenta. Retorna (creada, mensaje).

    Las reglas se revisan en este orden: usuario no vacio y sin |, clave igual
    a la confirmacion, clave de al menos LONGITUD_MINIMA caracteres, rol de
    ROLES y usuario no registrado. Si todo esta bien, la guarda con
    agregar_usuario() (sal aleatoria y hash, nunca la contrasena).
    """
    if usuario.strip() == "" or SEPARADOR in usuario:
        return False, "Usuario invalido"
    if clave != confirmacion:
        return False, "Las contrasenas no coinciden"
    if len(clave) < LONGITUD_MINIMA:
        return False, ("La contrasena debe tener al menos " + str(LONGITUD_MINIMA)
                       + " caracteres")
    if rol not in ROLES:
        return False, "Rol invalido"
    if usuario_existe(usuario, ruta):
        return False, "El usuario ya existe"
    if agregar_usuario(usuario, clave, rol, ruta):
        return True, "Cuenta creada"
    return False, "No se pudo crear la cuenta"
