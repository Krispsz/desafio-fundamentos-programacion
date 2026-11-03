"""Pruebas de autenticacion.py con un usuarios.txt guardado con BOM.

El Bloc de notas de Windows agrega un BOM al guardar; pegado al primer
usuario, ese usuario ya no podia entrar. Todo se hace en una carpeta temporal.
"""

import os
import tempfile
import unittest

from autenticacion import agregar_usuario, verificar_login


class PruebasUsuariosConBom(unittest.TestCase):

    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.anterior = os.getcwd()
        os.chdir(self.carpeta.name)
        self.ruta = os.path.join(self.carpeta.name, "usuarios.txt")
        agregar_usuario("admin", "admin123", "administrador", self.ruta)
        agregar_usuario("jmesa", "mesa2026", "usuario", self.ruta)
        with open(self.ruta, "rb") as archivo:
            contenido = archivo.read()
        with open(self.ruta, "wb") as archivo:
            archivo.write(b"\xef\xbb\xbf" + contenido)

    def tearDown(self):
        os.chdir(self.anterior)
        self.carpeta.cleanup()

    def test_primer_usuario_entra_aunque_el_archivo_tenga_bom(self):
        self.assertEqual(verificar_login("admin", "admin123", self.ruta),
                         (True, "administrador"))

    def test_los_demas_usuarios_siguen_entrando(self):
        self.assertEqual(verificar_login("jmesa", "mesa2026", self.ruta), (True, "usuario"))

    def test_clave_incorrecta_sigue_fallando(self):
        self.assertEqual(verificar_login("admin", "otra", self.ruta), (False, ""))


if __name__ == "__main__":
    unittest.main()
