from datetime import date

from expediente import crear_expediente, generar_codigo, DEPENDENCIAS
from persistencia import guardar_en_archivo
from validaciones import validar_datos, normalizar_texto
from procesamiento import buscar_posicion

def elegir_dependencia():
    """Muestra las dependencias numeradas y repite hasta elegir una valida."""
    while True:
        print("Dependencias:")
        for i in range(len(DEPENDENCIAS)):
            print("  " + str(i + 1) + ". " + DEPENDENCIAS[i])
        opcion = input("Dependencia (1-" + str(len(DEPENDENCIAS)) + "): ").strip()
        if opcion.isdigit() and 1 <= int(opcion) <= len(DEPENDENCIAS):
            return DEPENDENCIAS[int(opcion) - 1]
        print("Opcion invalida, intente de nuevo.")

def registrar_expediente(expedientes, usuario):
    """Pide datos en bucle hasta que sean validos, elige la dependencia, genera
    codigo, crea el expediente con historial a nombre del usuario y guarda."""
    while True:
        nombre = input("Nombre: ")
        nombre = normalizar_texto(nombre).title()
        dni = input("DNI: ")
        dni = dni.replace(" ", "")
        asunto = input("Asunto: ")
        asunto = normalizar_texto(asunto)
        if validar_datos(nombre, dni, asunto):
            break
        print("Datos invalidos, intente de nuevo.")

    dependencia = elegir_dependencia()
    codigo = generar_codigo(expedientes)
    fecha = date.today().isoformat()
    historial = [{"fecha": fecha, "estado": "Recibido", "usuario": usuario}]
    nuevo = crear_expediente(codigo, nombre, dni, asunto, fecha,
                             "Recibido", dependencia, historial)
    expedientes.append(nuevo)
    guardar_en_archivo(expedientes)
    print("Expediente registrado con codigo " + codigo)

def modificar_expediente(expedientes):
    """Busca por codigo con buscar_posicion(). Si no existe, avisa.
    Si existe, pide datos nuevos, valida en bucle, reemplaza y guarda.
    Conserva fecha, estado, dependencia e historial del expediente original."""
    codigo = input("Codigo a modificar: ")
    pos = buscar_posicion(expedientes, codigo)
    if pos is None:
        print("Expediente no encontrado.")
        return
    while True:
        nombre = input("Nombre: ")
        nombre = normalizar_texto(nombre).title()
        dni = input("DNI: ")
        dni = dni.replace(" ", "")
        asunto = input("Asunto: ")
        asunto = normalizar_texto(asunto)
        if validar_datos(nombre, dni, asunto):
            break
        print("Datos invalidos, intente de nuevo.")
    original = expedientes[pos]
    expedientes[pos] = crear_expediente(codigo, nombre, dni, asunto, original["fecha"],
                                        original["estado"], original["dependencia"],
                                        original["historial"])
    guardar_en_archivo(expedientes)
    print("Expediente modificado.")
