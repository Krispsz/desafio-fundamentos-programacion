"""Revision de integridad de los expedientes leidos del archivo.

Comprueba que cada campo tenga el formato esperado antes de aceptar el
expediente. Las funciones reciben datos y retornan valores: no imprimen ni
piden datos, para poder reutilizarlas desde la consola, la ventana y las
pruebas automaticas.
"""

from datetime import date

from expediente import DEPENDENCIAS, ESTADOS

MAXIMO_DETALLES = 5


def fecha_valida(texto):
    """Retorna True si el texto es una fecha real con formato AAAA-MM-DD."""
    if len(texto) != 10 or texto[4] != "-" or texto[7] != "-":
        return False
    anio, mes, dia = texto[:4], texto[5:7], texto[8:]
    if not (anio.isdigit() and mes.isdigit() and dia.isdigit()):
        return False
    try:
        date(int(anio), int(mes), int(dia))
    except ValueError:
        return False
    return True


def revisar_historial(historial):
    """Retorna la lista de problemas del historial (vacia si esta integro)."""
    if not isinstance(historial, list) or len(historial) == 0:
        return ["historial vacio"]
    problemas = []
    for entrada in historial:
        if not isinstance(entrada, dict):
            problemas.append("historial mal formado")
            continue
        if not fecha_valida(entrada.get("fecha", "")):
            problemas.append("historial con fecha invalida")
        if entrada.get("estado") not in ESTADOS:
            problemas.append("historial con estado desconocido")
        if not entrada.get("usuario"):
            problemas.append("historial sin usuario")
    return problemas


def revisar_expediente(expediente):
    """Retorna los problemas de integridad del expediente; vacia si esta bien."""
    problemas = []
    codigo = expediente.get("codigo", "")
    if not codigo.startswith("EXP-") or not codigo[4:].isdigit() or len(codigo) < 8:
        problemas.append("codigo fuera de formato")
    nombre = expediente.get("nombre", "")
    if not nombre:
        problemas.append("sin nombre")
    elif "|" in nombre:
        problemas.append("nombre con separador")
    dni = expediente.get("dni", "")
    if not (len(dni) == 8 and dni.isdigit()):
        problemas.append("dni invalido")
    asunto = expediente.get("asunto", "")
    if not asunto:
        problemas.append("sin asunto")
    elif "|" in asunto:
        problemas.append("asunto con separador")
    if not fecha_valida(expediente.get("fecha", "")):
        problemas.append("fecha invalida")
    if expediente.get("estado") not in ESTADOS:
        problemas.append("estado desconocido")
    if expediente.get("dependencia") not in DEPENDENCIAS:
        problemas.append("dependencia desconocida")
    problemas.extend(revisar_historial(expediente.get("historial")))
    return problemas


def revisar_lista(expedientes):
    """Separa los expedientes integros de los rechazados.

    Retorna (validos, rechazos). Cada rechazo es {"codigo", "motivo"}.
    Un codigo repetido se rechaza para no trabajar con dos expedientes iguales.
    """
    validos = []
    rechazos = []
    vistos = set()
    for expediente in expedientes:
        problemas = revisar_expediente(expediente)
        codigo = expediente.get("codigo", "")
        if codigo in vistos:
            problemas.append("codigo repetido")
        if problemas:
            rechazos.append({"codigo": codigo, "motivo": ", ".join(problemas)})
            continue
        vistos.add(codigo)
        validos.append(expediente)
    return validos, rechazos


def resumir_rechazos(rechazos):
    """Retorna el texto que avisa que expedientes deben corregirse y por que."""
    if not rechazos:
        return ""
    detalles = []
    for rechazo in rechazos[:MAXIMO_DETALLES]:
        detalles.append(rechazo["codigo"] + " (" + rechazo["motivo"] + ")")
    if len(rechazos) == 1:
        resumen = "1 expediente tiene datos invalidos y debe corregirse: "
    else:
        resumen = (str(len(rechazos))
                   + " expedientes tienen datos invalidos y deben corregirse: ")
    resumen = resumen + "; ".join(detalles)
    restantes = len(rechazos) - MAXIMO_DETALLES
    if restantes > 0:
        resumen = resumen + "; y " + str(restantes) + " mas"
    return resumen
