from persistencia import guardar_en_archivo

def buscar_posicion(expedientes, codigo):
    """Retorna el indice del expediente con ese codigo, o None si no existe."""
    for i in range(len(expedientes)):
        if expedientes[i]["codigo"] == codigo:
            return i
    return None

def mostrar_expediente(expediente):
    """Imprime los datos de un expediente en una linea."""
    print(f'{expediente["codigo"]} | {expediente["nombre"]} | {expediente["dni"]} | '
          f'{expediente["asunto"]} | {expediente["fecha"]}')

def buscar_expediente(expedientes):
    """Pide un codigo, usa buscar_posicion() y muestra el resultado."""
    codigo = input("Ingrese codigo a buscar: ").strip()
    posicion = buscar_posicion(expedientes, codigo)
    if posicion != None:
        mostrar_expediente(expedientes[posicion])
    else:
        print("Expediente no encontrado")

def buscar_por_texto(expedientes, campo, texto):
    """Retorna una lista con los expedientes cuyo campo ('nombre' o 'asunto')
    contiene el texto, sin distinguir mayusculas. Usa lower() y find()."""
    resultados = []
    buscado = texto.lower()
    for i in range(len(expedientes)):
        if expedientes[i][campo].lower().find(buscado) != -1:
            resultados.append(expedientes[i])
    return resultados

def buscar_textual(expedientes):
    """Pide el campo (nombre/asunto) y el texto; muestra las coincidencias
    o 'Sin coincidencias' si la lista queda vacia."""
    campo = input("Buscar en (nombre/asunto): ").strip().lower()
    texto = input("Texto a buscar: ").strip()
    if campo not in ("nombre", "asunto") or texto == "":
        print("Busqueda invalida")
        return
    resultados = buscar_por_texto(expedientes, campo, texto)
    if len(resultados) == 0:
        print("Sin coincidencias")
        return
    for expediente in resultados:
        mostrar_expediente(expediente)

def ordenar_expedientes(expedientes, criterio="codigo"):
    """Ordena con algoritmo BURBUJA (no usar sorted() ni list.sort())."""
    ingresado = input("Ingrese criterio (codigo/nombre/dni/asunto/fecha) [codigo]: ").strip()
    if ingresado != "":
        criterio = ingresado
    if criterio not in ("codigo", "nombre", "dni", "asunto", "fecha"):
        print("Criterio invalido.")
        return expedientes
    n = len(expedientes)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            if expedientes[j][criterio] > expedientes[j + 1][criterio]:
                temporal = expedientes[j]
                expedientes[j] = expedientes[j + 1]
                expedientes[j + 1] = temporal
    for expediente in expedientes:
        mostrar_expediente(expediente)
    return expedientes

def eliminar_expediente(expedientes):
    """Busca por codigo con buscar_posicion(), lo quita (pop) y guarda."""
    codigo = input("Ingrese el codigo del expediente a eliminar: ").strip()
    posicion = buscar_posicion(expedientes, codigo)
    if posicion == None:
        print("Expediente no encontrado")
    else:
        expedientes.pop(posicion)
        print("Expediente eliminado con éxito.")
        guardar_en_archivo(expedientes)
