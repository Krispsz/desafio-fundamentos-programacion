from persistencia import guardar_en_archivo
expedientes = [
    {"codigo": 8212, "nombre": "Juana Pérez"},
    {"codigo": 6121, "nombre": "Carlos Gómez"},
    {"codigo": 1131, "nombre": "Ana Torres"},
    {"codigo": 5313, "nombre": "Luis Mendoza"}
]


def buscar_posicion(expedientes, codigo):
    """Retorna el indice del expediente con ese codigo, o None si no existe."""
    for i in range(len(expedientes)):
        if expedientes[i]["codigo"] == codigo:
            return i
    return None
    # TODO (Alex) - subir primero, Cristobal depende de esta funcion
    pass

def buscar_expediente(expedientes):
    """Pide un codigo, usa buscar_posicion() y muestra el resultado."""
    codigo = int(input("Ingrese codigo a buscar: "))
    posicion = buscar_posicion(expedientes, codigo)
    if posicion != None:
        print(f'Expediente N°: {posicion}')
    else:
        print("Expediente no encontrado")
    # TODO (Alex)
    pass

def ordenar_expedientes(expedientes, criterio="codigo"):
    """Ordena con algoritmo BURBUJA (no usar sorted() ni list.sort())."""
    criterio = input("Ingrese criterio: ")
    n = len(expedientes)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            if expedientes[j][criterio] > expedientes[j + 1][criterio]:
                temporal = expedientes[j]
                expedientes[j] = expedientes[j + 1]
                temporal = expedientes[j + 1]
    print(expedientes)
    return expedientes
    # TODO (Alex)
    pass

def eliminar_expediente(expedientes):
    """Busca por codigo con buscar_posicion(), lo quita (pop) y guarda."""
    # TODO (Alex)
    pass

print("--- ANTES DE ORDENAR ---")
for exp in expedientes:
    print(exp)

# Ejecutamos la función
ordenar_expedientes(expedientes)

print("\n--- DESPUÉS DE ORDENAR ---")
for exp in expedientes:
    print(exp)