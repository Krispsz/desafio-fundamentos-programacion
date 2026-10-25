from persistencia import guardar_en_archivo

ENCABEZADOS = ["Codigo", "Nombre", "DNI", "Asunto", "Fecha", "Estado", "Dependencia"]


# --- logica: solo recibe parametros y retorna valores (sin input/print) ---

def buscar_posicion(expedientes, codigo):
    """Retorna el indice del expediente con ese codigo, o None si no existe."""
    for i in range(len(expedientes)):
        if expedientes[i]["codigo"] == codigo:
            return i
    return None


def buscar_por_texto(expedientes, campo, texto):
    """Retorna los expedientes cuyo campo ('nombre' o 'asunto') contiene el
    texto, sin distinguir mayusculas. Usa lower() y find()."""
    resultados = []
    buscado = texto.lower()
    for i in range(len(expedientes)):
        if expedientes[i][campo].lower().find(buscado) != -1:
            resultados.append(expedientes[i])
    return resultados


def validar_busqueda(campo, texto):
    """Retorna True si el campo es nombre/asunto y el texto no esta vacio."""
    return campo in ("nombre", "asunto") and texto != ""


def validar_criterio(criterio):
    """Retorna True si el criterio de ordenamiento es uno de los permitidos."""
    return criterio in ("codigo", "nombre", "dni", "asunto", "fecha")


def ordenar_con_burbuja(expedientes, criterio):
    """Ordena la lista in place con el algoritmo BURBUJA (no usar sorted()
    ni list.sort()). Retorna la lista ordenada o None si el criterio es invalido."""
    if not validar_criterio(criterio):
        return None
    n = len(expedientes)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            if expedientes[j][criterio] > expedientes[j + 1][criterio]:
                temporal = expedientes[j]
                expedientes[j] = expedientes[j + 1]
                expedientes[j + 1] = temporal
    return expedientes


def eliminar_por_codigo(expedientes, codigo):
    """Quita el expediente de la lista (pop) y guarda el archivo.
    Retorna (eliminado, guardado)."""
    posicion = buscar_posicion(expedientes, codigo)
    if posicion is None:
        return False, False
    expedientes.pop(posicion)
    guardado = guardar_en_archivo(expedientes)
    return True, guardado


def construir_matriz(expedientes):
    """Retorna una matriz (lista de listas): la fila 0 son los encabezados y cada
    fila siguiente es [codigo, nombre, dni, asunto, fecha, estado, dependencia].
    El asunto se recorta a 25 caracteres con [:22] + '...' si es mas largo."""
    matriz = [ENCABEZADOS]
    for expediente in expedientes:
        asunto = expediente["asunto"]
        if len(asunto) > 25:
            asunto = asunto[:22] + "..."
        fila = [expediente["codigo"], expediente["nombre"], expediente["dni"],
                asunto, expediente["fecha"], expediente["estado"],
                expediente["dependencia"]]
        matriz.append(fila)
    return matriz


def calcular_anchos(matriz):
    """Retorna la lista de anchos maximos por columna, calculada con dos for
    anidados (fila x columna) sin imprimir nada."""
    anchos = []
    for columna in range(len(matriz[0])):
        anchos.append(0)
    for fila in range(len(matriz)):
        for columna in range(len(matriz[fila])):
            if len(matriz[fila][columna]) > anchos[columna]:
                anchos[columna] = len(matriz[fila][columna])
    return anchos


def formatear_linea(fila, anchos):
    """Retorna la fila como texto alineado con ljust y separado por ' | '."""
    linea = ""
    for columna in range(len(fila)):
        if columna > 0:
            linea = linea + " | "
        linea = linea + fila[columna].ljust(anchos[columna])
    return linea


def formatear_separador(anchos):
    """Retorna la linea de guiones que separa el encabezado de los datos."""
    separador = ""
    for columna in range(len(anchos)):
        if columna > 0:
            separador = separador + "-+-"
        separador = separador + "-" * anchos[columna]
    return separador


# --- consola: aqui van los input y print ---

def mostrar_expediente(expediente):
    """Imprime los datos de un expediente en una linea."""
    print(f'{expediente["codigo"]} | {expediente["nombre"]} | {expediente["dni"]} | '
          f'{expediente["asunto"]} | {expediente["fecha"]} | {expediente["estado"]} | '
          f'{expediente["dependencia"]}')


def imprimir_tabla(expedientes):
    """Construye la matriz, calcula los anchos y la imprime alineada."""
    matriz = construir_matriz(expedientes)
    anchos = calcular_anchos(matriz)
    for fila in range(len(matriz)):
        print(formatear_linea(matriz[fila], anchos))
        if fila == 0:
            print(formatear_separador(anchos))


def listar_expedientes(expedientes):
    """Muestra todos los expedientes en tabla, o un aviso si no hay ninguno."""
    if len(expedientes) == 0:
        print("No hay expedientes registrados.")
        return
    imprimir_tabla(expedientes)


def buscar_expediente(expedientes):
    """Pide un codigo, usa buscar_posicion() y muestra el resultado."""
    codigo = input("Ingrese codigo a buscar: ").strip()
    posicion = buscar_posicion(expedientes, codigo)
    if posicion is not None:
        mostrar_expediente(expedientes[posicion])
    else:
        print("Expediente no encontrado")


def buscar_textual(expedientes):
    """Pide el campo (nombre/asunto) y el texto; muestra las coincidencias con
    imprimir_tabla o un aviso si la busqueda es invalida o no hay resultados."""
    campo = input("Buscar en (nombre/asunto): ").strip().lower()
    texto = input("Texto a buscar: ").strip()
    if not validar_busqueda(campo, texto):
        print("Busqueda invalida")
        return
    resultados = buscar_por_texto(expedientes, campo, texto)
    if len(resultados) == 0:
        print("Sin coincidencias")
        return
    imprimir_tabla(resultados)


def ordenar_expedientes(expedientes, criterio="codigo"):
    """Pide el criterio, ordena con ordenar_con_burbuja() y muestra la tabla."""
    ingresado = input("Ingrese criterio (codigo/nombre/dni/asunto/fecha) [codigo]: ").strip()
    if ingresado != "":
        criterio = ingresado
    if ordenar_con_burbuja(expedientes, criterio) is None:
        print("Criterio invalido.")
        return expedientes
    imprimir_tabla(expedientes)
    return expedientes


def eliminar_expediente(expedientes):
    """Pide el codigo y llama a eliminar_por_codigo(); avisa del resultado."""
    codigo = input("Ingrese el codigo del expediente a eliminar: ").strip()
    eliminado, guardado = eliminar_por_codigo(expedientes, codigo)
    if not eliminado:
        print("Expediente no encontrado")
    else:
        print("Expediente eliminado con exito.")
        if not guardado:
            print("No se pudo guardar en expedientes.txt. Revise el archivo.")
