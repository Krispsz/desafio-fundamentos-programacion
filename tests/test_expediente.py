"""Pruebas de expediente.py: estructura, historial y codigos correlativos."""

import unittest

from expediente import crear_expediente, historial_a_texto, texto_a_historial, generar_codigo


class PruebasCrearExpediente(unittest.TestCase):

    def test_sin_historial_crea_entrada_recibido_por_sistema(self):
        expediente = crear_expediente("EXP-0001", "Juan Perez", "12345678", "Tramite",
                                      "2026-10-22")
        self.assertEqual(expediente["historial"],
                         [{"fecha": "2026-10-22", "estado": "Recibido", "usuario": "sistema"}])

    def test_sin_estado_ni_dependencia_usa_valores_por_defecto(self):
        expediente = crear_expediente("EXP-0001", "Juan Perez", "12345678", "Tramite",
                                      "2026-10-22")
        self.assertEqual(expediente["estado"], "Recibido")
        self.assertEqual(expediente["dependencia"], "Mesa de Partes")

    def test_con_historial_lo_conserva_tal_cual(self):
        historial = [{"fecha": "2026-10-22", "estado": "Recibido", "usuario": "admin"},
                     {"fecha": "2026-10-23", "estado": "En proceso", "usuario": "jmesa"}]
        expediente = crear_expediente("EXP-0001", "Juan Perez", "12345678", "Tramite",
                                      "2026-10-22", "En proceso", "Licencias", historial)
        self.assertEqual(expediente["historial"], historial)
        self.assertEqual(expediente["estado"], "En proceso")
        self.assertEqual(expediente["dependencia"], "Licencias")


class PruebasHistorial(unittest.TestCase):

    def test_historial_a_texto_y_texto_a_historial_son_inversos(self):
        historial = [{"fecha": "2026-10-22", "estado": "Recibido", "usuario": "admin"},
                     {"fecha": "2026-10-23", "estado": "En proceso", "usuario": "jmesa"}]
        texto = historial_a_texto(historial)
        self.assertEqual(texto, "2026-10-22,Recibido,admin;2026-10-23,En proceso,jmesa")
        self.assertEqual(texto_a_historial(texto), historial)

    def test_texto_vacio_da_historial_vacio(self):
        self.assertEqual(texto_a_historial(""), [])

    def test_entrada_mal_formada_se_ignora(self):
        historial = texto_a_historial("2026-10-22,Recibido;2026-10-23,En proceso,jmesa")
        self.assertEqual(historial,
                         [{"fecha": "2026-10-23", "estado": "En proceso", "usuario": "jmesa"}])


class PruebasGenerarCodigo(unittest.TestCase):

    def test_lista_vacia_da_exp_0001(self):
        self.assertEqual(generar_codigo([]), "EXP-0001")

    def test_codigo_siguiente_usa_el_mayor_mas_uno(self):
        expedientes = [crear_expediente("EXP-0001", "A", "11111111", "x", "2026-10-22"),
                       crear_expediente("EXP-0003", "B", "22222222", "y", "2026-10-22")]
        self.assertEqual(generar_codigo(expedientes), "EXP-0004")

    def test_codigo_tiene_cuatro_digitos_con_ceros(self):
        expedientes = [crear_expediente("EXP-0099", "A", "11111111", "x", "2026-10-22")]
        codigo = generar_codigo(expedientes)
        self.assertEqual(codigo, "EXP-0100")
        self.assertEqual(len(codigo[4:]), 4)
        self.assertTrue(codigo[4:].isdigit())


if __name__ == "__main__":
    unittest.main()
