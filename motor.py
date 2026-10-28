"""Analizador lexico, parser descendente recursivo e interprete educativo.

No utiliza eval(), exec() ni ejecuta comandos del sistema.
Solo entiende la gramatica restringida documentada en documentacion/GRAMATICA.md.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


KEYWORDS = {
    'algoritmo': 'ALGORITMO', 'finalgoritmo': 'FINALGORITMO',
    'definir': 'DEFINIR', 'como': 'COMO',
    'entero': 'ENTERO', 'decimal': 'DECIMAL', 'texto': 'TEXTO',
    'leer': 'LEER', 'escribir': 'ESCRIBIR',
    'si': 'SI', 'entonces': 'ENTONCES', 'sino': 'SINO', 'finsi': 'FINSI',
}

TOKEN_RE = re.compile(
    r'(?P<ESPACIO>[ \t\r\n]+)'
    r'|(?P<COMENTARIO>//[^\n]*)'
    r'|(?P<CADENA>"(?:\\["\\ntr]|[^"\\\n])*")'
    r'|(?P<NUMERO>\d+(?:\.\d+)?)'
    r'|(?P<COMPARADOR>==|!=|<=|>=|<|>)'
    r'|(?P<OPERADOR>[+\-*/=])'
    r'|(?P<SIMBOLO>[();,])'
    r'|(?P<IDENTIFICADOR>[A-Za-z_][A-Za-z0-9_]*)'
    r'|(?P<INVALIDO>.)'
)


@dataclass(frozen=True)
class Token:
    tipo: str
    lexema: str
    linea: int
    columna: int

    def to_dict(self):
        return {'tipo': self.tipo, 'lexema': self.lexema,
                'linea': self.linea, 'columna': self.columna}


class ErrorLenguaje(Exception):
    categoria = 'Error'

    def __init__(self, mensaje: str, linea: int, columna: int = 1):
        self.mensaje = mensaje
        self.linea = linea
        self.columna = columna
        super().__init__(f'{self.categoria} en linea {linea}, columna {columna}: {mensaje}')

    def to_dict(self):
        return {'categoria': self.categoria, 'mensaje': self.mensaje,
                'linea': self.linea, 'columna': self.columna}


class ErrorLexico(ErrorLenguaje):
    categoria = 'Error lexico'


class ErrorSintactico(ErrorLenguaje):
    categoria = 'Error sintactico'


class ErrorEjecucion(ErrorLenguaje):
    categoria = 'Error de ejecucion'


class SolicitudEntrada(Exception):
    def __init__(self, nombre, tipo, indice, linea):
        self.nombre, self.tipo, self.indice, self.linea = nombre, tipo, indice, linea
        super().__init__(f'Se necesita un valor para {nombre} ({tipo})')


def analizar_lexico(codigo: str) -> list[Token]:
    if len(codigo) > 60_000:
        raise ErrorLexico('El programa supera el limite de 60 000 caracteres.', 1)
    tokens = []
    linea, columna, posicion = 1, 1, 0
    while posicion < len(codigo):
        if codigo[posicion] == '"':
            # Si hay una comilla sin cerrar, se informa un error orientativo.
            match_cadena = TOKEN_RE.match(codigo, posicion)
            if not match_cadena or match_cadena.lastgroup != 'CADENA':
                raise ErrorLexico('Cadena sin cerrar o escape no permitido. Use comillas dobles.', linea, columna)
        match = TOKEN_RE.match(codigo, posicion)
        if not match:
            raise ErrorLexico('Caracter no reconocido.', linea, columna)
        clase, lexema = match.lastgroup, match.group()
        if clase == 'INVALIDO':
            raise ErrorLexico(f'Caracter no permitido: {lexema!r}.', linea, columna)
        if clase not in ('ESPACIO', 'COMENTARIO'):
            if clase == 'NUMERO' and len(lexema) > 100:
                raise ErrorLexico('Numero demasiado largo (maximo 100 caracteres).', linea, columna)
            tipo = clase
            if clase == 'IDENTIFICADOR':
                tipo = KEYWORDS.get(lexema.lower(), 'IDENTIFICADOR')
            elif clase == 'COMPARADOR' or clase == 'OPERADOR' or clase == 'SIMBOLO':
                tipo = lexema
            tokens.append(Token(tipo, lexema, linea, columna))
            if len(tokens) > 12000:
                raise ErrorLexico('Demasiados tokens (maximo 12000).', linea, columna)
        saltos = lexema.count('\n')
        if saltos:
            linea += saltos
            columna = len(lexema.rsplit('\n', 1)[-1]) + 1
        else:
            columna += len(lexema)
        posicion = match.end()
    tokens.append(Token('EOF', '', linea, columna))
    return tokens


@dataclass
class Numero:
    valor: int | float
    token: Token


@dataclass
class Cadena:
    valor: str
    token: Token


@dataclass
class Variable:
    nombre: str
    token: Token


@dataclass
class Unario:
    operador: str
    expresion: Any
    token: Token


@dataclass
class Binario:
    izquierda: Any
    operador: str
    derecha: Any
    token: Token


@dataclass
class Declaracion:
    nombre: str
    tipo: str
    token: Token


@dataclass
class Asignacion:
    nombre: str
    expresion: Any
    token: Token


@dataclass
class Lectura:
    nombre: str
    token: Token


@dataclass
class Escritura:
    expresiones: list
    token: Token


@dataclass
class Condicional:
    izquierda: Any
    operador: str
    derecha: Any
    verdadero: list
    falso: list
    token: Token


@dataclass
class Programa:
    nombre: str
    instrucciones: list


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0
        self.profundidad = 0

    @property
    def actual(self):
        return self.tokens[self.i]

    def tomar(self):
        t = self.actual
        self.i += 1
        return t

    def aceptar(self, tipo):
        if self.actual.tipo == tipo:
            return self.tomar()
        return None

    def exigir(self, tipo, explicacion=None):
        t = self.aceptar(tipo)
        if t is None:
            actual = self.actual
            cerca = f' (se encontro {actual.lexema!r})' if actual.tipo != 'EOF' else ' (fin de codigo)'
            raise ErrorSintactico((explicacion or f'Se esperaba {tipo!r}') + cerca + '.',
                                  actual.linea, actual.columna)
        return t

    def analizar(self):
        self.exigir('ALGORITMO', 'El programa debe comenzar con Algoritmo')
        nombre = self.exigir('IDENTIFICADOR', 'Se esperaba el nombre del algoritmo').lexema
        cuerpo = self.bloque({'FINALGORITMO'})
        self.exigir('FINALGORITMO', 'Falta FinAlgoritmo para cerrar el programa')
        self.exigir('EOF', 'No se permiten instrucciones despues de FinAlgoritmo')
        return Programa(nombre, cuerpo)

    def bloque(self, fin):
        instrucciones = []
        while self.actual.tipo not in fin and self.actual.tipo != 'EOF':
            if self.actual.tipo == 'FINALGORITMO' and 'FINSI' in fin:
                raise ErrorSintactico('Falta FinSi antes de FinAlgoritmo.', self.actual.linea, self.actual.columna)
            instrucciones.append(self.instruccion())
            if len(instrucciones) > 5000:
                t = self.actual
                raise ErrorSintactico('Demasiadas instrucciones en un bloque.', t.linea, t.columna)
        return instrucciones

    def instruccion(self):
        t = self.actual
        if t.tipo == 'DEFINIR':
            self.tomar()
            nombre = self.exigir('IDENTIFICADOR', 'Se esperaba un nombre de variable despues de Definir')
            self.exigir('COMO', 'Falta Como en la declaracion')
            if self.actual.tipo not in ('ENTERO', 'DECIMAL', 'TEXTO'):
                raise ErrorSintactico('El tipo debe ser Entero, Decimal o Texto.', self.actual.linea, self.actual.columna)
            tipo = self.tomar().tipo
            self.exigir(';', 'Falta ; al finalizar la declaracion')
            return Declaracion(nombre.lexema, tipo, t)
        if t.tipo == 'IDENTIFICADOR':
            self.tomar()
            self.exigir('=', 'Una asignacion debe utilizar =')
            expresion = self.expresion()
            self.exigir(';', 'Falta ; al finalizar la asignacion')
            return Asignacion(t.lexema, expresion, t)
        if t.tipo == 'LEER':
            self.tomar()
            self.exigir('(', 'Leer requiere parentesis de apertura (')
            nombre = self.exigir('IDENTIFICADOR', 'Leer requiere el nombre de una variable')
            self.exigir(')', 'Leer requiere parentesis de cierre )')
            self.exigir(';', 'Falta ; al finalizar Leer')
            return Lectura(nombre.lexema, t)
        if t.tipo == 'ESCRIBIR':
            self.tomar()
            self.exigir('(', 'Escribir requiere parentesis de apertura (')
            expresiones = [self.expresion()]
            while self.aceptar(','):
                expresiones.append(self.expresion())
            self.exigir(')', 'Escribir requiere parentesis de cierre )')
            self.exigir(';', 'Falta ; al finalizar Escribir')
            return Escritura(expresiones, t)
        if t.tipo == 'SI':
            self.tomar()
            izquierda = self.expresion()
            if self.actual.tipo not in ('==', '!=', '>', '<', '>=', '<='):
                raise ErrorSintactico('La condicion necesita un comparador: ==, !=, >, <, >= o <=.',
                                      self.actual.linea, self.actual.columna)
            operador = self.tomar().tipo
            derecha = self.expresion()
            self.exigir('ENTONCES', 'Falta Entonces despues de la condicion')
            self.profundidad += 1
            if self.profundidad > 40:
                raise ErrorSintactico('Demasiados condicionales anidados (maximo 40).', t.linea, t.columna)
            verdadero = self.bloque({'SINO', 'FINSI'})
            falso = self.bloque({'FINSI'}) if self.aceptar('SINO') else []
            self.exigir('FINSI', 'Falta FinSi para cerrar el condicional')
            self.profundidad -= 1
            return Condicional(izquierda, operador, derecha, verdadero, falso, t)
        if t.tipo in ('SINO', 'FINSI'):
            raise ErrorSintactico(f'{t.lexema} sin un Si correspondiente.', t.linea, t.columna)
        raise ErrorSintactico(
            'Instruccion no valida. Use Definir, asignacion, Leer, Escribir o Si.'
            + (f' Se encontro {t.lexema!r}.' if t.tipo != 'EOF' else ''),
            t.linea, t.columna)

    def expresion(self):
        nodo = self.termino()
        while self.actual.tipo in ('+', '-'):
            t = self.tomar()
            nodo = Binario(nodo, t.tipo, self.termino(), t)
        return nodo

    def termino(self):
        nodo = self.factor()
        while self.actual.tipo in ('*', '/'):
            t = self.tomar()
            nodo = Binario(nodo, t.tipo, self.factor(), t)
        return nodo

    def factor(self):
        t = self.actual
        if t.tipo in ('+', '-'):
            self.tomar()
            return Unario(t.tipo, self.factor(), t)
        if t.tipo == 'NUMERO':
            self.tomar()
            return Numero(float(t.lexema) if '.' in t.lexema else int(t.lexema), t)
        if t.tipo == 'CADENA':
            self.tomar()
            escapes = {'\\n': '\n', '\\t': '\t', '\\r': '\r', '\\"': '"', '\\\\': '\\'}
            texto = re.sub(r'\\[ntr"\\]', lambda m: escapes[m.group()], t.lexema[1:-1])
            return Cadena(texto, t)
        if t.tipo == 'IDENTIFICADOR':
            self.tomar()
            return Variable(t.lexema, t)
        if self.aceptar('('):
            resultado = self.expresion()
            self.exigir(')', 'Falta parentesis ) en la expresion')
            return resultado
        raise ErrorSintactico('Se esperaba un numero, texto, variable o expresion entre parentesis.',
                              t.linea, t.columna)


def formato_valor(v):
    if isinstance(v, float):
        return f'{v:.12g}'
    return str(v)


class Interprete:
    def __init__(self, entradas=None):
        self.variables = {}
        self.salida = []
        self.entradas = entradas if entradas is not None else []
        self.indice_entrada = 0
        self.pasos = 0

    def error(self, mensaje, t):
        raise ErrorEjecucion(mensaje, t.linea, t.columna)

    def visitar_expresion(self, nodo):
        if isinstance(nodo, (Numero, Cadena)):
            return nodo.valor
        if isinstance(nodo, Variable):
            v = self.variables.get(nodo.nombre)
            if v is None:
                self.error(f'La variable {nodo.nombre!r} no esta declarada.', nodo.token)
            if v['valor'] is None:
                self.error(f'La variable {nodo.nombre!r} aun no tiene un valor.', nodo.token)
            return v['valor']
        if isinstance(nodo, Unario):
            valor = self.visitar_expresion(nodo.expresion)
            if type(valor) not in (int, float):
                self.error('El signo + o - solo se aplica a numeros.', nodo.token)
            return valor if nodo.operador == '+' else -valor
        if isinstance(nodo, Binario):
            a = self.visitar_expresion(nodo.izquierda)
            b = self.visitar_expresion(nodo.derecha)
            if type(a) not in (int, float) or type(b) not in (int, float):
                self.error('Los operadores aritmeticos solo admiten numeros.', nodo.token)
            if nodo.operador == '+': return a + b
            if nodo.operador == '-': return a - b
            if nodo.operador == '*': return a * b
            if b == 0:
                self.error('Division entre cero. Revise el denominador.', nodo.token)
            return a / b
        raise AssertionError('Nodo de expresion desconocido')

    def asignar(self, nombre, valor, token):
        variable = self.variables.get(nombre)
        if variable is None:
            self.error(f'La variable {nombre!r} no esta declarada. Declarela con Definir.', token)
        tipo = variable['tipo']
        if tipo == 'TEXTO':
            if not isinstance(valor, str):
                self.error(f'La variable {nombre!r} es Texto y no admite numeros.', token)
        elif tipo == 'ENTERO':
            if type(valor) not in (int, float) or (isinstance(valor, float) and not valor.is_integer()):
                self.error(f'La variable {nombre!r} es Entero y requiere un numero entero.', token)
            valor = int(valor)
        else:
            if type(valor) not in (int, float):
                self.error(f'La variable {nombre!r} es Decimal y requiere un numero.', token)
            valor = float(valor)
        self.variables[nombre]['valor'] = valor

    def condicion(self, nodo):
        a = self.visitar_expresion(nodo.izquierda)
        b = self.visitar_expresion(nodo.derecha)
        if type(a) not in (int, float) or type(b) not in (int, float):
            if not (isinstance(a, str) and isinstance(b, str) and nodo.operador in ('==', '!=')):
                self.error('Solo se pueden ordenar numeros. Para textos utilice == o !=.', nodo.token)
        return {'==': lambda: a == b, '!=': lambda: a != b,
                '<': lambda: a < b, '>': lambda: a > b,
                '<=': lambda: a <= b, '>=': lambda: a >= b}[nodo.operador]()

    def ejecutar_bloque(self, instrucciones):
        for nodo in instrucciones:
            self.pasos += 1
            if self.pasos > 10000:
                self.error('Se supero el limite de 10000 instrucciones.', nodo.token)
            if isinstance(nodo, Declaracion):
                if nodo.nombre in self.variables:
                    self.error(f'La variable {nodo.nombre!r} ya fue declarada.', nodo.token)
                self.variables[nodo.nombre] = {'tipo': nodo.tipo, 'valor': None}
            elif isinstance(nodo, Asignacion):
                self.asignar(nodo.nombre, self.visitar_expresion(nodo.expresion), nodo.token)
            elif isinstance(nodo, Lectura):
                variable = self.variables.get(nodo.nombre)
                if variable is None:
                    self.error(f'La variable {nodo.nombre!r} debe declararse antes de Leer.', nodo.token)
                if self.indice_entrada >= len(self.entradas):
                    raise SolicitudEntrada(nodo.nombre, variable['tipo'], self.indice_entrada, nodo.token.linea)
                bruto = self.entradas[self.indice_entrada]
                self.indice_entrada += 1
                if not isinstance(bruto, str) or len(bruto) > 2000:
                    self.error('La entrada debe ser texto de hasta 2000 caracteres.', nodo.token)
                if variable['tipo'] == 'ENTERO':
                    if not re.fullmatch(r'[+-]?\d+', bruto.strip()):
                        self.error(f'Entrada incorrecta para {nodo.nombre}: se esperaba Entero.', nodo.token)
                    valor = int(bruto.strip())
                elif variable['tipo'] == 'DECIMAL':
                    if not re.fullmatch(r'[+-]?\d+(?:\.\d+)?', bruto.strip()):
                        self.error(f'Entrada incorrecta para {nodo.nombre}: se esperaba Decimal.', nodo.token)
                    valor = float(bruto.strip())
                else:
                    valor = bruto
                self.asignar(nodo.nombre, valor, nodo.token)
            elif isinstance(nodo, Escritura):
                self.salida.append(''.join(formato_valor(self.visitar_expresion(e)) for e in nodo.expresiones))
            elif isinstance(nodo, Condicional):
                self.ejecutar_bloque(nodo.verdadero if self.condicion(nodo) else nodo.falso)
            else:
                raise AssertionError('Nodo de instruccion desconocido')

    def ejecutar(self, programa):
        self.ejecutar_bloque(programa.instrucciones)
        return {'salida': self.salida, 'variables': self.variables}


def procesar(codigo: str, entradas=None, solo_analizar=False):
    """API pura para web y pruebas automatizadas."""
    tokens = []
    try:
        tokens = analizar_lexico(codigo)
        arbol = Parser(tokens).analizar()
        respuesta = {
            'estado': 'analizado' if solo_analizar else 'correcto',
            'mensaje': f'Analisis lexico y sintactico correcto: Algoritmo {arbol.nombre}.',
            'tokens': [t.to_dict() for t in tokens if t.tipo != 'EOF'],
            'cantidad_instrucciones': len(arbol.instrucciones),
            'nombre_algoritmo': arbol.nombre,
        }
        if solo_analizar:
            return respuesta
        interprete = Interprete(entradas)
        try:
            respuesta.update(interprete.ejecutar(arbol))
            respuesta['mensaje'] = f'Programa {arbol.nombre} ejecutado correctamente.'
        except SolicitudEntrada as solicitud:
            respuesta.update({
                'estado': 'esperando_entrada',
                'entrada_solicitada': {'nombre': solicitud.nombre, 'tipo': solicitud.tipo,
                                      'indice': solicitud.indice, 'linea': solicitud.linea},
                'salida': interprete.salida,
                'variables': interprete.variables,
                'mensaje': f'Esperando un dato para {solicitud.nombre}.',
            })
        except ErrorEjecucion as e:
            respuesta.update({'estado': 'error', 'error': e.to_dict(),
                              'mensaje': str(e), 'salida': interprete.salida,
                              'variables': interprete.variables})
        return respuesta
    except ErrorLenguaje as e:
        return {'estado': 'error', 'mensaje': str(e), 'error': e.to_dict(),
                'tokens': [t.to_dict() for t in tokens if t.tipo != 'EOF'],
                'salida': [], 'variables': {}}
