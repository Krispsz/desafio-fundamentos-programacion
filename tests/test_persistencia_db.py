"""Pruebas de persistencia_db.py (SQLite) y del selector de persistencia.py.

Cada prueba trabaja en una carpeta temporal: nunca se toca el mesa_partes.db real.
Los valores por defecto ruta=RUTA_DB se fijan al cargar el modulo, por eso
setUp tambien cambia la carpeta de trabajo a la temporal: asi cualquier ruta
relativa (mesa_partes.db, expedientes.txt) queda dentro de ella.
"""

import os
import sqlite3
import tempfile
import unittest
from contextlib import closing

import persistencia
import persistencia_db
from expediente import crear_expediente


def expedientes_de_prueba():
    """Retorna 2 expedientes con historial de 2 y 1 entradas."""
    historial_1 = [{"fecha": "2026-10-16", "estado": "Recibido", "usuario": "admin"},
                   {"fecha": "2026-10-20", "estado": "En proceso", "usuario": "jmesa"}]
    historial_2 = [{"fecha": "2026-10-17", "estado": "Recibido", "usuario": "jmesa"}]
    return [crear_expediente("EXP-0001", "Juan Perez", "12345678", "Solicitud de licencia",
                             "2026-10-16", "En proceso", "Licencias", historial_1),
            crear_expediente("EXP-0002", "Maria Lopez", "87654321", "Reclamo de arbitrios",
                             "2026-10-17", "Recibido", "Rentas", historial_2)]


class PruebasPersistenciaDB(unittest.TestCase):

    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.carpeta_original = os.getcwd()
        os.chdir(self.carpeta.name)
        self.ruta_db = os.path.join(self.carpeta.name, "mesa_partes.db")
        self.ruta_txt = os.path.join(self.carpeta.name, "expedientes.txt")
        self.ruta_db_original = persistencia_db.RUTA_DB
        self.almacenamiento_original = persistencia.ALMACENAMIENTO

    def tearDown(self):
        persistencia_db.RUTA_DB = self.ruta_db_original
        persistencia.ALMACENAMIENTO = self.almacenamiento_original
        os.chdir(self.carpeta_original)
        self.carpeta.cleanup()

    def contar_filas(self, tabla):
        """Retorna la cantidad de filas de una tabla de la base de prueba."""
        with closing(sqlite3.connect(self.ruta_db)) as conexion:
            return conexion.execute("SELECT COUNT(*) FROM " + tabla).fetchone()[0]

    def test_crear_tablas_crea_expedientes_e_historial(self):
        self.assertTrue(persistencia_db.crear_tablas(self.ruta_db))
        with closing(sqlite3.connect(self.ruta_db)) as conexion:
            filas = conexion.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        nombres = [fila[0] for fila in filas]
        self.assertIn("expedientes", nombres)
        self.assertIn("historial", nombres)

    def test_guardar_y_cargar_dos_expedientes_con_historial_en_orden(self):
        expedientes = expedientes_de_prueba()
        self.assertTrue(persistencia_db.guardar_en_db(expedientes, self.ruta_db))
        cargados = persistencia_db.cargar_desde_db(self.ruta_db)
        self.assertEqual(cargados, expedientes)
        self.assertEqual([e["estado"] for e in cargados[0]["historial"]],
                         ["Recibido", "En proceso"])

    def test_nombre_con_apostrofe_se_guarda_y_lee_bien(self):
        expedientes = [crear_expediente("EXP-0001", "Patrick O'Brien", "12345678",
                                        "Tramite de 'prueba'", "2026-10-16")]
        self.assertTrue(persistencia_db.guardar_en_db(expedientes, self.ruta_db))
        cargados = persistencia_db.cargar_desde_db(self.ruta_db)
        self.assertEqual(cargados[0]["nombre"], "Patrick O'Brien")
        self.assertEqual(cargados[0]["asunto"], "Tramite de 'prueba'")

    def test_guardar_sin_un_expediente_borra_tambien_su_historial(self):
        expedientes = expedientes_de_prueba()
        persistencia_db.guardar_en_db(expedientes, self.ruta_db)
        self.assertEqual(self.contar_filas("historial"), 3)
        expedientes.pop(0)
        self.assertTrue(persistencia_db.guardar_en_db(expedientes, self.ruta_db))
        self.assertEqual(self.contar_filas("expedientes"), 1)
        self.assertEqual(self.contar_filas("historial"), 1)
        with closing(sqlite3.connect(self.ruta_db)) as conexion:
            filas = conexion.execute(
                "SELECT COUNT(*) FROM historial WHERE codigo = ?", ("EXP-0001",)).fetchone()
        self.assertEqual(filas[0], 0)

    def test_base_inexistente_da_lista_vacia(self):
        self.assertEqual(persistencia_db.cargar_desde_db(self.ruta_db), [])

    def test_migrar_txt_de_tres_lineas_retorna_tres(self):
        with open(self.ruta_txt, "w", encoding="utf-8") as archivo:
            archivo.write("EXP-0001|Juan Perez|12345678|Tramite|2026-10-16\n"
                          "EXP-0002|Maria Lopez|87654321|Reclamo|2026-10-17|Recibido|Rentas|"
                          "2026-10-17,Recibido,admin\n"
                          "EXP-0003|Ana Diaz|11223344|Licencia de obra|2026-10-18\n")
        self.assertEqual(persistencia_db.migrar_txt_a_db(self.ruta_txt, self.ruta_db), 3)
        self.assertEqual(len(persistencia_db.cargar_desde_db(self.ruta_db)), 3)

    def test_migrar_sin_txt_retorna_menos_uno(self):
        self.assertEqual(persistencia_db.migrar_txt_a_db(self.ruta_txt, self.ruta_db), -1)
        self.assertFalse(os.path.exists(self.ruta_db))

    def test_selector_sqlite_migra_solo_si_no_hay_db_y_hay_txt(self):
        with open(self.ruta_txt, "w", encoding="utf-8") as archivo:
            archivo.write("EXP-0001|Juan Perez|12345678|Tramite|2026-10-16\n"
                          "EXP-0002|Maria Lopez|87654321|Reclamo|2026-10-17\n")
        persistencia.ALMACENAMIENTO = "sqlite"
        persistencia_db.RUTA_DB = self.ruta_db
        expedientes = persistencia.cargar_desde_archivo(self.ruta_txt)
        self.assertEqual([e["codigo"] for e in expedientes], ["EXP-0001", "EXP-0002"])
        self.assertTrue(os.path.exists(self.ruta_db))
        self.assertTrue(os.path.exists(self.ruta_txt))


if __name__ == "__main__":
    unittest.main()
