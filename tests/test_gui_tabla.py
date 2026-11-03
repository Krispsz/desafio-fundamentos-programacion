"""Pruebas de gui_tabla.py: logica de filas y dibujo de la tabla en la ventana."""

import os
import tempfile
import unittest

import persistencia
from expediente import crear_expediente

try:
    import tkinter as tk
    import gui
    import gui_tabla
except Exception:
    tk = None
    gui = None
    gui_tabla = None


def datos_de_prueba():
    """Tres expedientes de ejemplo, uno con asunto mas largo de 25 caracteres."""
    return [
        crear_expediente("EXP-0001", "Juan Perez", "30112233", "Licencia", "2026-10-20"),
        crear_expediente("EXP-0002", "Maria Lopez", "28455666", "Constancia de deuda",
                         "2026-10-21", "En proceso", "Rentas"),
        crear_expediente("EXP-0003", "Carlos Ruiz", "33122004",
                         "Reclamo por bache en la avenida principal", "2026-10-22"),
    ]


class PruebasDeLogicaDeFilas(unittest.TestCase):
    """preparar_filas decide que mostrar sin crear widgets."""

    def setUp(self):
        if gui_tabla is None:
            self.skipTest("tkinter no disponible")

    def test_sin_texto_muestra_todas_las_filas(self):
        filas, aviso = gui_tabla.preparar_filas(datos_de_prueba(), "", "nombre")
        self.assertIsNone(aviso)
        self.assertEqual(len(filas), 3)

    def test_campo_invalido_avisa_busqueda_invalida(self):
        filas, aviso = gui_tabla.preparar_filas(datos_de_prueba(), "juan", "codigo")
        self.assertEqual(aviso, "Busqueda invalida")
        self.assertEqual(filas, [])

    def test_texto_vacio_tras_validar_no_esta_permitido(self):
        filas, aviso = gui_tabla.preparar_filas(datos_de_prueba(), "", "codigo")
        self.assertEqual(aviso, "Busqueda invalida")
        self.assertEqual(filas, [])

    def test_sin_coincidencias_avisa(self):
        filas, aviso = gui_tabla.preparar_filas(datos_de_prueba(), "zzz", "nombre")
        self.assertEqual(aviso, "Sin coincidencias")
        self.assertEqual(filas, [])

    def test_lista_vacia_con_texto_avisa_sin_coincidencias(self):
        filas, aviso = gui_tabla.preparar_filas([], "juan", "nombre")
        self.assertEqual(aviso, "Sin coincidencias")
        self.assertEqual(filas, [])

    def test_filtra_por_nombre_sin_distinguir_mayusculas(self):
        filas, aviso = gui_tabla.preparar_filas(datos_de_prueba(), "MARIA", "nombre")
        self.assertIsNone(aviso)
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0][0], "EXP-0002")

    def test_filtra_por_asunto_y_corta_el_largo(self):
        filas, aviso = gui_tabla.preparar_filas(datos_de_prueba(), "avenida", "asunto")
        self.assertIsNone(aviso)
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0][3], "Reclamo por bache en l...")
        self.assertEqual(len(filas[0]), 7)

    def test_las_filas_tienen_los_siete_datos(self):
        filas, aviso = gui_tabla.preparar_filas(datos_de_prueba(), "", "nombre")
        self.assertEqual(filas[0],
                         ["EXP-0001", "Juan Perez", "30112233", "Licencia",
                          "2026-10-20", "Recibido", "Mesa de Partes"])


class PruebasDeVentana(unittest.TestCase):
    """mostrar_tabla dibuja dentro del contenedor y respeta el rol."""

    def setUp(self):
        if gui_tabla is None:
            self.skipTest("tkinter no disponible")
        try:
            self.raiz = tk.Tk()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.raiz.withdraw()
        self.carpeta = tempfile.TemporaryDirectory()
        self.anterior = os.getcwd()
        os.chdir(self.carpeta.name)
        self.almacen = persistencia.ALMACENAMIENTO
        persistencia.ALMACENAMIENTO = "txt"
        self.expedientes = datos_de_prueba()

    def tearDown(self):
        persistencia.ALMACENAMIENTO = self.almacen
        os.chdir(self.anterior)
        self.carpeta.cleanup()
        self.raiz.destroy()

    def widgets(self, clase, texto=None):
        """Devuelve los widgets de la jerarquia que coinciden con clase y texto."""
        encontrados = []
        pendientes = [self.raiz]
        while pendientes:
            actual = pendientes.pop()
            for hijo in actual.winfo_children():
                if hijo.__class__.__name__ == clase and (
                        texto is None or hijo.cget("text") == texto):
                    encontrados.append(hijo)
                pendientes.append(hijo)
        return encontrados

    def etiquetas(self):
        return [etiqueta.cget("text") for etiqueta in self.widgets("Label")]

    def boton(self, texto):
        encontrados = self.widgets("Button", texto)
        if len(encontrados) == 0:
            return None
        return encontrados[0]

    def combo_campo(self):
        """El combo del campo de busqueda es el unico cuyos valores no traen dni."""
        for combo in self.widgets("Combobox"):
            if "dni" not in str(combo.cget("values")):
                return combo
        return None

    def dibujar(self, rol):
        gui_tabla.mostrar_tabla(self.raiz, self.expedientes, "admin", rol)
        return self.widgets("Treeview")[0]

    def test_dibuja_una_tabla_dentro_del_contenedor(self):
        tabla = self.dibujar("administrador")
        self.assertEqual(len(tabla.get_children()), 3)
        self.assertEqual(tabla["columns"],
                         ("codigo", "nombre", "dni", "asunto", "fecha",
                          "estado", "dependencia"))
        self.assertEqual(tabla.item("EXP-0001", "values")[1], "Juan Perez")
        self.assertEqual(len(self.widgets("Toplevel")), 0)

    def test_el_boton_eliminar_solo_existe_para_administrador(self):
        self.dibujar("usuario")
        self.assertIsNone(self.boton("Eliminar"))
        self.raiz.destroy()
        self.raiz = tk.Tk()
        self.raiz.withdraw()
        self.dibujar("administrador")
        self.assertIsNotNone(self.boton("Eliminar"))

    def test_eliminar_sin_seleccion_pide_elegir_un_expediente(self):
        tabla = self.dibujar("administrador")
        self.boton("Eliminar").invoke()
        self.assertIn("Seleccione un expediente para eliminar", self.etiquetas())
        self.assertEqual(len(self.expedientes), 3)
        self.assertEqual(len(tabla.get_children()), 3)

    def test_eliminar_quita_de_la_lista_y_guarda_el_archivo(self):
        tabla = self.dibujar("administrador")
        tabla.selection_set("EXP-0002")
        self.boton("Eliminar").invoke()
        self.assertEqual(len(self.expedientes), 2)
        self.assertEqual([e["codigo"] for e in self.expedientes],
                         ["EXP-0001", "EXP-0003"])
        self.assertNotIn("EXP-0002", tabla.get_children())
        self.assertIn("Expediente EXP-0002 eliminado.", self.etiquetas())
        self.assertEqual(len(persistencia.cargar_desde_archivo()), 2)

    def test_codigos_repetidos_no_impiden_dibujar_la_tabla(self):
        self.expedientes.append(crear_expediente("EXP-0002", "Rosa Diaz", "41122334",
                                                 "Duplicado", "2026-10-23"))
        tabla = self.dibujar("administrador")
        self.assertEqual(len(tabla.get_children()), 4)
        codigos = [tabla.set(item, "codigo") for item in tabla.get_children()]
        self.assertEqual(codigos.count("EXP-0002"), 2)

    def test_eliminar_codigo_repetido_lee_el_codigo_de_la_fila(self):
        self.expedientes.append(crear_expediente("EXP-0002", "Rosa Diaz", "41122334",
                                                 "Duplicado", "2026-10-23"))
        tabla = self.dibujar("administrador")
        tabla.selection_set(tabla.get_children()[3])
        self.boton("Eliminar").invoke()
        self.assertEqual(len(self.expedientes), 3)
        self.assertIn("Expediente EXP-0002 eliminado.", self.etiquetas())

    def test_buscar_filtra_las_filas(self):
        tabla = self.dibujar("administrador")
        self.combo_campo().set("asunto")
        entrada = self.widgets("Entry")[0]
        entrada.insert(0, "avenida")
        self.boton("Buscar").invoke()
        self.assertEqual(tabla.get_children(), ("EXP-0003",))

    def test_boton_buscar_sin_texto_avisa_busqueda_invalida(self):
        tabla = self.dibujar("administrador")
        self.boton("Buscar").invoke()
        self.assertIn("Busqueda invalida", self.etiquetas())
        self.assertEqual(len(tabla.get_children()), 3)

    def test_ordenar_reordena_la_lista_y_conserva_el_filtro(self):
        datos = datos_de_prueba()
        self.expedientes = [datos[2], datos[0], datos[1]]
        tabla = self.dibujar("administrador")
        self.combo_campo().set("asunto")
        entrada = self.widgets("Entry")[0]
        entrada.insert(0, "avenida")
        self.boton("Buscar").invoke()
        self.assertEqual(tabla.get_children(), ("EXP-0003",))
        self.assertEqual([e["codigo"] for e in self.expedientes],
                         ["EXP-0003", "EXP-0001", "EXP-0002"])
        self.boton("Ordenar").invoke()
        self.assertEqual([e["codigo"] for e in self.expedientes],
                         ["EXP-0001", "EXP-0002", "EXP-0003"])
        self.assertEqual(tabla.get_children(), ("EXP-0003",))

    def test_doble_clic_esta_enganchado_en_la_tabla(self):
        tabla = self.dibujar("administrador")
        self.assertNotIn(tabla.bind("<Double-1>"), ("", None))

    def test_abrir_detalle_reemplaza_la_tabla_por_el_detalle(self):
        self.dibujar("administrador")
        capturas = []
        original = gui.mostrar_detalle
        gui.mostrar_detalle = lambda contenedor, expedientes, codigo, usuario, rol: \
            capturas.append((codigo, usuario, rol))
        try:
            gui_tabla.abrir_detalle(self.raiz, self.expedientes, "EXP-0001",
                                    "admin", "administrador")
        finally:
            gui.mostrar_detalle = original
        self.assertEqual(capturas, [("EXP-0001", "admin", "administrador")])
        self.assertEqual(self.widgets("Treeview"), [])


if __name__ == "__main__":
    unittest.main()
