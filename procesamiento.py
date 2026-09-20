from persistencia import guardar_en_archivo

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
                expedientes[j + 1] = temporal
    print(expedientes)
    return expedientes
    # TODO (Alex)
    pass

def eliminar_expediente(expedientes):
    """Busca por codigo con buscar_posicion(), lo quita (pop) y guarda."""
    # TODO (Alex)
    codigo = int(input("Ingrese el codigo del expediente a eliminar: "))
    posicion = buscar_posicion(expedientes, codigo)
    if posicion == None:
        print("Expediente no encontrado")
    else:
        expedientes.pop(posicion)
        print("Expediente eliminado con éxito.")
        guardar_en_archivo(expedientes)
    pass
