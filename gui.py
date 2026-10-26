"""Interfaz grafica (tkinter) de la Mesa de Partes Digital.

Convencion: este archivo es la capa grafica (aqui van los widgets); la logica
se reutiliza de los otros modulos, igual que en la version de consola.
Ejecucion: python gui.py
"""

import tkinter as tk
from tkinter import ttk, messagebox

from autenticacion import verificar_login
from expediente import DEPENDENCIAS
from persistencia import cargar_desde_archivo, guardar_en_archivo
from registro import preparar_datos, crear_registro

# La tabla de expedientes (tarea 13) va en gui_tabla.py. Mientras no exista,
# el boton "Listar / Buscar" muestra un aviso.
try:
    from gui_tabla import mostrar_tabla
except ImportError:
    mostrar_tabla = None

MAX_INTENTOS = 3

TITULO = "Mesa de Partes Digital"

REGLAS = ("Revise los datos:\n"
          "- Nombre y asunto no pueden estar vacios.\n"
          "- Nombre y asunto no pueden contener el caracter |.\n"
          "- El DNI debe tener exactamente 8 digitos.")


def limpiar(contenedor):
    """Destruye todos los widgets que hay dentro del contenedor."""
    for widget in contenedor.winfo_children():
        widget.destroy()


def crear_ventana_login(ventana, al_ingresar):
    """Dibuja el inicio de sesion dentro de ventana.

    Permite MAX_INTENTOS intentos. Si el acceso es correcto llama a
    al_ingresar(usuario, rol); al ultimo fallo avisa y cierra la ventana.
    """
    ventana.title(TITULO + " - Inicio de sesion")
    ventana.resizable(False, False)
    intentos = {"fallidos": 0}

    marco = ttk.Frame(ventana, padding=20)
    marco.pack()
    ttk.Label(marco, text=TITULO, font=("Segoe UI", 14, "bold")).grid(
        row=0, column=0, columnspan=2, pady=(0, 15))
    ttk.Label(marco, text="Usuario:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    entrada_usuario = ttk.Entry(marco, width=25)
    entrada_usuario.grid(row=1, column=1, pady=5)
    ttk.Label(marco, text="Contrasena:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    entrada_clave = ttk.Entry(marco, width=25, show="*")
    entrada_clave.grid(row=2, column=1, pady=5)
    mensaje = ttk.Label(marco, text="", foreground="red")
    mensaje.grid(row=4, column=0, columnspan=2, pady=(10, 0))

    def ingresar(evento=None):
        """Verifica el usuario y la contrasena escritos en el formulario."""
        usuario = entrada_usuario.get().strip()
        valido, rol = verificar_login(usuario, entrada_clave.get())
        if valido:
            al_ingresar(usuario.lower(), rol)
            return
        intentos["fallidos"] = intentos["fallidos"] + 1
        if intentos["fallidos"] >= MAX_INTENTOS:
            messagebox.showerror("Acceso bloqueado",
                                 "Se agotaron los " + str(MAX_INTENTOS) + " intentos.")
            ventana.destroy()
            return
        mensaje.config(text="Usuario o contrasena incorrectos. Intentos restantes: "
                       + str(MAX_INTENTOS - intentos["fallidos"]))
        entrada_clave.delete(0, tk.END)
        entrada_clave.focus()

    ttk.Button(marco, text="Ingresar", command=ingresar).grid(
        row=3, column=0, columnspan=2, pady=(10, 0))
    # La tecla Enter tambien envia el formulario
    entrada_usuario.bind("<Return>", ingresar)
    entrada_clave.bind("<Return>", ingresar)
    entrada_usuario.focus()


def procesar_registro(expedientes, nombre, dni, asunto, dependencia, usuario):
    """Valida con preparar_datos() y crea el expediente con crear_registro().

    Retorna lo mismo que crear_registro(): la tupla (codigo, guardado), con el
    codigo asignado y si el guardado tuvo exito; o None si los datos no son validos.
    """
    datos = preparar_datos(nombre, dni, asunto)
    if datos is None:
        return None
    return crear_registro(expedientes, datos[0], datos[1], datos[2], dependencia, usuario)


def mostrar_formulario_registro(contenedor, expedientes, usuario):
    """Dibuja el formulario de registro dentro de contenedor.

    El boton Registrar usa procesar_registro(): si los datos son invalidos
    muestra las reglas; si son validos muestra el codigo y limpia el formulario.
    """
    ttk.Label(contenedor, text="Registrar expediente", font=("Segoe UI", 12, "bold")).grid(
        row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
    ttk.Label(contenedor, text="Nombre:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    entrada_nombre = ttk.Entry(contenedor, width=40)
    entrada_nombre.grid(row=1, column=1, sticky="w", pady=5)
    ttk.Label(contenedor, text="DNI:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    entrada_dni = ttk.Entry(contenedor, width=15)
    entrada_dni.grid(row=2, column=1, sticky="w", pady=5)
    ttk.Label(contenedor, text="Asunto:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    entrada_asunto = ttk.Entry(contenedor, width=40)
    entrada_asunto.grid(row=3, column=1, sticky="w", pady=5)
    ttk.Label(contenedor, text="Dependencia:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
    combo_dependencia = ttk.Combobox(contenedor, values=DEPENDENCIAS, state="readonly", width=25)
    combo_dependencia.current(0)
    combo_dependencia.grid(row=4, column=1, sticky="w", pady=5)

    def registrar():
        """Lee el formulario, registra el expediente y muestra el resultado."""
        resultado = procesar_registro(expedientes, entrada_nombre.get(), entrada_dni.get(),
                                      entrada_asunto.get(), combo_dependencia.get(), usuario)
        if resultado is None:
            messagebox.showwarning("Datos invalidos", REGLAS)
            return
        codigo, guardado = resultado
        messagebox.showinfo("Registro", "Expediente registrado con codigo " + codigo)
        if not guardado:
            messagebox.showerror("Error", "El expediente se registro pero no se pudo guardar.")
        entrada_nombre.delete(0, tk.END)
        entrada_dni.delete(0, tk.END)
        entrada_asunto.delete(0, tk.END)
        combo_dependencia.current(0)
        entrada_nombre.focus()

    ttk.Button(contenedor, text="Registrar", command=registrar).grid(
        row=5, column=1, sticky="w", pady=(10, 0))
    entrada_nombre.focus()


def crear_ventana_principal(ventana, usuario, rol):
    """Dibuja la ventana principal dentro de ventana y carga los expedientes.

    A la izquierda van los botones del menu y a la derecha area_contenido,
    donde se muestra cada vista. Al salir (boton o X) guarda los expedientes.
    Retorna area_contenido.
    """
    ventana.title(TITULO)
    ventana.resizable(True, True)
    ventana.geometry("900x500")
    expedientes = cargar_desde_archivo()

    encabezado = ttk.Frame(ventana, padding=(10, 8))
    encabezado.pack(side="top", fill="x")
    ttk.Label(encabezado, text=TITULO, font=("Segoe UI", 14, "bold")).pack(side="left")
    ttk.Label(encabezado, text="Usuario: " + usuario + " (" + rol + ")").pack(side="right")
    ttk.Separator(ventana, orient="horizontal").pack(side="top", fill="x")

    menu = ttk.Frame(ventana, padding=10)
    menu.pack(side="left", fill="y")
    ttk.Separator(ventana, orient="vertical").pack(side="left", fill="y")
    area_contenido = ttk.Frame(ventana, padding=15)
    area_contenido.pack(side="left", fill="both", expand=True)

    def ver_registro():
        """Muestra el formulario de registro en area_contenido."""
        limpiar(area_contenido)
        mostrar_formulario_registro(area_contenido, expedientes, usuario)

    def ver_listado():
        """Muestra la tabla de expedientes (gui_tabla.py) en area_contenido."""
        limpiar(area_contenido)
        if mostrar_tabla is None:
            ttk.Label(area_contenido,
                      text="Tabla de expedientes: en desarrollo (tarea 13)").pack(anchor="nw")
            return
        mostrar_tabla(area_contenido, expedientes, usuario, rol)

    def salir():
        """Guarda los expedientes, avisa si falla y cierra la ventana."""
        if not guardar_en_archivo(expedientes):
            messagebox.showerror("Error", "No se pudieron guardar los datos.")
        ventana.destroy()

    ttk.Button(menu, text="Registrar", width=18, command=ver_registro).pack(pady=4)
    ttk.Button(menu, text="Listar / Buscar", width=18, command=ver_listado).pack(pady=4)
    ttk.Button(menu, text="Salir", width=18, command=salir).pack(pady=4)
    ventana.protocol("WM_DELETE_WINDOW", salir)

    ttk.Label(area_contenido, text="Bienvenido, " + usuario + ". Expedientes cargados: "
              + str(len(expedientes)) + ".").pack(anchor="nw")
    ttk.Label(area_contenido, text="Elija una opcion del menu de la izquierda.").pack(anchor="nw")
    return area_contenido


def iniciar_gui():
    """Abre el inicio de sesion y, si el acceso es correcto, la ventana principal."""
    ventana = tk.Tk()

    def al_ingresar(usuario, rol):
        """Reemplaza el inicio de sesion por la ventana principal."""
        limpiar(ventana)
        crear_ventana_principal(ventana, usuario, rol)

    crear_ventana_login(ventana, al_ingresar)
    ventana.mainloop()


if __name__ == "__main__":
    iniciar_gui()
