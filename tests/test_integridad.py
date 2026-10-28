"""Pruebas de la rutina de integridad aplicada a los datos leidos del archivo.

Cada prueba de carga trabaja en una carpeta temporal: nunca se toca el
expedientes.txt real.
"""

import os
import tempfile
import unittest

import integridad
import persistencia
from expediente import crear_expediente


def crear_valido(**cambios):
    """Retorna un expediente integro; cambios permite romper un campo."""
    datos = {"codigo": "EXP-0001", "nombre": "Juan Perez", "dni": "30112233",
             "asunto": "Solicitud de licencia", "fecha": "2026-10-20",
             "estado": "En proceso", "dependencia": "Licencias"}
    datos.update(cambios)
    return crear_expediente(**datos)


class PruebasDeFecha(unittest.TestCase):

    def test_fecha_del_calendario_es_valida(self):
        self.assertTrue(integridad.fecha_valida("2026-10-20"))
        self.assertTrue(integridad.fecha_valida("2024-02-29"))

    def test_fecha_que_no_existe_es_invalida(self):
        self.assertFalse(integridad.fecha_valida("2026-02-30"))
        self.assertFalse(integridad.fecha_valida("2026-13-01"))
        self.assertFalse(integridad.fecha_valida("2025-02-29"))

    def test_fecha_con_otro_formato_es_invalida(self):
        self.assertFalse(integridad.fecha_valida("20-10-2026"))
        self.assertFalse(integridad.fecha_valida("2026-1-1"))
        self.assertFalse(integridad.fecha_valida("2026/10/20"))
        self.assertFalse(integridad.fecha_valida(""))


class PruebasDeExpediente(unittest.TestCase):

    def test_expediente_integro_no_tiene_problemas(self):
        self.assertEqual(integridad.revisar_expediente(crear_valido()), [])

    def test_dni_sin_ocho_digitos_se_reporta(self):
        self.assertIn("dni invalido", integridad.revisar_expediente(crear_valido(dni="ABC")))
        self.assertIn("dni invalido", integridad.revisar_expediente(crear_valido(dni="1234")))

    def test_nombre_y_asunto_vacios_se_reportan(self):
        self.assertIn("sin nombre", integridad.revisar_expediente(crear_valido(nombre="")))
        self.assertIn("sin asunto", integridad.revisar_expediente(crear_valido(asunto="")))

    def test_codigo_fuera_de_formato_se_reporta(self):
        self.assertIn("codigo fuera de formato",
                      integridad.revisar_expediente(crear_valido(codigo="123-ABC")))

    def test_estado_y_dependencia_desconocidos_se_reportan(self):
        problemas = integridad.revisar_expediente(
            crear_valido(estado="Volando", dependencia="Marte"))
        self.assertIn("estado desconocido", problemas)
        self.assertIn("dependencia desconocida", problemas)

    def test_fecha_inexistente_se_reporta(self):
        self.assertIn("fecha invalida",
                      integridad.revisar_expediente(crear_valido(fecha="2026-13-45")))

    def test_historial_vacio_se_reporta(self):
        self.assertIn("historial vacio",
                      integridad.revisar_expediente(crear_valido(historial=[])))

    def test_historial_con_estado_desconocido_se_reporta(self):
        historial = [{"fecha": "2026-10-20", "estado": "Volando", "usuario": "admin"}]
        self.assertIn("historial con estado desconocido",
                      integridad.revisar_expediente(crear_valido(historial=historial)))

    def test_historial_con_entrada_mal_formada_se_reporta(self):
        self.assertIn("historial mal formado",
                      integridad.revisar_expediente(crear_valido(historial=["2026-10-20"])))


class PruebasDeLista(unittest.TestCase):

    def test_lista_separa_integros_de_rechazados(self):
        validos, rechazos = integridad.revisar_lista(
            [crear_valido(), crear_valido(codigo="EXP-0002", dni="ABC")])
        self.assertEqual([e["codigo"] for e in validos], ["EXP-0001"])
        self.assertEqual(rechazos[0]["codigo"], "EXP-0002")
        self.assertIn("dni invalido", rechazos[0]["motivo"])

    def test_codigo_repetido_rechaza_el_segundo(self):
        validos, rechazos = integridad.revisar_lista(
            [crear_valido(), crear_valido(nombre="Maria Lopez")])
        self.assertEqual(len(validos), 1)
        self.assertIn("codigo repetido", rechazos[0]["motivo"])

    def test_resumen_menciona_codigo_y_motivo(self):
        resumen = integridad.resumir_rechazos(
            [{"codigo": "EXP-0007", "motivo": "dni invalido"}])
        self.assertIn("EXP-0007", resumen)
        self.assertIn("dni invalido", resumen)
        self.assertEqual(integridad.resumir_rechazos([]), "")


class PruebasDeCarga(unittest.TestCase):

    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.ruta = os.path.join(self.carpeta.name, "expedientes.txt")
        self.almacenamiento_original = persistencia.ALMACENAMIENTO
        persistencia.ALMACENAMIENTO = "txt"

    def tearDown(self):
        persistencia.ALMACENAMIENTO = self.almacenamiento_original
        self.carpeta.cleanup()

    def escribir(self, lineas):
        with open(self.ruta, "w", encoding="utf-8", newline="\n") as archivo:
            archivo.write("\n".join(lineas) + "\n")

    def test_carga_omite_lineas_con_datos_invalidos(self):
        self.escribir([
            "EXP-0001|Juan Perez|30112233|Solicitud de licencia|2026-10-20|En proceso|Licencias|2026-10-20,Recibido,sistema",
            "EXP-0002|Maria Lopez|ABC|Constancia|2026-10-21|Recibido|Rentas|2026-10-21,Recibido,sistema",
            "EXP-0003|Carlos Ruiz|33122004|Reclamo|2026-13-45|Recibido|Obras|2026-10-22,Recibido,sistema",
            "EXP-0004|Ana Torres|27788999|Matrimonio|2026-10-23",
            "linea|mal|formada",
        ])
        expedientes, rechazos = persistencia.cargar_con_informe(self.ruta)
        self.assertEqual([e["codigo"] for e in expedientes], ["EXP-0001", "EXP-0004"])
        self.assertEqual(len(rechazos), 3)

    def test_carga_de_cinco_campos_sigue_siendo_valida(self):
        self.escribir(["EXP-0001|Juan Perez|12345678|Tramite|2026-10-16"])
        expedientes, rechazos = persistencia.cargar_con_informe(self.ruta)
        self.assertEqual(len(expedientes), 1)
        self.assertEqual(rechazos, [])

    def test_archivo_inexistente_no_reporta_rechazos(self):
        self.assertEqual(persistencia.cargar_con_informe(self.ruta), ([], []))

    def test_cargar_desde_archivo_devuelve_solo_los_integros(self):
        self.escribir([
            "EXP-0001|Juan Perez|30112233|Solicitud de licencia|2026-10-20|En proceso|Licencias|2026-10-20,Recibido,sistema",
            "EXP-0002|Maria Lopez|ABC|Constancia|2026-10-21|Recibido|Rentas|2026-10-21,Recibido,sistema",
        ])
        self.assertEqual([e["codigo"] for e in persistencia.cargar_desde_archivo(self.ruta)],
                         ["EXP-0001"])


if __name__ == "__main__":
    unittest.main()
