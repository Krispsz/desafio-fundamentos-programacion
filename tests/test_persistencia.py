"""Pruebas de persistencia.py con ALMACENAMIENTO = "txt".

Cada prueba trabaja en una carpeta temporal: nunca se toca el expedientes.txt real.
"""

import os
import tempfile
import unittest

import persistencia
from expediente import crear_expediente


class PruebasPersistenciaTexto(unittest.TestCase):

    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.ruta = os.path.join(self.carpeta.name, "expedientes.txt")
        self.almacenamiento_original = persistencia.ALMACENAMIENTO
        persistencia.ALMACENAMIENTO = "txt"

    def tearDown(self):
        persistencia.ALMACENAMIENTO = self.almacenamiento_original
        self.carpeta.cleanup()

    def escribir(self, contenido):
        """Escribe bytes en el archivo de prueba."""
        with open(self.ruta, "wb") as archivo:
            archivo.write(contenido)

    def test_guardar_y_cargar_con_historial_lo_deja_igual(self):
        historial = [{"fecha": "2026-10-16", "estado": "Recibido", "usuario": "admin"},
                     {"fecha": "2026-10-20", "estado": "En proceso", "usuario": "jmesa"}]
        expedientes = [crear_expediente("EXP-0001", "Juan Perez", "12345678",
                                        "Solicitud de licencia", "2026-10-16",
                                        "En proceso", "Licencias", historial)]
        self.assertTrue(persistencia.guardar_en_archivo(expedientes, self.ruta))
        self.assertEqual(persistencia.cargar_desde_archivo(self.ruta), expedientes)

    def test_linea_de_cinco_campos_usa_valores_por_defecto(self):
        self.escribir(b"EXP-0001|Juan Perez|12345678|Tramite|2026-10-16\n")
        expedientes = persistencia.cargar_desde_archivo(self.ruta)
        self.assertEqual(len(expedientes), 1)
        self.assertEqual(expedientes[0]["estado"], "Recibido")
        self.assertEqual(expedientes[0]["dependencia"], "Mesa de Partes")
        self.assertEqual(expedientes[0]["historial"],
                         [{"fecha": "2026-10-16", "estado": "Recibido", "usuario": "sistema"}])

    def test_lineas_vacias_o_mal_formadas_se_saltan(self):
        self.escribir(b"\n"
                      b"EXP-0001|Juan Perez|12345678|Tramite|2026-10-16\n"
                      b"   \n"
                      b"linea|mal|formada\n"
                      b"EXP-0002|Maria Lopez|87654321|Reclamo|2026-10-17\n")
        expedientes = persistencia.cargar_desde_archivo(self.ruta)
        self.assertEqual([e["codigo"] for e in expedientes], ["EXP-0001", "EXP-0002"])

    def test_archivo_inexistente_da_lista_vacia(self):
        self.assertEqual(persistencia.cargar_desde_archivo(self.ruta), [])

    def test_byte_invalido_no_detiene_la_carga(self):
        self.escribir(b"EXP-0001|Juan P\xffrez|12345678|Tramite|2026-10-16\n"
                      b"\xff\n"
                      b"EXP-0002|Maria Lopez|87654321|Reclamo|2026-10-17\n")
        expedientes = persistencia.cargar_desde_archivo(self.ruta)
        self.assertEqual([e["codigo"] for e in expedientes], ["EXP-0001", "EXP-0002"])
        self.assertEqual(expedientes[1]["nombre"], "Maria Lopez")

    def test_guardar_en_carpeta_inexistente_retorna_false(self):
        ruta = os.path.join(self.carpeta.name, "no_existe", "expedientes.txt")
        expedientes = [crear_expediente("EXP-0001", "Juan Perez", "12345678", "Tramite",
                                        "2026-10-16")]
        self.assertFalse(persistencia.guardar_en_archivo(expedientes, ruta))


if __name__ == "__main__":
    unittest.main()
