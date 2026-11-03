"""Tabla de expedientes dentro de la ventana: listar, buscar, ordenar y eliminar.

La logica no se copia: las filas se arman con construir_matriz(), la busqueda
usa buscar_por_texto(), el orden usa ordenar_con_burbuja() y la eliminacion
usa eliminar_por_codigo() de procesamiento.py. Este modulo solo dibuja.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from procesamiento import (ENCABEZADOS, buscar_por_texto, construir_matriz,
                           eliminar_por_codigo, ordenar_con_burbuja,
                           validar_busqueda)

COLUMNAS = ("codigo", "nombre", "dni", "asunto", "fecha", "estado", "dependencia")

ANCHOS = (90, 140, 95, 250, 95, 100, 150)

CRITERIOS = ("codigo", "nombre", "dni", "asunto", "fecha")


def preparar_filas(expedientes, texto, campo):
    """Retorna (filas, aviso): las filas de 7 datos para la tabla y el aviso
    correspondiente (None, "Busqueda invalida" o "Sin coincidencias")."""
    if campo not in ("nombre", "asunto"):
        return [], "Busqueda invalida"
    if texto == "":
        return construir_matriz(expedientes)[1:], None
    encontrados = buscar_por_texto(expedientes, campo, texto)
    if len(encontrados) == 0:
        return [], "Sin coincidencias"
    return construir_matriz(encontrados)[1:], None


def confirmar(codigo):
    """Pregunta si se elimina el expediente; retorna True o False."""
    return messagebox.askyesno("Eliminar", "Eliminar el expediente " + codigo + "?")


def abrir_detalle(contenedor, expedientes, codigo, usuario, rol):
    """Reemplaza la tabla por el detalle del expediente elegido."""
    import gui
    gui.limpiar(contenedor)
    gui.mostrar_detalle(contenedor, expedientes, codigo, usuario, rol)


def mostrar_tabla(contenedor, expedientes, usuario, rol):
    """Dibuja dentro de contenedor el buscador, el orden y la tabla con filas.

    La lista expedientes se modifica en el lugar: se ordena y se le quitan
    elementos con eliminar_por_codigo(), que ademas guarda el archivo.
    """
    vista = {"texto": "", "campo": "nombre"}

    barra_busqueda = ttk.Frame(contenedor)
    barra_busqueda.pack(fill="x")
    ttk.Label(barra_busqueda, text="Buscar en (nombre/asunto):").pack(side="left")
    campo = ttk.Combobox(barra_busqueda, values=("nombre", "asunto"),
                         width=10, state="readonly")
    campo.set("nombre")
    campo.pack(side="left", padx=(5, 10))
    entrada = ttk.Entry(barra_busqueda, width=30)
    entrada.pack(side="left")

    barra_orden = ttk.Frame(contenedor)
    barra_orden.pack(fill="x", pady=(8, 0))
    ttk.Label(barra_orden, text="Ordenar por:").pack(side="left")
    criterio = ttk.Combobox(barra_orden, values=CRITERIOS, width=10, state="readonly")
    criterio.set("codigo")
    criterio.pack(side="left", padx=(5, 10))

    marco_tabla = ttk.Frame(contenedor)
    marco_tabla.pack(fill="both", expand=True, pady=(10, 0))
    tabla = ttk.Treeview(marco_tabla, columns=COLUMNAS, show="headings",
                         selectmode="browse")
    for columna in range(len(COLUMNAS)):
        tabla.heading(COLUMNAS[columna], text=ENCABEZADOS[columna])
        tabla.column(COLUMNAS[columna], width=ANCHOS[columna], anchor="w")
    scroll = ttk.Scrollbar(marco_tabla, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scroll.set)
    tabla.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    pie = ttk.Frame(contenedor)
    pie.pack(fill="x", pady=(10, 0))
    etiqueta_aviso = ttk.Label(pie, text="", foreground="#a40000")
    etiqueta_aviso.pack(side="left")

    def avisar(texto):
        """Deja el mensaje del momento en el pie de la tabla."""
        etiqueta_aviso.config(text=texto)

    def refrescar():
        """Vuelve a dibujar las filas de la busqueda activa."""
        filas, aviso = preparar_filas(expedientes, vista["texto"], vista["campo"])
        for item in tabla.get_children():
            tabla.delete(item)
        for fila in filas:
            # Un codigo repetido (la integridad lo conserva) no puede ser iid
            # dos veces: la segunda fila recibe el iid que genere Tkinter.
            if tabla.exists(fila[0]):
                tabla.insert("", tk.END, values=fila)
            else:
                tabla.insert("", tk.END, iid=fila[0], values=fila)
        avisar(aviso if aviso is not None else "")

    def buscar(evento=None):
        """Aplica lo escrito en el campo o avisa si la busqueda no es valida."""
        texto = entrada.get().strip()
        if not validar_busqueda(campo.get(), texto):
            avisar("Busqueda invalida")
            return
        vista["texto"] = texto
        vista["campo"] = campo.get()
        refrescar()

    def ver_todos():
        """Quita el filtro de busqueda y vuelve a mostrar todas las filas."""
        entrada.delete(0, tk.END)
        vista["texto"] = ""
        refrescar()

    def ordenar():
        """Ordena la lista principal en el lugar y redibuja la vista."""
        if ordenar_con_burbuja(expedientes, criterio.get()) is None:
            avisar("Criterio invalido.")
            return
        refrescar()

    def eliminar():
        """Pide confirmacion y quita el expediente elegido con eliminar_por_codigo()."""
        seleccion = tabla.selection()
        if len(seleccion) == 0:
            avisar("Seleccione un expediente para eliminar")
            return
        codigo = tabla.set(seleccion[0], "codigo")
        if not confirmar(codigo):
            return
        eliminado, guardado = eliminar_por_codigo(expedientes, codigo)
        refrescar()
        if not eliminado:
            avisar("Expediente no encontrado")
        elif not guardado:
            avisar("No se pudo guardar en expedientes.txt. Revise el archivo.")
        else:
            avisar("Expediente " + codigo + " eliminado.")

    def doble_clic(evento):
        """Abre el detalle del expediente de la fila elegida."""
        seleccion = tabla.selection()
        if len(seleccion) > 0:
            abrir_detalle(contenedor, expedientes, tabla.set(seleccion[0], "codigo"),
                          usuario, rol)

    ttk.Button(barra_busqueda, text="Buscar", command=buscar).pack(side="left",
                                                                   padx=(8, 0))
    ttk.Button(barra_busqueda, text="Ver todos", command=ver_todos).pack(side="left",
                                                                         padx=(5, 0))
    ttk.Button(barra_orden, text="Ordenar", command=ordenar).pack(side="left")
    if rol == "administrador":
        ttk.Button(pie, text="Eliminar", command=eliminar).pack(side="right")
    tabla.bind("<Double-1>", doble_clic)
    entrada.bind("<Return>", buscar)
    entrada.focus()
    refrescar()
