"""Pruebas de integracion de la consola: main.main() de principio a fin.

Cada prueba ejecuta el programa completo con entradas simuladas en una carpeta
temporal: nunca se tocan los usuarios.txt ni los expedientes.txt reales.

El menu definitivo es 9 = Salir y 10 = Crear usuario (solo administrador).
"""

import contextlib
import io
import os
import tempfile
import unittest
from datetime import date
from unittest import mock

import main
import persistencia
from autenticacion import agregar_usuario, leer_usuarios, verificar_login

HOY = date.today().isoformat()

# Un expediente valido en formato de 8 campos, con dos entradas de historial.
EN_PROCESO = ("EXP-0001|Juan Perez|12345678|Solicitud de licencia|2026-10-16|"
              "En proceso|Licencias|2026-10-16,Recibido,admin;"
              "2026-10-20,En proceso,jmesa\n")

# Tres expedientes con nombres desordenados a proposito.
TRES = ("EXP-0001|Juan Perez|12345678|Solicitud de licencia|2026-10-16\n"
        "EXP-0002|Maria Lopez|87654321|Reclamo de arbitrios|2026-10-17\n"
        "EXP-0003|Ana Diaz|11223344|Licencia de obra|2026-10-18\n")


class PruebasIntegracionConsola(unittest.TestCase):

    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.anterior = os.getcwd()
        os.chdir(self.carpeta.name)
        self.almacenamiento = persistencia.ALMACENAMIENTO
        persistencia.ALMACENAMIENTO = "txt"
        agregar_usuario("admin", "admin123", "administrador")
        agregar_usuario("jmesa", "mesa2026", "usuario")

    def tearDown(self):
        persistencia.ALMACENAMIENTO = self.almacenamiento
        os.chdir(self.anterior)
        self.carpeta.cleanup()

    def correr(self, entradas):
        """Ejecuta main.main() con esas entradas y retorna todo lo impreso."""
        pendientes = iter(entradas)

        def responder(pregunta=""):
            return next(pendientes)

        salida = io.StringIO()
        with mock.patch("builtins.input", responder), \
                mock.patch("getpass.getpass", responder), \
                contextlib.redirect_stdout(salida):
            main.main()
        return salida.getvalue()

    def escribir(self, contenido):
        """Escribe el expedientes.txt de la carpeta temporal."""
        with open("expedientes.txt", "w", encoding="utf-8") as archivo:
            archivo.write(contenido)

    def leer(self):
        """Contenido del expedientes.txt de la carpeta temporal."""
        with open("expedientes.txt", encoding="utf-8") as archivo:
            return archivo.read()

    # --- menu y opciones generales ---------------------------------------

    def test_menu_definitivo_con_9_salir_y_10_crear_usuario(self):
        salida = self.correr(["admin", "admin123", "9"])
        self.assertIn("9. Salir", salida)
        self.assertIn("10. Crear usuario (solo administrador)", salida)
        self.assertNotIn("Opcion invalida", salida)

    def test_opcion_fuera_del_menu_avisa(self):
        salida = self.correr(["admin", "admin123", "99", "9"])
        self.assertIn("Opcion invalida, intenta de nuevo.", salida)

    def test_lista_vacia_avisa_en_las_opciones_2_a_8(self):
        salida = self.correr(["admin", "admin123",
                              "2", "3", "4", "5", "6", "7", "8", "9"])
        self.assertEqual(salida.count("No hay expedientes registrados."), 7)

    def test_tres_fallos_bloquean_el_acceso(self):
        salida = self.correr(["admin", "x", "admin", "y", "jmesa", "z"])
        self.assertIn("Intentos restantes: 2", salida)
        self.assertIn("Intentos restantes: 1", salida)
        self.assertIn("Acceso bloqueado: se agotaron los 3 intentos.", salida)
        self.assertNotIn("--- Mesa de Partes Digital ---", salida)

    # --- sesion completa y persistencia ----------------------------------

    def test_sesion_completa_de_administrador(self):
        salida = self.correr(["admin", "admin123",
                              "1", "Ana Diaz", "11223344", "Licencia de obra", "4",
                              "7", "9"])
        self.assertIn("Bienvenido, admin (administrador)", salida)
        self.assertIn("Expediente registrado con codigo EXP-0001", salida)
        self.assertIn("Licencia de obra", salida)
        self.assertIn("Datos guardados. Hasta luego.", salida)
        campos = self.leer().strip().split("|")
        self.assertEqual(len(campos), 8)
        self.assertEqual(campos[:7], ["EXP-0001", "Ana Diaz", "11223344",
                                      "Licencia de obra", HOY, "Recibido", "Obras"])
        self.assertEqual(campos[7], HOY + ",Recibido,admin")

    def test_registro_rechaza_datos_invalidos_y_repite(self):
        salida = self.correr(["admin", "admin123", "1",
                              "Ana", "123", "Licencia",
                              "Ana Diaz", "11223344", "Licencia de obra", "4", "9"])
        self.assertIn("Datos invalidos, intente de nuevo.", salida)
        self.assertIn("Expediente registrado con codigo EXP-0001", salida)

    def test_lee_el_formato_viejo_de_5_campos_con_valores_por_defecto(self):
        # Un archivo de antes tiene 5 campos; al cargar se completan estado,
        # dependencia e historial, y al salir se guarda ya con 8 campos.
        self.escribir("EXP-0001|Juan Perez|12345678|Solicitud de licencia|2026-10-16\n")
        salida = self.correr(["admin", "admin123", "7", "9"])
        fila = [linea for linea in salida.splitlines() if "EXP-0001" in linea][0]
        self.assertIn("Recibido", fila)
        self.assertIn("Mesa de Partes", fila)
        campos = self.leer().strip().split("|")
        self.assertEqual(len(campos), 8)
        self.assertEqual(campos[5:7], ["Recibido", "Mesa de Partes"])
        self.assertEqual(campos[7], "2026-10-16,Recibido,sistema")

    def test_los_datos_sobreviven_entre_ejecuciones(self):
        self.correr(["admin", "admin123", "1", "Ana Diaz", "11223344",
                     "Licencia de obra", "4", "9"])
        salida = self.correr(["admin", "admin123", "7", "9"])
        self.assertIn("Expedientes cargados: 1", salida)
        self.assertIn("Ana Diaz", salida)
        self.assertIn("Licencia de obra", salida)

    def test_usuario_normal_puede_registrar(self):
        salida = self.correr(["jmesa", "mesa2026", "1", "Ana Diaz", "11223344",
                              "Licencia de obra", "4", "9"])
        self.assertIn("Expediente registrado con codigo EXP-0001", salida)
        self.assertIn(",Recibido,jmesa", self.leer())

    # --- crear usuarios (opcion 10) --------------------------------------

    def test_opcion_10_crea_usuario_aunque_no_haya_expedientes(self):
        salida = self.correr(["admin", "admin123", "10",
                              "prueba01", "clave01", "clave01", "2", "9"])
        self.assertIn("Expedientes cargados: 0", salida)
        self.assertIn("Cuenta creada", salida)
        roles = {u["usuario"]: u["rol"] for u in leer_usuarios()}
        self.assertEqual(roles.get("prueba01"), "usuario")
        with open("usuarios.txt", encoding="utf-8") as archivo:
            self.assertNotIn("clave01", archivo.read())

    def test_la_cuenta_creada_entra_despues_con_su_rol(self):
        self.correr(["admin", "admin123", "10",
                     "prueba01", "clave01", "clave01", "2", "9"])
        salida = self.correr(["prueba01", "clave01", "9"])
        self.assertIn("Bienvenido, prueba01 (usuario)", salida)

    def test_se_puede_crear_otro_administrador(self):
        salida = self.correr(["admin", "admin123", "10",
                              "jefa01", "secreta9", "secreta9", "1", "9"])
        self.assertIn("Cuenta creada", salida)
        self.assertEqual(verificar_login("jefa01", "secreta9"),
                         (True, "administrador"))

    def test_crear_usuario_repetido_avisa(self):
        salida = self.correr(["admin", "admin123", "10",
                              "admin", "clave01", "clave01", "1", "9"])
        self.assertIn("El usuario ya existe", salida)

    def test_usuario_no_puede_crear_ni_eliminar(self):
        # Con la lista vacia, la opcion 5 avisa "No hay expedientes" antes de
        # revisar el rol; se carga un expediente para llegar al bloqueo real.
        self.escribir(EN_PROCESO)
        salida = self.correr(["jmesa", "mesa2026", "10", "5", "9"])
        self.assertIn("Solo el administrador puede crear usuarios.", salida)
        self.assertIn("Solo el administrador puede eliminar expedientes.", salida)
        self.assertIn("EXP-0001", self.leer())

    # --- operaciones sobre expedientes -----------------------------------

    def test_modificar_conserva_estado_dependencia_e_historial(self):
        self.escribir(EN_PROCESO)
        salida = self.correr(["admin", "admin123", "4", "EXP-0001",
                              "Juan Perez", "12345678",
                              "Licencia de funcionamiento", "9"])
        self.assertIn("Expediente modificado.", salida)
        texto = self.leer()
        self.assertIn("Licencia de funcionamiento", texto)
        self.assertIn("|En proceso|Licencias|2026-10-16,Recibido,admin;"
                      "2026-10-20,En proceso,jmesa", texto)

    def test_cambiar_estado_agrega_la_entrada_al_historial(self):
        self.escribir(EN_PROCESO)
        salida = self.correr(["admin", "admin123", "8", "EXP-0001", "3", "9"])
        self.assertIn("Estado actual: En proceso", salida)
        self.assertIn("Estado cambiado a Atendido.", salida)
        self.assertIn("|Atendido|Licencias|2026-10-16,Recibido,admin;"
                      "2026-10-20,En proceso,jmesa;" + HOY + ",Atendido,admin",
                      self.leer())

    def test_cambiar_al_mismo_estado_no_duplica_el_historial(self):
        self.escribir(EN_PROCESO)
        salida = self.correr(["admin", "admin123", "8", "EXP-0001", "2", "9"])
        self.assertIn("El expediente ya esta en ese estado.", salida)
        self.assertEqual(self.leer().count(";"), 1)

    def test_buscar_por_codigo_y_por_texto(self):
        self.escribir(TRES)
        salida = self.correr(["admin", "admin123", "2", "EXP-0002",
                              "3", "asunto", "licencia", "9"])
        self.assertIn("EXP-0002 | Maria Lopez | 87654321 | Reclamo de arbitrios", salida)
        self.assertIn("Solicitud de licencia", salida)
        self.assertIn("Licencia de obra", salida)

    def test_ordenar_por_nombre(self):
        self.escribir(TRES)
        salida = self.correr(["admin", "admin123", "6", "nombre", "9"])
        self.assertLess(salida.index("EXP-0003"), salida.index("EXP-0001"))
        self.assertLess(salida.index("EXP-0001"), salida.index("EXP-0002"))

    def test_eliminar_como_administrador(self):
        self.escribir(TRES)
        salida = self.correr(["admin", "admin123", "5", "EXP-0001", "9"])
        self.assertIn("Expediente eliminado con exito.", salida)
        lineas = self.leer().strip().splitlines()
        self.assertEqual(len(lineas), 2)
        self.assertFalse([l for l in lineas if l.startswith("EXP-0001|")])


if __name__ == "__main__":
    unittest.main()
