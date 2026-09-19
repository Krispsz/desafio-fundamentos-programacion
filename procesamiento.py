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

    # TODO (Alex)
    pass

def eliminar_expediente(expedientes):
    """Busca por codigo con buscar_posicion(), lo quita (pop) y guarda."""
    # TODO (Alex)
    pass
