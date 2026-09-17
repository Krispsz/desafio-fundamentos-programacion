from persistencia import cargar_desde_archivo, guardar_en_archivo
from registro import registrar_expediente, modificar_expediente
from procesamiento import buscar_expediente, ordenar_expedientes, eliminar_expediente

def mostrar_menu():
    print("\n--- Mesa de Partes Digital ---")
    print("1. Registrar expediente")
    print("2. Buscar expediente")
    print("3. Modificar expediente")
    print("4. Eliminar expediente")
    print("5. Ordenar expedientes")
    print("6. Salir")

def main():
    expedientes = cargar_desde_archivo()
    salir = False
    while not salir:
        mostrar_menu()
        opcion = input("Elige una opcion: ")
        if opcion == "1":
            registrar_expediente(expedientes)
        elif opcion == "2":
            buscar_expediente(expedientes)
        elif opcion == "3":
            modificar_expediente(expedientes)
        elif opcion == "4":
            eliminar_expediente(expedientes)
        elif opcion == "5":
            ordenar_expedientes(expedientes)
        elif opcion == "6":
            salir = True
        else:
            print("Opcion invalida, intenta de nuevo.")
    guardar_en_archivo(expedientes)
    print("Datos guardados. Hasta luego.")

if __name__ == "__main__":
    main()
