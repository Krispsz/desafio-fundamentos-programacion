def validar_datos(nombre, dni, asunto):
    """Retorna True si los datos son validos, False si no.
    Reglas: nombre no vacio, dni tiene exactamente 8 caracteres, asunto no vacio.
    """
    def validar_datos(nombre, dni, asunto):
    if not nombre:
        return False
    if len(dni) != 8:
        return False
    if not asunto:
        return False
    return True
    # TODO (Cristobal)
    pass
