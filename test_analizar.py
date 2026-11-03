import unittest
from io import StringIO

from analizar import calcular, validar


class AnalizarTests(unittest.TestCase):
    def leer(self, datos):
        return validar(StringIO("imdb,title,year,budget,domgross\n" + datos))

    def test_suma_y_media(self):
        resultado = calcular(self.leer("tt1,Una,2001,20,100\ntt2,Dos,2002,40,200\n"))
        self.assertEqual(resultado["suma"], 300)
        self.assertEqual(resultado["media"], 30)

    def test_faltantes(self):
        filas = self.leer("tt1,Una,2001,NA,NA\ntt2,Dos,2002,40,0\n")
        self.assertIsNone(filas[0]["domgross"])
        resultado = calcular(filas)
        self.assertEqual(resultado["faltantes"], 1)
        self.assertEqual(resultado["media"], 40)
        self.assertEqual(len(resultado["top"]), 1)

    def test_ingreso_negativo(self):
        with self.assertRaisesRegex(ValueError, "Fila 2, columna domgross"):
            self.leer("tt1,Una,2001,20,-100\n")

    def test_columna_ausente(self):
        with self.assertRaisesRegex(ValueError, "Fila 1, columna domgross"):
            validar(StringIO("imdb,title,year,budget\ntt1,Una,2001,20\n"))

    def test_titulo_con_marcador_de_dato_faltante(self):
        with self.assertRaisesRegex(ValueError, "Fila 2, columna title"):
            self.leer("tt0000001,#N/A,2001,20,100\n")
