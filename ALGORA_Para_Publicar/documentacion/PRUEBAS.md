# Registro de las diez pruebas obligatorias

Fecha de ejecución: 2026-10-28.
Generación: `python documentacion/generar_registros.py` sobre el motor real.
Una prueba de error es aprobada si se detecta el error previsto, no si ejecuta código inválido.

**Resultado general: 10/10 aprobadas.**

## Prueba 01: Asignación y precedencia aritmética

**Código ingresado**

```text
Algoritmo AritmeticaBasica
    Definir a Como Entero;
    Definir b Como Entero;
    Definir resultado Como Entero;
    a = 10;
    b = 4;
    resultado = a + b * 2;
    Escribir("Resultado: ", resultado);
FinAlgoritmo
```

**Datos de entrada:** No aplica.

**Resultado esperado:** Resultado: 18

**Resultado obtenido (registro de ejecución):**

```text
Resultado: 18
```

**Estado de prueba:** APROBADA

---

## Prueba 02: Paréntesis y números decimales

**Código ingresado**

```text
Algoritmo ParentesisYDecimales
    Definir precio Como Decimal;
    Definir total Como Decimal;
    precio = 12.5;
    total = (precio + 2.5) / 3;
    Escribir("Total: ", total);
FinAlgoritmo
```

**Datos de entrada:** No aplica.

**Resultado esperado:** Total: 5

**Resultado obtenido (registro de ejecución):**

```text
Total: 5
```

**Estado de prueba:** APROBADA

---

## Prueba 03: Entrada de número entero

**Código ingresado**

```text
Algoritmo EntradaEdad
    Definir edad Como Entero;
    Leer(edad);
    Escribir("Edad ingresada: ", edad);
FinAlgoritmo
```

**Datos de entrada:** '21'

**Resultado esperado:** Edad ingresada: 21

**Resultado obtenido (registro de ejecución):**

```text
Edad ingresada: 21
```

**Estado de prueba:** APROBADA

---

## Prueba 04: Entrada y salida de texto

**Código ingresado**

```text
Algoritmo EntradaNombre
    Definir nombre Como Texto;
    Leer(nombre);
    Escribir("Hola, ", nombre, "!");
FinAlgoritmo
```

**Datos de entrada:** 'Ana'

**Resultado esperado:** Hola, Ana!

**Resultado obtenido (registro de ejecución):**

```text
Hola, Ana!
```

**Estado de prueba:** APROBADA

---

## Prueba 05: Condición verdadera

**Código ingresado**

```text
Algoritmo MayorDeEdad
    Definir edad Como Entero;
    edad = 20;
    Si edad >= 18 Entonces
        Escribir("Es mayor de edad");
    SiNo
        Escribir("Es menor de edad");
    FinSi
FinAlgoritmo
```

**Datos de entrada:** No aplica.

**Resultado esperado:** Es mayor de edad

**Resultado obtenido (registro de ejecución):**

```text
Es mayor de edad
```

**Estado de prueba:** APROBADA

---

## Prueba 06: Condición falsa

**Código ingresado**

```text
Algoritmo CondicionFalsa
    Definir nota Como Decimal;
    nota = 49.5;
    Si nota >= 61 Entonces
        Escribir("Aprobado");
    SiNo
        Escribir("Reprobado");
    FinSi
FinAlgoritmo
```

**Datos de entrada:** No aplica.

**Resultado esperado:** Reprobado

**Resultado obtenido (registro de ejecución):**

```text
Reprobado
```

**Estado de prueba:** APROBADA

---

## Prueba 07: Detección de símbolo inválido

**Código ingresado**

```text
Algoritmo CaracterInvalido
    Definir valor Como Entero;
    valor = 4 @ 2;
    Escribir(valor);
FinAlgoritmo
```

**Datos de entrada:** No aplica.

**Resultado esperado:** Error léxico, línea 3, carácter @

**Resultado obtenido (registro de ejecución):**

```text
Error lexico en linea 3, columna 15: Caracter no permitido: '@'.
```

**Estado de prueba:** APROBADA

---

## Prueba 08: Falta de punto y coma

**Código ingresado**

```text
Algoritmo PuntoYComa
    Definir x Como Entero;
    x = 7
    Escribir(x);
FinAlgoritmo
```

**Datos de entrada:** No aplica.

**Resultado esperado:** Error sintáctico, línea 4, falta ;

**Resultado obtenido (registro de ejecución):**

```text
Error sintactico en linea 4, columna 5: Falta ; al finalizar la asignacion (se encontro 'Escribir').
```

**Estado de prueba:** APROBADA

---

## Prueba 09: Control de división entre cero

**Código ingresado**

```text
Algoritmo DivisionCero
    Definir resultado Como Decimal;
    resultado = 5 / (3 - 3);
    Escribir(resultado);
FinAlgoritmo
```

**Datos de entrada:** No aplica.

**Resultado esperado:** Error de ejecución: división entre cero

**Resultado obtenido (registro de ejecución):**

```text
Error de ejecucion en linea 3, columna 19: Division entre cero. Revise el denominador.
```

**Estado de prueba:** APROBADA

---

## Prueba 10: Control de variable no declarada

**Código ingresado**

```text
Algoritmo VariableNoDeclarada
    total = 5;
    Escribir(total);
FinAlgoritmo
```

**Datos de entrada:** No aplica.

**Resultado esperado:** Error de ejecución: variable no declarada

**Resultado obtenido (registro de ejecución):**

```text
Error de ejecucion en linea 2, columna 5: La variable 'total' no esta declarada. Declarela con Definir.
```

**Estado de prueba:** APROBADA

---

# Evidencia del análisis léxico

Se analizaron los tokens del programa `01_aritmetica_basica.pseudo`.

| # | Lexema | Clase | Línea | Columna |
|---:|---|---|---:|---:|
| 1 | `Algoritmo` | `ALGORITMO` | 1 | 1 |
| 2 | `AritmeticaBasica` | `IDENTIFICADOR` | 1 | 11 |
| 3 | `Definir` | `DEFINIR` | 2 | 5 |
| 4 | `a` | `IDENTIFICADOR` | 2 | 13 |
| 5 | `Como` | `COMO` | 2 | 15 |
| 6 | `Entero` | `ENTERO` | 2 | 20 |
| 7 | `;` | `;` | 2 | 26 |
| 8 | `Definir` | `DEFINIR` | 3 | 5 |
| 9 | `b` | `IDENTIFICADOR` | 3 | 13 |
| 10 | `Como` | `COMO` | 3 | 15 |
| 11 | `Entero` | `ENTERO` | 3 | 20 |
| 12 | `;` | `;` | 3 | 26 |
| 13 | `Definir` | `DEFINIR` | 4 | 5 |
| 14 | `resultado` | `IDENTIFICADOR` | 4 | 13 |
| 15 | `Como` | `COMO` | 4 | 23 |
| 16 | `Entero` | `ENTERO` | 4 | 28 |
| 17 | `;` | `;` | 4 | 34 |
| 18 | `a` | `IDENTIFICADOR` | 5 | 5 |
| 19 | `=` | `=` | 5 | 7 |
| 20 | `10` | `NUMERO` | 5 | 9 |
| 21 | `;` | `;` | 5 | 11 |
| 22 | `b` | `IDENTIFICADOR` | 6 | 5 |
| 23 | `=` | `=` | 6 | 7 |
| 24 | `4` | `NUMERO` | 6 | 9 |
| 25 | `;` | `;` | 6 | 10 |
| 26 | `resultado` | `IDENTIFICADOR` | 7 | 5 |
| 27 | `=` | `=` | 7 | 15 |
| 28 | `a` | `IDENTIFICADOR` | 7 | 17 |
| 29 | `+` | `+` | 7 | 19 |
| 30 | `b` | `IDENTIFICADOR` | 7 | 21 |
| 31 | `*` | `*` | 7 | 23 |
| 32 | `2` | `NUMERO` | 7 | 25 |
| 33 | `;` | `;` | 7 | 26 |
| 34 | `Escribir` | `ESCRIBIR` | 8 | 5 |
| 35 | `(` | `(` | 8 | 13 |
| 36 | `"Resultado: "` | `CADENA` | 8 | 14 |
| 37 | `,` | `,` | 8 | 27 |
| 38 | `resultado` | `IDENTIFICADOR` | 8 | 29 |
| 39 | `)` | `)` | 8 | 38 |
| 40 | `;` | `;` | 8 | 39 |
| 41 | `FinAlgoritmo` | `FINALGORITMO` | 9 | 1 |

Total: 41 tokens.
En `documentacion/GRAMATICA.md` se documentan las expresiones regulares y el autómata del identificador.
