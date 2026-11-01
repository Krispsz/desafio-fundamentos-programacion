"""Pruebas de cambiar_estado(): cambio de estado e historial (tareas 09 y 07)."""

import os
import tempfile
import unittest
from datetime import date

import integridad
import persistencia
from expediente import crear_expediente
from registro import cambiar_estado

try:
    import tkinter as tk
    import gui
except Exception:
    tk = None
    gui = None


def crear_uno():
    """Un expediente con el historial inicial que crea crear_expediente()."""
    return crear_expediente("EXP-0001", "Juan Perez", "30112233",
                            "Licencia de funcionamiento", "2026-10-20")


class PruebasCambiarEstado(unittest.TestCase):
    """cambiar_estado actualiza el estado, el historial y el archivo."""

    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.anterior = os.getcwd()
        os.chdir(self.carpeta.name)
        self.almacen = persistencia.ALMACENAMIENTO
        persistencia.ALMACENAMIENTO = "txt"
        self.expedientes = [crear_uno()]

    def tearDown(self):
        persistencia.ALMACENAMIENTO = self.almacen
        os.chdir(self.anterior)
        self.carpeta.cleanup()

    def test_cambia_el_estado_y_agrega_una_entrada_al_historial(self):
        cambio, guardado = cambiar_estado(self.expedientes, "EXP-0001",
                                          "En proceso", "admin")
        self.assertTrue(cambio)
        self.assertTrue(guardado)
        self.assertEqual(self.expedientes[0]["estado"], "En proceso")
        self.assertEqual(len(self.expedientes[0]["historial"]), 2)
        self.assertEqual(self.expedientes[0]["historial"][1],
                         {"fecha": date.today().isoformat(),
                          "estado": "En proceso", "usuario": "admin"})

    def test_conserva_las_entradas_anteriores_del_historial(self):
        cambiar_estado(self.expedientes, "EXP-0001", "En proceso", "admin")
        cambiar_estado(self.expedientes, "EXP-0001", "Atendido", "jmesa")
        historial = self.expedientes[0]["historial"]
        self.assertEqual(len(historial), 3)
        self.assertEqual([entrada["estado"] for entrada in historial],
                         ["Recibido", "En proceso", "Atendido"])
        self.assertEqual(historial[0]["usuario"], "sistema")

    def test_guarda_el_estado_y_el_historial_en_el_archivo(self):
        cambiar_estado(self.expedientes, "EXP-0001", "En proceso", "admin")
        cargados = persistencia.cargar_desde_archivo()
        self.assertEqual(len(cargados), 1)
        self.assertEqual(cargados[0]["estado"], "En proceso")
        self.assertEqual(len(cargados[0]["historial"]), 2)
        self.assertEqual(cargados[0]["historial"][1]["estado"], "En proceso")
        self.assertEqual(cargados[0]["historial"][1]["usuario"], "admin")

    def test_codigo_inexistente_no_cambia_nada_ni_crea_el_archivo(self):
        cambio, guardado = cambiar_estado(self.expedientes, "EXP-9999",
                                          "Atendido", "admin")
        self.assertEqual((cambio, guardado), (False, False))
        self.assertEqual(self.expedientes[0]["estado"], "Recibido")
        self.assertEqual(len(self.expedientes[0]["historial"]), 1)
        self.assertFalse(os.path.exists("expedientes.txt"))

    def test_estado_desconocido_no_cambia_nada(self):
        cambio, guardado = cambiar_estado(self.expedientes, "EXP-0001",
                                          "Volando", "admin")
        self.assertEqual((cambio, guardado), (False, False))
        self.assertEqual(self.expedientes[0]["estado"], "Recibido")
        self.assertEqual(len(self.expedientes[0]["historial"]), 1)

    def test_mismo_estado_no_duplica_la_entrada(self):
        cambio, guardado = cambiar_estado(self.expedientes, "EXP-0001",
                                          "Recibido", "admin")
        self.assertEqual((cambio, guardado), (False, False))
        self.assertEqual(len(self.expedientes[0]["historial"]), 1)

    def test_usuario_vacio_no_cambia_nada(self):
        cambio, guardado = cambiar_estado(self.expedientes, "EXP-0001",
                                          "Atendido", "")
        self.assertEqual((cambio, guardado), (False, False))
        self.assertEqual(self.expedientes[0]["estado"], "Recibido")

    def test_el_expediente_sigue_integro_despues_del_cambio(self):
        cambiar_estado(self.expedientes, "EXP-0001", "Atendido", "admin")
        self.assertEqual(integridad.revisar_expediente(self.expedientes[0]), [])


class PruebasDetalleConCambioDeEstado(unittest.TestCase):
    """El detalle de la GUI muestra y aplica el cambio de estado."""

    def setUp(self):
        if gui is None:
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
        self.expedientes = [crear_uno()]

    def tearDown(self):
        persistencia.ALMACENAMIENTO = self.almacen
        os.chdir(self.anterior)
        self.carpeta.cleanup()
        self.raiz.destroy()

    def widgets(self, clase):
        """Devuelve los widgets de la jerarquia que son de esa clase."""
        encontrados = []
        pendientes = [self.raiz]
        while pendientes:
            actual = pendientes.pop()
            for hijo in actual.winfo_children():
                if hijo.__class__.__name__ == clase:
                    encontrados.append(hijo)
                pendientes.append(hijo)
        return encontrados

    def combo_estado(self):
        for combo in self.widgets("Combobox"):
            if "Recibido" in str(combo.cget("values")):
                return combo
        return None

    def boton_cambiar(self):
        for boton in self.widgets("Button"):
            if boton.cget("text") == "Cambiar estado":
                return boton
        return None

    def test_el_detalle_muestra_el_selector_y_el_boton(self):
        gui.mostrar_detalle(self.raiz, self.expedientes, "EXP-0001",
                            "admin", "administrador")
        self.assertIsNotNone(self.combo_estado())
        self.assertEqual(self.combo_estado().get(), "Recibido")
        self.assertIsNotNone(self.boton_cambiar())

    def test_cambiar_estado_desde_el_detalle_actualiza_y_guarda(self):
        original_info = gui.messagebox.showinfo
        original_error = gui.messagebox.showerror
        gui.messagebox.showinfo = lambda *args, **kwargs: None
        gui.messagebox.showerror = lambda *args, **kwargs: None
        try:
            gui.mostrar_detalle(self.raiz, self.expedientes, "EXP-0001",
                                "admin", "administrador")
            self.combo_estado().set("Atendido")
            self.boton_cambiar().invoke()
        finally:
            gui.messagebox.showinfo = original_info
            gui.messagebox.showerror = original_error
        self.assertEqual(self.expedientes[0]["estado"], "Atendido")
        self.assertEqual(len(self.expedientes[0]["historial"]), 2)
        cargados = persistencia.cargar_desde_archivo()
        self.assertEqual(cargados[0]["estado"], "Atendido")


if __name__ == "__main__":
    unittest.main()

