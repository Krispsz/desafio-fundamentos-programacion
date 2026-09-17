from expediente import crear_expediente, generar_codigo
from persistencia import guardar_en_archivo
from validaciones import validar_datos
from procesamiento import buscar_posicion

def registrar_expediente(expedientes):
    """Pide datos en bucle hasta que sean validos, genera codigo,
    crea el expediente, lo agrega y guarda el archivo."""
    while True:
        nombre = input("Nombre: ")
        dni = input("DNI: ")
        asunto = input("Asunto: ")
        if validar_datos(nombre, dni, asunto):
            break
        print("Datos invalidos, intente de nuevo.")

    codigo = generar_codigo(expedientes)
    fecha = date.today().isoformat()
    nuevo = crear_expediente(codigo, nombre, dni, asunto, fecha)
    expedientes.append(nuevo)
    guardar_en_archivo(expedientes)
    # TODO (Cristobal)
    pass

def modificar_expediente(expedientes):
    """Busca por codigo con buscar_posicion(). Si no existe, avisa.
    Si existe, pide datos nuevos, valida en bucle, reemplaza y guarda."""
    
    # TODO (Cristobal) - usa buscar_posicion(expedientes, codigo)
    pass
