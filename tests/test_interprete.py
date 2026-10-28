"""Bateria de pruebas del lenguaje Algora. Ejecutar python -m unittest discover -s tests -v"""
import sys
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from motor import procesar, analizar_lexico


class PruebasObligatorias(unittest.TestCase):
    def caso(self, archivo, estado='correcto', entradas=None):
        codigo = (BASE / 'ejemplos' / archivo).read_text(encoding='utf-8')
        resultado = procesar(codigo, entradas)
        self.assertEqual(resultado['estado'], estado, resultado.get('mensaje'))
        return resultado

    def test_01_aritmetica_precedencia(self):
        self.assertEqual(self.caso('01_aritmetica_basica.pseudo')['salida'], ['Resultado: 18'])

    def test_02_parentesis_y_decimales(self):
        self.assertEqual(self.caso('02_parentesis_decimales.pseudo')['salida'], ['Total: 5'])

    def test_03_entrada_numero(self):
        self.assertEqual(self.caso('03_entrada_edad.pseudo', entradas=['21'])['salida'], ['Edad ingresada: 21'])

    def test_04_entrada_texto(self):
        self.assertEqual(self.caso('04_entrada_nombre.pseudo', entradas=['Ana'])['salida'], ['Hola, Ana!'])

    def test_05_condicional_verdadera(self):
        self.assertEqual(self.caso('05_condicion_verdadera.pseudo')['salida'], ['Es mayor de edad'])

    def test_06_condicional_falsa(self):
        self.assertEqual(self.caso('06_condicion_falsa.pseudo')['salida'], ['Reprobado'])

    def test_07_error_lexico(self):
        r = self.caso('07_error_lexico.pseudo', 'error')
        self.assertEqual(r['error']['categoria'], 'Error lexico')
        self.assertEqual(r['error']['linea'], 3)

    def test_08_error_sintactico(self):
        r = self.caso('08_error_sintactico.pseudo', 'error')
        self.assertEqual(r['error']['categoria'], 'Error sintactico')
        self.assertEqual(r['error']['linea'], 4)

    def test_09_division_cero(self):
        r = self.caso('09_division_cero.pseudo', 'error')
        self.assertEqual(r['error']['categoria'], 'Error de ejecucion')
        self.assertIn('Division entre cero', r['mensaje'])

    def test_10_variable_sin_declarar(self):
        r = self.caso('10_variable_sin_declarar.pseudo', 'error')
        self.assertEqual(r['error']['categoria'], 'Error de ejecucion')
        self.assertIn('no esta declarada', r['mensaje'])


class PruebasAdicionales(unittest.TestCase):
    def test_11_condicional_anidado_comentarios_unarios(self):
        r = procesar((BASE / 'ejemplos/11_anidado_y_comentarios.pseudo').read_text())
        self.assertEqual(r['salida'], ['Negativo'])

    def test_12_solicitar_entrada(self):
        r = procesar((BASE / 'ejemplos/12_entrada_y_calculo.pseudo').read_text())
        self.assertEqual(r['estado'], 'esperando_entrada')
        self.assertEqual(r['entrada_solicitada']['tipo'], 'DECIMAL')

    def test_13_entrada_decimal(self):
        r = procesar((BASE / 'ejemplos/12_entrada_y_calculo.pseudo').read_text(), ['2.25'])
        self.assertEqual(r['salida'], ['El doble es 4.5'])

    def test_14_entrada_tipo_incorrecto(self):
        r = procesar((BASE / 'ejemplos/03_entrada_edad.pseudo').read_text(), ['dos'])
        self.assertEqual(r['estado'], 'error')
        self.assertIn('se esperaba Entero', r['mensaje'])

    def test_15_cadena_sin_cerrar(self):
        r = procesar('Algoritmo P\n Escribir("sin cerrar);\nFinAlgoritmo')
        self.assertEqual(r['error']['categoria'], 'Error lexico')
        self.assertEqual(r['error']['linea'], 2)

    def test_16_tipo_incorrecto(self):
        r = procesar('Algoritmo P\n Definir a Como Entero;\n a = 1.25;\nFinAlgoritmo')
        self.assertEqual(r['estado'], 'error')
        self.assertIn('requiere un numero entero', r['mensaje'])

    def test_17_texto_comparaciones(self):
        r = procesar('Algoritmo P\n Definir a Como Texto;\n a = "hola";\n Si a == "hola" Entonces\n Escribir("Si");\n FinSi\nFinAlgoritmo')
        self.assertEqual(r['salida'], ['Si'])

    def test_18_no_ejecuta_si_hay_sintaxis_erronea(self):
        r = procesar('Algoritmo P\n Escribir("Primero");\n Escribir("Falta")\nFinAlgoritmo')
        self.assertEqual(r['estado'], 'error')
        self.assertEqual(r['salida'], [])

    def test_19_tokens_reconocidos(self):
        t = analizar_lexico('Algoritmo Uno\n Definir x Como Decimal; x = 2.5; FinAlgoritmo')
        self.assertTrue(any(x.tipo=='NUMERO' and x.lexema=='2.5' for x in t))
        self.assertTrue(any(x.tipo=='DEFINIR' for x in t))

    def test_20_rechaza_codigo_python(self):
        r=procesar('Algoritmo P\n import os;\nFinAlgoritmo')
        self.assertEqual(r['estado'], 'error')


if __name__ == '__main__':
    unittest.main()
