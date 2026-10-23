"""Punto de entrada de la Mesa de Partes Digital: integra todos los modulos.

Convencion: este archivo es la capa de consola (aqui van los input y print);
los modulos de logica solo reciben parametros y retornan valores."""

from persistencia import cargar_desde_archivo, guardar_en_archivo
from registro import registrar_expediente, modificar_expediente
from procesamiento import (buscar_expediente, buscar_textual, ordenar_expedientes,
                           eliminar_expediente, listar_expedientes)

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
    print("8. Salir")

def main():
    """Carga los expedientes, ejecuta el menu y guarda los cambios al salir."""
    expedientes = cargar_desde_archivo()
    print("Expedientes cargados: " + str(len(expedientes)))
    salir = False
    while not salir:
        mostrar_menu()
        opcion = input("Elige una opcion: ").strip()
        if opcion == "1":
            registrar_expediente(expedientes, "sistema")
        elif opcion in ("2", "3", "4", "5", "6", "7") and len(expedientes) == 0:
            print("No hay expedientes registrados.")
        elif opcion == "2":
            buscar_expediente(expedientes)
        elif opcion == "3":
            buscar_textual(expedientes)
        elif opcion == "4":
            modificar_expediente(expedientes)
        elif opcion == "5":
            eliminar_expediente(expedientes)
        elif opcion == "6":
            ordenar_expedientes(expedientes)
        elif opcion == "7":
            listar_expedientes(expedientes)
        elif opcion == "8":
            salir = True
        else:
            print("Opcion invalida, intenta de nuevo.")
    if guardar_en_archivo(expedientes):
        print("Datos guardados. Hasta luego.")
    else:
        print("No se pudo guardar en expedientes.txt. Revise el archivo.")

if __name__ == "__main__":
    main()
