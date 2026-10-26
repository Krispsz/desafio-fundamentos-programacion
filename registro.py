from datetime import date

from expediente import crear_expediente, generar_codigo, DEPENDENCIAS
from persistencia import guardar_en_archivo
from validaciones import validar_datos, normalizar_texto
from procesamiento import buscar_posicion


def preparar_datos(nombre, dni, asunto):
    """Normaliza y valida; retorna (nombre, dni, asunto) o None si no pasan."""
    nombre = normalizar_texto(nombre).title()
    dni = dni.replace(" ", "")
    asunto = normalizar_texto(asunto)
    if validar_datos(nombre, dni, asunto):
        return nombre, dni, asunto
    return None


def obtener_dependencia(opcion):
    """Retorna el nombre de la dependencia (1-5) o None si la opcion es invalida."""
    if opcion.isdigit() and 1 <= int(opcion) <= len(DEPENDENCIAS):
        return DEPENDENCIAS[int(opcion) - 1]
    return None


def crear_registro(expedientes, nombre, dni, asunto, dependencia, usuario):
    """Crea el expediente con historial, lo agrega y guarda.
    Retorna (codigo, guardado): el codigo asignado y si el guardado tuvo exito."""
    codigo = generar_codigo(expedientes)
    fecha = date.today().isoformat()
    historial = [{"fecha": fecha, "estado": "Recibido", "usuario": usuario}]
    nuevo = crear_expediente(codigo, nombre, dni, asunto, fecha,
                             "Recibido", dependencia, historial)
    expedientes.append(nuevo)
    guardado = guardar_en_archivo(expedientes)
    return codigo, guardado


def aplicar_modificacion(expedientes, codigo, nombre, dni, asunto):
    """Reemplaza el expediente conservando fecha, estado, dependencia e historial.
    Retorna (modifico, guardado): si existia el codigo y si el guardado tuvo exito."""
    pos = buscar_posicion(expedientes, codigo)
    if pos is None:
        return False, False
    original = expedientes[pos]
    expedientes[pos] = crear_expediente(codigo, nombre, dni, asunto, original["fecha"],
                                        original["estado"], original["dependencia"],
                                        original["historial"])
    guardado = guardar_en_archivo(expedientes)
    return True, guardado


def elegir_dependencia():
    """Muestra las dependencias numeradas y repite hasta que la opcion sea valida."""
    while True:
        print("Dependencias:")
        for i in range(len(DEPENDENCIAS)):
            print("  " + str(i + 1) + ". " + DEPENDENCIAS[i])
        opcion = input("Dependencia (1-" + str(len(DEPENDENCIAS)) + "): ").strip()
        nombre = obtener_dependencia(opcion)
        if nombre is not None:
            return nombre
        print("Opcion invalida, intente de nuevo.")


def registrar_expediente(expedientes, usuario):
    """Pide datos en bucle hasta que preparar_datos() los aprueba, elige la
    dependencia y crea el expediente con crear_registro()."""
    while True:
        nombre = input("Nombre: ")
        dni = input("DNI: ")
        asunto = input("Asunto: ")
        datos = preparar_datos(nombre, dni, asunto)
        if datos is not None:
            break
        print("Datos invalidos, intente de nuevo.")
    dependencia = elegir_dependencia()
    codigo, guardado = crear_registro(expedientes, datos[0], datos[1], datos[2],
                                      dependencia, usuario)
    print("Expediente registrado con codigo " + codigo)
    if not guardado:
        print("No se pudo guardar en expedientes.txt. Revise el archivo.")


def modificar_expediente(expedientes):
    """Busca por codigo con buscar_posicion(). Si no existe, avisa.
    Si existe, pide datos nuevos, valida en bucle y llama a aplicar_modificacion()."""
    codigo = input("Codigo a modificar: ").strip()
    if buscar_posicion(expedientes, codigo) is None:
        print("Expediente no encontrado.")
        return
    while True:
        nombre = input("Nombre: ")
        dni = input("DNI: ")
        asunto = input("Asunto: ")
        datos = preparar_datos(nombre, dni, asunto)
        if datos is not None:
            break
        print("Datos invalidos, intente de nuevo.")
    modifico, guardado = aplicar_modificacion(expedientes, codigo, datos[0], datos[1],
                                              datos[2])
    if modifico:
        print("Expediente modificado.")
        if not guardado:
            print("No se pudo guardar en expedientes.txt. Revise el archivo.")
    else:
        print("Expediente no encontrado.")
