"""Pruebas de crear_cuenta() y del boton Usuarios de la GUI.

Todo se hace en una carpeta temporal: nunca se toca el usuarios.txt real.
"""

import os
import tempfile
import unittest
from unittest import mock

import persistencia
from autenticacion import (LONGITUD_MINIMA, ROLES, agregar_usuario, crear_cuenta,
                           leer_usuarios, verificar_login)

try:
    import tkinter as tk
    import gui
except Exception:
    tk = None
    gui = None


class PruebasCrearCuenta(unittest.TestCase):
    """Cada regla de crear_cuenta(), en el orden en que se revisan."""

    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.ruta = os.path.join(self.carpeta.name, "usuarios.txt")
        agregar_usuario("admin", "admin123", "administrador", self.ruta)

    def tearDown(self):
        self.carpeta.cleanup()

    def crear(self, usuario, clave, confirmacion, rol):
        return crear_cuenta(usuario, clave, confirmacion, rol, self.ruta)

    def test_constantes(self):
        self.assertEqual(ROLES, ["administrador", "usuario"])
        self.assertEqual(LONGITUD_MINIMA, 6)

    def test_usuario_vacio_es_invalido(self):
        self.assertEqual(self.crear("", "clave01", "clave01", "usuario"),
                         (False, "Usuario invalido"))
        self.assertEqual(self.crear("   ", "clave01", "clave01", "usuario"),
                         (False, "Usuario invalido"))

    def test_usuario_con_separador_es_invalido(self):
        self.assertEqual(self.crear("ana|x", "clave01", "clave01", "usuario"),
                         (False, "Usuario invalido"))

    def test_contrasenas_distintas(self):
        self.assertEqual(self.crear("prueba01", "clave01", "clave02", "usuario"),
                         (False, "Las contrasenas no coinciden"))

    def test_contrasena_corta(self):
        self.assertEqual(self.crear("prueba01", "abc12", "abc12", "usuario"),
                         (False, "La contrasena debe tener al menos 6 caracteres"))

    def test_rol_invalido(self):
        self.assertEqual(self.crear("prueba01", "clave01", "clave01", "jefe"),
                         (False, "Rol invalido"))

    def test_usuario_existente_sin_distinguir_mayusculas(self):
        self.assertEqual(self.crear("ADMIN", "clave01", "clave01", "usuario"),
                         (False, "El usuario ya existe"))

    def test_cuenta_correcta_se_crea(self):
        self.assertEqual(self.crear("prueba01", "clave01", "clave01", "usuario"),
                         (True, "Cuenta creada"))

    def test_si_agregar_usuario_falla_no_se_crea(self):
        # La clave con | pasa las reglas de crear_cuenta, pero agregar_usuario la rechaza
        self.assertEqual(self.crear("prueba01", "clave|01", "clave|01", "usuario"),
                         (False, "No se pudo crear la cuenta"))
        self.assertEqual(len(leer_usuarios(self.ruta)), 1)

    def test_las_reglas_se_revisan_en_orden(self):
        self.assertEqual(self.crear("", "a", "b", "jefe"), (False, "Usuario invalido"))
        self.assertEqual(self.crear("admin", "a", "b", "jefe"),
                         (False, "Las contrasenas no coinciden"))
        self.assertEqual(self.crear("admin", "a", "a", "jefe"),
                         (False, "La contrasena debe tener al menos 6 caracteres"))
        self.assertEqual(self.crear("admin", "clave01", "clave01", "jefe"),
                         (False, "Rol invalido"))

    def test_cuenta_rechazada_no_se_guarda(self):
        self.crear("prueba01", "clave01", "clave02", "usuario")
        self.assertEqual([u["usuario"] for u in leer_usuarios(self.ruta)], ["admin"])

    def test_cuenta_creada_puede_entrar_con_su_rol(self):
        self.crear("prueba01", "clave01", "clave01", "usuario")
        self.crear("jefa01", "secreta9", "secreta9", "administrador")
        self.assertEqual(verificar_login("prueba01", "clave01", self.ruta), (True, "usuario"))
        self.assertEqual(verificar_login("jefa01", "secreta9", self.ruta),
                         (True, "administrador"))
        self.assertEqual(verificar_login("prueba01", "otra01", self.ruta), (False, ""))

    def test_se_guarda_sal_y_hash_nunca_la_contrasena(self):
        self.crear("prueba01", "clave01", "clave01", "usuario")
        with open(self.ruta, encoding="utf-8") as archivo:
            contenido = archivo.read()
        self.assertNotIn("clave01", contenido)
        linea = contenido.strip().splitlines()[-1]
        usuario, sal, hash_guardado, rol = linea.split("|")
        self.assertEqual((usuario, rol), ("prueba01", "usuario"))
        self.assertEqual(len(sal), 16)
        self.assertEqual(len(hash_guardado), 64)


class PruebasBotonUsuarios(unittest.TestCase):
    """El boton Usuarios del menu solo aparece para el administrador."""

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

    def campos_del_formulario(self):
        """Usuario, Contrasena y Confirmar contrasena, en el orden de sus filas."""
        entradas = []
        for fila in (1, 2, 3):
            for entrada in self.widgets("Entry"):
                if int(entrada.grid_info()["row"]) == fila:
                    entradas.append(entrada)
        return entradas

    def test_administrador_ve_el_boton_usuarios(self):
        gui.crear_ventana_principal(self.raiz, "admin", "administrador")
        self.assertEqual(len(self.widgets("Button", "Usuarios")), 1)

    def test_usuario_no_ve_el_boton_usuarios(self):
        gui.crear_ventana_principal(self.raiz, "jmesa", "usuario")
        self.assertEqual(self.widgets("Button", "Usuarios"), [])
        self.assertEqual(len(self.widgets("Button", "Registrar")), 1)

    def test_el_boton_muestra_el_formulario_y_crea_la_cuenta(self):
        gui.crear_ventana_principal(self.raiz, "admin", "administrador")
        self.widgets("Button", "Usuarios")[0].invoke()
        self.assertEqual(len(self.widgets("Button", "Crear cuenta")), 1)
        combo = self.widgets("Combobox")[0]
        self.assertEqual(str(combo.cget("state")), "readonly")
        self.assertEqual(list(combo.cget("values")), ROLES)
        usuario, clave, confirmacion = self.campos_del_formulario()
        self.assertEqual((clave.cget("show"), confirmacion.cget("show")), ("*", "*"))
        usuario.insert(0, "prueba01")
        clave.insert(0, "clave01")
        confirmacion.insert(0, "clave01")
        combo.set("usuario")
        with mock.patch.object(gui.messagebox, "showinfo") as aviso:
            self.widgets("Button", "Crear cuenta")[0].invoke()
        aviso.assert_called_once_with("Crear usuario", "Cuenta creada")
        self.assertEqual(usuario.get(), "")
        self.assertEqual(verificar_login("prueba01", "clave01"), (True, "usuario"))

    def test_formulario_con_error_avisa_el_motivo(self):
        gui.crear_ventana_principal(self.raiz, "admin", "administrador")
        self.widgets("Button", "Usuarios")[0].invoke()
        entradas = self.campos_del_formulario()
        entradas[0].insert(0, "prueba01")
        entradas[1].insert(0, "clave01")
        entradas[2].insert(0, "clave02")
        with mock.patch.object(gui.messagebox, "showwarning") as aviso:
            self.widgets("Button", "Crear cuenta")[0].invoke()
        aviso.assert_called_once_with("Crear usuario", "Las contrasenas no coinciden")
        self.assertEqual(entradas[0].get(), "prueba01")
        self.assertFalse(os.path.exists("usuarios.txt"))


if __name__ == "__main__":
    unittest.main()
