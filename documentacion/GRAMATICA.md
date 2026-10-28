# Especificación del lenguaje Algora y gramática independiente de contexto

## 1. Definición y reglas de escritura

Algora es un pseudolenguaje interpretado en español que permite programas secuenciales y condicionales. No tiene ciclos ni funciones: no forman parte de los requisitos obligatorios.

- Estructura obligatoria: `Algoritmo Identificador` al principio y `FinAlgoritmo` al final. Solo se admite un algoritmo por archivo.
- Las instrucciones simples `Definir`, asignación, `Leer` y `Escribir` terminan con `;`.
- `Si ... Entonces` se cierra con `FinSi`; `SiNo` es opcional y no lleva punto y coma.
- Las palabras reservadas son indiferentes a mayúsculas/minúsculas; los identificadores son **sensibles** a mayúsculas.
- Identificador: comienza con letra ASCII o `_`, y continúa con letras ASCII, dígitos o `_`. No puede ser una palabra reservada.
- Los tipos admitidos son `Entero`, `Decimal` y `Texto`. Todas las variables requieren declaración previa.
- Las cadenas usan comillas dobles y admiten los escapes `\n`, `\t`, `\r`, `\"`, `\\`.
- Los decimales usan punto, como `3.14`. No se admite separador de miles.
- Se permiten comentarios de línea con `//`.
- Los operadores aritméticos son `+ - * /`; el orden es paréntesis, unarios, multiplicación/división, suma/resta.
- Los relacionales son `== != < <= > >=`. Para textos solo se permiten `==` y `!=`.
- `Escribir` admite una o más expresiones separadas por coma y las concatena sin insertar espacios adicionales. El usuario agrega espacios en sus cadenas cuando los necesita.
- `Leer(variable)` espera un valor desde el panel de consola y valida su tipo. Si faltan datos, la ejecución los solicita uno a uno.

## 2. Componentes léxicos

| Token | Expresión regular / reconocimiento | Ejemplo |
|---|---|---|
| Reservadas | Palabras exactas reconocidas tras identificar `[A-Za-z_][A-Za-z0-9_]*` | `Definir`, `SiNo` |
| IDENTIFICADOR | `[A-Za-z_][A-Za-z0-9_]*` salvo reservadas | `total_1` |
| NUMERO | `\d+(\.\d+)?` | `10`, `2.75` |
| CADENA | `"(?:\\["\\ntr]|[^"\\\n])*"` | `"Hola"` |
| Aritméticos | `+`, `-`, `*`, `/` | `+` |
| Asignación | `=` | `=` |
| Comparadores | `==`, `!=`, `<`, `<=`, `>`, `>=` | `>=` |
| Agrupación / signos | `(`, `)`, `,`, `;` | `;` |
| Ignorados | Espacios, saltos, `//` hasta fin de línea | `// nota` |

El analizador léxico implementa una colección de expresiones regulares con precedencia: primero cadenas y operadores largos, después los operadores simples. Un barrido izquierda-a-derecha produce tokens con tipo, lexema, línea y columna. El autómata que reconoce un identificador puede describirse con estado inicial `q0`, transición `letra/_` a `q1` y bucle `letra/dígito/_` en `q1` (estado de aceptación). Los caracteres inválidos originan errores léxicos.

## 3. Gramática independiente de contexto (BNF extendida)

**Símbolo inicial:** `<programa>`.

**No terminales:** `<programa>`, `<bloque>`, `<instruccion>`, `<declaracion>`, `<asignacion>`, `<lectura>`, `<escritura>`, `<lista_exp>`, `<cola_exp>`, `<condicional>`, `<opcional_sino>`, `<condicion>`, `<relop>`, `<expresion>`, `<resto_expresion>`, `<termino>`, `<resto_termino>`, `<factor>`, `<tipo>`.

**Terminales:** `ALGORITMO`, `FINALGORITMO`, `DEFINIR`, `COMO`, `ENTERO`, `DECIMAL`, `TEXTO`, `LEER`, `ESCRIBIR`, `SI`, `ENTONCES`, `SINO`, `FINSI`, `IDENTIFICADOR`, `NUMERO`, `CADENA`, `=`, `==`, `!=`, `<`, `<=`, `>`, `>=`, `+`, `-`, `*`, `/`, `(`, `)`, `,`, `;`.

Las palabras reservadas corresponden a los tokens que entrega el analizador léxico; `ε` representa la cadena vacía.

```bnf
<programa>         ::= ALGORITMO IDENTIFICADOR <bloque> FINALGORITMO
<bloque>           ::= <instruccion> <bloque> | ε
<instruccion>      ::= <declaracion> | <asignacion> | <lectura> | <escritura> | <condicional>
<declaracion>      ::= DEFINIR IDENTIFICADOR COMO <tipo> ;
<tipo>             ::= ENTERO | DECIMAL | TEXTO
<asignacion>       ::= IDENTIFICADOR = <expresion> ;
<lectura>          ::= LEER ( IDENTIFICADOR ) ;
<escritura>        ::= ESCRIBIR ( <lista_exp> ) ;
<lista_exp>        ::= <expresion> <cola_exp>
<cola_exp>         ::= , <expresion> <cola_exp> | ε
<condicional>      ::= SI <condicion> ENTONCES <bloque> <opcional_sino> FINSI
<opcional_sino>    ::= SINO <bloque> | ε
<condicion>        ::= <expresion> <relop> <expresion>
<relop>            ::= == | != | < | <= | > | >=
<expresion>        ::= <termino> <resto_expresion>
<resto_expresion>  ::= + <termino> <resto_expresion>
                     | - <termino> <resto_expresion> | ε
<termino>          ::= <factor> <resto_termino>
<resto_termino>    ::= * <factor> <resto_termino>
                     | / <factor> <resto_termino> | ε
<factor>           ::= NUMERO | CADENA | IDENTIFICADOR | ( <expresion> )
                     | + <factor> | - <factor>
```

`<bloque>` se termina según el contexto: `FINALGORITMO` para el programa, `SINO` o `FINSI` para el bloque verdadero y `FINSI` para el bloque falso. El parser descendente recursivo implementa estas producciones con las funciones `analizar`, `bloque`, `instruccion`, `expresion`, `termino` y `factor`. La estructura aritmética implementa precedencia sin recurrencia izquierda.

## 4. Reglas semánticas

La gramática valida la **forma** del programa. El intérprete verifica además:

1. Una variable debe haberse declarado antes de su primer uso y solo puede declararse una vez durante la ruta de ejecución.
2. Una variable recién declarada no tiene valor: leerla produce error hasta asignarla o introducir un dato con `Leer`.
3. `Entero` exige valor entero; `Decimal` admite enteros o decimales; `Texto` exige cadenas.
4. Las operaciones `+ - * /` son numéricas. La división obtiene un valor numérico decimal y se rechaza un divisor igual a cero. Puede asignarse a `Entero` si el resultado es matemáticamente entero.
5. `Si` ejecuta **solo** la rama correspondiente, y `SiNo` es opcional. Puede haber `Si` anidados.
6. Una expresión compara números entre sí, o compara textos con igualdad/desigualdad.
7. Los errores léxicos y sintácticos impiden toda ejecución; los errores de ejecución detienen el programa en la instrucción afectada.
8. No se ejecuta texto como código Python; no existen imports, ejecución de comandos ni acceso a archivos desde el pseudolenguaje.

## 5. Cinco programas válidos

**V1. Salida simple**
```text
Algoritmo Hola
    Escribir("Hola");
FinAlgoritmo
```

**V2. Variable entera**
```text
Algoritmo Numero
    Definir n Como Entero;
    n = 9;
    Escribir(n);
FinAlgoritmo
```

**V3. Cálculo con paréntesis**
```text
Algoritmo Operacion
    Definir r Como Decimal;
    r = (2 + 3) / 2;
    Escribir(r);
FinAlgoritmo
```

**V4. Entrada de texto**
```text
Algoritmo Nombre
    Definir nombre Como Texto;
    Leer(nombre);
    Escribir("Hola ", nombre);
FinAlgoritmo
```

**V5. Condición**
```text
Algoritmo Comparar
    Definir x Como Entero;
    x = 7;
    Si x > 5 Entonces
        Escribir("Alto");
    SiNo
        Escribir("Bajo");
    FinSi
FinAlgoritmo
```

## 6. Cinco programas inválidos

**I1. Falta el delimitador inicial**
```text
Escribir("Hola");
FinAlgoritmo
```
Error sintáctico: falta `Algoritmo`.

**I2. Falta punto y coma**
```text
Algoritmo ErrorDos
    Definir x Como Entero
FinAlgoritmo
```
Error sintáctico: falta `;`.

**I3. Literal no cerrado**
```text
Algoritmo ErrorTres
    Escribir("Hola);
FinAlgoritmo
```
Error léxico: cadena sin cerrar.

**I4. Falta `FinSi`**
```text
Algoritmo ErrorCuatro
    Si 2 > 1 Entonces
        Escribir("Sí");
FinAlgoritmo
```
Error sintáctico: se requiere cerrar el condicional con `FinSi`.

**I5. Carácter no admitido**
```text
Algoritmo ErrorCinco
    Escribir(2 @ 3);
FinAlgoritmo
```
Error léxico: `@` no es un token del lenguaje.

## 7. Arquitectura

```text
Editor HTML/CSS/JS
     | POST /api/analizar o /api/ejecutar
     v
Servidor HTTP de Python (app.py)
     v
Analizador lexico (expresiones regulares)
     v
Lista de tokens con posicion de origen
     v
Parser descendente recursivo (GIC)
     v
Arbol de sintaxis abstracta (AST)
     v
Interprete de instrucciones y expresiones
     v
Salida, variables, peticiones de Leer o errores
     v
Consola, tabla de tokens y campo de entrada
```

El árbol sintáctico se construye **completo antes de comenzar la ejecución**. Cuando `Leer` necesita datos, el navegador solicita el valor en un campo controlado y reenvía la lista de entradas ya reunidas; la interpretación reinicia de forma determinista. No se soporta ejecución arbitraria del sistema anfitrión.
