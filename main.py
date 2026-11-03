"""Punto de entrada de la Mesa de Partes Digital: integra todos los modulos.

Convencion: este archivo es la capa de consola (aqui van los input y print);
los modulos de logica solo reciben parametros y retornan valores."""

import getpass
import os

import integridad
from autenticacion import ROLES, crear_cuenta, verificar_login
from persistencia import cargar_con_informe, guardar_en_archivo
from registro import (registrar_expediente, modificar_expediente,
                      cambiar_estado_expediente)
from procesamiento import (buscar_expediente, buscar_textual, ordenar_expedientes,
                           eliminar_expediente, listar_expedientes)

MAX_INTENTOS = 3


def iniciar_sesion():
    """Pide usuario y contrasena hasta MAX_INTENTOS veces.

    Retorna (usuario, rol) si el acceso es correcto, o (None, "") si se agotan
    los intentos. La verificacion la hace verificar_login() de autenticacion.py.
    """
    print("=== Mesa de Partes Digital: inicio de sesion ===")
    intentos = 0
    while intentos < MAX_INTENTOS:
        usuario = input("Usuario: ").strip()
        clave = getpass.getpass("Contrasena: ")
        valido, rol = verificar_login(usuario, clave)
        if valido:
            return usuario.lower(), rol
        intentos = intentos + 1
        if intentos < MAX_INTENTOS:
            print("Usuario o contrasena incorrectos. Intentos restantes: "
                  + str(MAX_INTENTOS - intentos))
    return None, ""

def mostrar_menu():
    """Imprime las opciones disponibles del menu principal."""
    print("\n--- Mesa de Partes Digital ---")
    print("1. Registrar expediente")
    print("2. Buscar expediente por codigo")
    print("3. Buscar por texto (nombre o asunto)")
    print("4. Modificar expediente")
    print("5. Eliminar expediente")
    print("6. Ordenar expedientes")
    print("7. Listar expedientes")
    print("8. Cambiar estado de un expediente")
    print("9. Salir")
    print("10. Crear usuario (solo administrador)")

def elegir_rol():
    """Muestra los roles numerados y repite hasta que la opcion sea valida."""
    while True:
        print("Roles:")
        for i in range(len(ROLES)):
            print("  " + str(i + 1) + ". " + ROLES[i])
        opcion = input("Rol (1-" + str(len(ROLES)) + "): ").strip()
        if opcion.isdigit() and 1 <= int(opcion) <= len(ROLES):
            return ROLES[int(opcion) - 1]
        print("Opcion invalida, intente de nuevo.")

def crear_usuario_consola():
    """Pide los datos de la cuenta y muestra el mensaje que retorna crear_cuenta()."""
    usuario = input("Usuario nuevo: ").strip()
    clave = getpass.getpass("Contrasena: ")
    confirmacion = getpass.getpass("Confirmar contrasena: ")
    rol = elegir_rol()
    creada, mensaje = crear_cuenta(usuario, clave, confirmacion, rol)
    print(mensaje)

def main():
    """Inicia sesion, carga los expedientes, ejecuta el menu y guarda al salir."""
    usuario, rol = iniciar_sesion()
    if usuario is None:
        print("Acceso bloqueado: se agotaron los " + str(MAX_INTENTOS) + " intentos.")
        return
    print("Bienvenido, " + usuario + " (" + rol + ")")
    expedientes, rechazos = cargar_con_informe()
    print("Expedientes cargados: " + str(len(expedientes)))
    if rechazos:
        print(integridad.resumir_rechazos(rechazos))
    salir = False
    while not salir:
        mostrar_menu()
        opcion = input("Elige una opcion: ").strip()
        if opcion == "1":
            registrar_expediente(expedientes, usuario)
        elif opcion == "10" and rol != "administrador":
            print("Solo el administrador puede crear usuarios.")
        elif opcion == "10":
            crear_usuario_consola()
        elif opcion in ("2", "3", "4", "5", "6", "7", "8") and len(expedientes) == 0:
            print("No hay expedientes registrados.")
        elif opcion == "2":
            buscar_expediente(expedientes)
        elif opcion == "3":
            buscar_textual(expedientes)
        elif opcion == "4":
            modificar_expediente(expedientes)
        elif opcion == "5" and rol != "administrador":
            print("Solo el administrador puede eliminar expedientes.")
        elif opcion == "5":
            eliminar_expediente(expedientes)
        elif opcion == "6":
            ordenar_expedientes(expedientes)
        elif opcion == "7":
            listar_expedientes(expedientes)
        elif opcion == "8":
            cambiar_estado_expediente(expedientes, usuario)
        elif opcion == "9":
            salir = True
        else:
            print("Opcion invalida, intenta de nuevo.")
    if guardar_en_archivo(expedientes):
        print("Datos guardados. Hasta luego.")
    else:
        print("No se pudieron guardar los datos.")

if __name__ == "__main__":
    # Las rutas de los datos son relativas: se trabaja en la carpeta del
    # programa para encontrar usuarios.txt aunque se ejecute desde otra.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
