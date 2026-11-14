# Pruebas de ColombiaScript: lexer, parser, árbol, intérprete y requerimientos finales.
#
#     python pruebas.py
#
# Lo ESPERADO se calculó a mano ANTES de ejecutar (columna = posición del primer
# carácter de la pieza, contando desde 1 en cada línea). Después se compara con la
# salida real del lexer.

import builtins
import io
import os
import sys
from contextlib import redirect_stdout

import main
from interprete import Interprete
from lexer import tokenizar
from main import imprimir_tokens
from parser import Parser
from tokens import Token, ErrorLexico

CARPETA = os.path.dirname(os.path.abspath(__file__))
RUTA_EJEMPLO = os.path.join(CARPETA, "programas", "ejemplo.txt")

resultados = []


def toks(*tuplas):
    # Atajo para escribir lo esperado: ("TIPO", "Pille", 1, 1) -> Token(...)
    return [Token(*t) for t in tuplas]


ultimo_punto = None


def lineas(valor):
    # Convierte lo esperado/obtenido en una lista de líneas de texto para mostrar:
    # una lista de Token (un token por línea), una lista de textos, o un solo texto.
    if isinstance(valor, list):
        return [str(x) for x in valor]
    return [str(valor)]


def verificar(punto, nombre, entrada, esperado, real):
    # Compara lo esperado (calculado a mano) con lo obtenido y MUESTRA ambos lado a
    # lado, línea por línea, para que se vea qué token reconoció el lexer.
    global ultimo_punto
    if punto != ultimo_punto:
        print("=" * 78)
        print(f"PUNTO {punto}")
        print("=" * 78)
        ultimo_punto = punto

    coincide = (real == esperado)
    resultados.append(coincide)

    exp, obt = lineas(esperado), lineas(real)
    ancho = max(len(x) for x in exp + ["ESPERADO (a mano)"])
    print(f"[{punto}] {nombre}")
    print(f"  entrada : {entrada!r}")
    print(f"  {'ESPERADO (a mano)':<{ancho}}  |  OBTENIDO")
    for k in range(max(len(exp), len(obt))):
        a = exp[k] if k < len(exp) else ""
        b = obt[k] if k < len(obt) else ""
        print(f"  {a:<{ancho}}  |  {b}   {'✓' if a == b else '✗'}")
    print(f"  resultado: {'PASA' if coincide else 'FALLA'}")
    print()


def correr(codigo, modo="ejecutar", entradas=None):
    # Pasa el código por main.ejecutar (las tres fases) y devuelve lo que se imprimió,
    # línea por línea. entradas: lo que "escribiría" el usuario cuando el programa usa leer().
    teclado = iter(entradas or [])
    interprete = Interprete(entrada=lambda pregunta: next(teclado))
    salida = io.StringIO()
    with redirect_stdout(salida):
        main.ejecutar(codigo, interprete, modo)
    return salida.getvalue().splitlines()


def primera(codigo):
    # Solo la primera línea de la salida (el mensaje de un error)
    return correr(codigo)[:1]


def probar(punto, nombre, entrada, esperado):
    # esperado es una lista de Token, o un texto si se espera un error léxico
    try:
        real = tokenizar(entrada)
    except ErrorLexico as e:
        real = str(e)
    verificar(punto, nombre, entrada, esperado, real)


# ---------------- Puntos 4, 5, 6 y 6.1 (ahora con Token y EOF) ----------------

probar("4", "Pille es un TIPO y edad un IDENTIFICADOR",
       "Pille edad",
       toks(("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "edad", 1, 7), ("EOF", "", 1, 11)))
probar("4", "Pillesito NO se parte en Pille + sito",
       "Pillesito",
       toks(("IDENTIFICADOR", "Pillesito", 1, 1), ("EOF", "", 1, 10)))
probar("4", "pille en minúscula no es el tipo (distingue mayúsculas)",
       "pille edad",
       toks(("IDENTIFICADOR", "pille", 1, 1), ("IDENTIFICADOR", "edad", 1, 7), ("EOF", "", 1, 11)))

probar("5", "declaración completa con espacios",
       "Pille edad := 18",
       toks(("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "edad", 1, 7),
            ("ASIGNACION", ":=", 1, 12), ("NUMERO", "18", 1, 15), ("EOF", "", 1, 17)))
probar("5", "declaración sin espacios alrededor de :=",
       "Pille edad:=18",
       toks(("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "edad", 1, 7),
            ("ASIGNACION", ":=", 1, 11), ("NUMERO", "18", 1, 13), ("EOF", "", 1, 15)))
probar("5", ">= se lee completo (el símbolo más largo primero)",
       "Si edad >= 18",
       toks(("RESERVADA", "Si", 1, 1), ("IDENTIFICADOR", "edad", 1, 4),
            ("COMPARADOR", ">=", 1, 9), ("NUMERO", "18", 1, 12), ("EOF", "", 1, 14)))
probar("5", "asignación estilo Java (=) produce error",
       "Pille edad = 18",
       "Error léxico en línea 1, columna 12: la asignación se escribe ':=' (el '=' solo sirve para comparar)")
probar("5", "fin de instrucción estilo Java (;) produce error",
       "Pille edad := 18;",
       "Error léxico en línea 1, columna 17: carácter ';' no reconocido")
probar("5", ": suelto produce error",
       "Pille edad : 18",
       "Error léxico en línea 1, columna 12: se esperaba '=' después de ':' (la asignación se escribe :=)")

probar("6", "comentario al final no cambia los tokens",
       "Pille edad := 18 // mayor de edad",
       toks(("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "edad", 1, 7),
            ("ASIGNACION", ":=", 1, 12), ("NUMERO", "18", 1, 15), ("EOF", "", 1, 34)))
probar("6", "la línea siguiente conserva su número de línea",
       "Pille edad := 18 // mayor de edad\nPille hora := 23",
       toks(("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "edad", 1, 7),
            ("ASIGNACION", ":=", 1, 12), ("NUMERO", "18", 1, 15),
            ("TIPO", "Pille", 2, 1), ("IDENTIFICADOR", "hora", 2, 7),
            ("ASIGNACION", ":=", 2, 12), ("NUMERO", "23", 2, 15), ("EOF", "", 2, 17)))
probar("6", "un comentario con símbolos raros se ignora completo",
       "// $ @ # ; 3.4.5",
       toks(("EOF", "", 1, 17)))

probar("6.1", "@ en la línea 1",
       "Pille x := 5 @",
       "Error léxico en línea 1, columna 14: carácter '@' no reconocido")
probar("6.1", "el mismo error en la línea 2 reporta línea 2",
       "Pille x := 5\nPille y := @",
       "Error léxico en línea 2, columna 12: carácter '@' no reconocido")
probar("6.1", "un comentario antes no descuadra la línea",
       "// nota\nPille x := $",
       "Error léxico en línea 2, columna 12: carácter '$' no reconocido")
probar("6.1", "la columna cuenta los espacios del comienzo",
       "  Pille x := #",
       "Error léxico en línea 1, columna 14: carácter '#' no reconocido")
probar("6.1", "cadena sin cerrar",
       'Si x = 1 Eche mostrar "hola',
       "Error léxico en línea 1, columna 23: cadena sin cerrar, falta la comilla final")

# ---------------- Tarea 8: delimitadores ----------------

probar("8", "paréntesis y coma con columnas correctas",
       "(a, 2)",
       toks(("SIMBOLO", "(", 1, 1), ("IDENTIFICADOR", "a", 1, 2), ("SIMBOLO", ",", 1, 3),
            ("NUMERO", "2", 1, 5), ("SIMBOLO", ")", 1, 6), ("EOF", "", 1, 7)))
probar("8", "llaves",
       "{a}",
       toks(("SIMBOLO", "{", 1, 1), ("IDENTIFICADOR", "a", 1, 2),
            ("SIMBOLO", "}", 1, 3), ("EOF", "", 1, 4)))
probar("8", "punto entre dos nombres es SIMBOLO",
       "System.out",
       toks(("IDENTIFICADOR", "System", 1, 1), ("SIMBOLO", ".", 1, 7),
            ("IDENTIFICADOR", "out", 1, 8), ("EOF", "", 1, 11)))
probar("8", "punto dentro de un número sigue siendo parte del número",
       "Pille t := 3.14",
       toks(("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "t", 1, 7), ("ASIGNACION", ":=", 1, 9),
            ("NUMERO", "3.14", 1, 12), ("EOF", "", 1, 16)))
probar("8", "decimal negativo",
       "Pille t := -0.5",
       toks(("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "t", 1, 7), ("ASIGNACION", ":=", 1, 9),
            ("NUMERO", "-0.5", 1, 12), ("EOF", "", 1, 16)))
probar("8", "punto sin dígito detrás no es decimal",
       "3.",
       toks(("NUMERO", "3", 1, 1), ("SIMBOLO", ".", 1, 2), ("EOF", "", 1, 3)))

# ---------------- Tarea 9: operadores de dos caracteres ----------------

probar("9", "x == 5 da 3 tokens (más EOF)",
       "x == 5",
       toks(("IDENTIFICADOR", "x", 1, 1), ("COMPARADOR", "==", 1, 3),
            ("NUMERO", "5", 1, 6), ("EOF", "", 1, 7)))
probar("9", "x = = 5 da 4 tokens (más EOF)",
       "x = = 5",
       toks(("IDENTIFICADOR", "x", 1, 1), ("COMPARADOR", "=", 1, 3),
            ("COMPARADOR", "=", 1, 5), ("NUMERO", "5", 1, 7), ("EOF", "", 1, 8)))
probar("9", "!= <= >= < >",
       "a != b <= c >= d < e > f",
       toks(("IDENTIFICADOR", "a", 1, 1), ("COMPARADOR", "!=", 1, 3), ("IDENTIFICADOR", "b", 1, 6),
            ("COMPARADOR", "<=", 1, 8), ("IDENTIFICADOR", "c", 1, 11), ("COMPARADOR", ">=", 1, 13),
            ("IDENTIFICADOR", "d", 1, 16), ("COMPARADOR", "<", 1, 18), ("IDENTIFICADOR", "e", 1, 20),
            ("COMPARADOR", ">", 1, 22), ("IDENTIFICADOR", "f", 1, 24), ("EOF", "", 1, 25)))
probar("9", "! solo (sin =) es error léxico",
       "x ! 5",
       "Error léxico en línea 1, columna 3: carácter '!' no reconocido")

# ---------------- Operadores aritméticos + - * / ----------------

probar("9", "(a+b)*2 con paréntesis y operadores",
       "(a+b)*2",
       toks(("SIMBOLO", "(", 1, 1), ("IDENTIFICADOR", "a", 1, 2), ("OPERADOR", "+", 1, 3),
            ("IDENTIFICADOR", "b", 1, 4), ("SIMBOLO", ")", 1, 5), ("OPERADOR", "*", 1, 6),
            ("NUMERO", "2", 1, 7), ("EOF", "", 1, 8)))
probar("9", "declaración con expresión: Pille c := (a+b)*2",
       "Pille c := (a+b)*2",
       toks(("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "c", 1, 7), ("ASIGNACION", ":=", 1, 9),
            ("SIMBOLO", "(", 1, 12), ("IDENTIFICADOR", "a", 1, 13), ("OPERADOR", "+", 1, 14),
            ("IDENTIFICADOR", "b", 1, 15), ("SIMBOLO", ")", 1, 16), ("OPERADOR", "*", 1, 17),
            ("NUMERO", "2", 1, 18), ("EOF", "", 1, 19)))
probar("9", "resta y división: a - b / 2",
       "a - b / 2",
       toks(("IDENTIFICADOR", "a", 1, 1), ("OPERADOR", "-", 1, 3), ("IDENTIFICADOR", "b", 1, 5),
            ("OPERADOR", "/", 1, 7), ("NUMERO", "2", 1, 9), ("EOF", "", 1, 10)))
probar("9", "a-5 es una resta (el - sigue a un nombre), no un número negativo",
       "a-5",
       toks(("IDENTIFICADOR", "a", 1, 1), ("OPERADOR", "-", 1, 2),
            ("NUMERO", "5", 1, 3), ("EOF", "", 1, 4)))
probar("9", "(a+b)-5 también es una resta (el - sigue a un paréntesis)",
       "(a+b)-5",
       toks(("SIMBOLO", "(", 1, 1), ("IDENTIFICADOR", "a", 1, 2), ("OPERADOR", "+", 1, 3),
            ("IDENTIFICADOR", "b", 1, 4), ("SIMBOLO", ")", 1, 5), ("OPERADOR", "-", 1, 6),
            ("NUMERO", "5", 1, 7), ("EOF", "", 1, 8)))
probar("9", ":= -5 sigue siendo un número negativo",
       "Pille f := -5",
       toks(("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "f", 1, 7), ("ASIGNACION", ":=", 1, 9),
            ("NUMERO", "-5", 1, 12), ("EOF", "", 1, 14)))
probar("9", "- separado del número ahora es el operador -",
       "Pille frio := - 5",
       toks(("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "frio", 1, 7), ("ASIGNACION", ":=", 1, 12),
            ("OPERADOR", "-", 1, 15), ("NUMERO", "5", 1, 17), ("EOF", "", 1, 18)))
probar("9", "// y /* siguen siendo comentarios, no divisiones",
       "a / b // resto\nc /* x */ / d",
       toks(("IDENTIFICADOR", "a", 1, 1), ("OPERADOR", "/", 1, 3), ("IDENTIFICADOR", "b", 1, 5),
            ("IDENTIFICADOR", "c", 2, 1), ("OPERADOR", "/", 2, 11), ("IDENTIFICADOR", "d", 2, 13),
            ("EOF", "", 2, 14)))

# ---------------- Tarea 10: reservadas de control y booleanos ----------------

probar("10", "Si es RESERVADA, Sillo y Tin_x son IDENTIFICADOR",
       "Si Sillo Tin_x",
       toks(("RESERVADA", "Si", 1, 1), ("IDENTIFICADOR", "Sillo", 1, 4),
            ("IDENTIFICADOR", "Tin_x", 1, 10), ("EOF", "", 1, 15)))
probar("10", "Eche, Tin, Tan y mostrar son RESERVADA; Melo y Paila BOOLEANO",
       "Eche Tin Tan mostrar Melo Paila",
       toks(("RESERVADA", "Eche", 1, 1), ("RESERVADA", "Tin", 1, 6), ("RESERVADA", "Tan", 1, 10),
            ("RESERVADA", "mostrar", 1, 14), ("BOOLEANO", "Melo", 1, 22),
            ("BOOLEANO", "Paila", 1, 27), ("EOF", "", 1, 32)))
probar("10", "Melosa no es el booleano Melo",
       "Melosa",
       toks(("IDENTIFICADOR", "Melosa", 1, 1), ("EOF", "", 1, 7)))

# ---------------- Tarea 11: comentarios de bloque ----------------

probar("11", "comentario de 3 líneas deja la segunda declaración en la línea 4",
       "Pille a := 1 /* uno\ndos\ntres */\nPille b := 2",
       toks(("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "a", 1, 7), ("ASIGNACION", ":=", 1, 9),
            ("NUMERO", "1", 1, 12),
            ("TIPO", "Pille", 4, 1), ("IDENTIFICADOR", "b", 4, 7), ("ASIGNACION", ":=", 4, 9),
            ("NUMERO", "2", 4, 12), ("EOF", "", 4, 13)))
probar("11", "la columna se reinicia después del cierre en la misma línea",
       "/* a\nb */ x",
       toks(("IDENTIFICADOR", "x", 2, 6), ("EOF", "", 2, 7)))
probar("11", "comentario de bloque en una sola línea",
       "a /* x */ b",
       toks(("IDENTIFICADOR", "a", 1, 1), ("IDENTIFICADOR", "b", 1, 11), ("EOF", "", 1, 12)))
probar("11", "comentario sin cerrar: error en la línea donde empezó",
       "Pille a := 1 /* sin cerrar",
       "Error léxico en línea 1, columna 14: comentario sin cerrar")
probar("11", "comentario sin cerrar que empezó en la línea 2",
       "Pille a := 1\n  /* sin\ncerrar",
       "Error léxico en línea 2, columna 3: comentario sin cerrar")
probar("11", "/*/ no cuenta como comentario cerrado",
       "/*/",
       "Error léxico en línea 1, columna 1: comentario sin cerrar")

# ---------------- Tarea 12: EOF ----------------

probar("12", "una declaración termina con EOF",
       "Pille x := 5",
       toks(("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "x", 1, 7), ("ASIGNACION", ":=", 1, 9),
            ("NUMERO", "5", 1, 12), ("EOF", "", 1, 13)))
probar("12", "texto vacío produce solo EOF",
       "",
       toks(("EOF", "", 1, 1)))
probar("12", "texto que termina en salto de línea: EOF al comienzo de la línea siguiente",
       "x\n",
       toks(("IDENTIFICADOR", "x", 1, 1), ("EOF", "", 2, 1)))

# ---------------- Tarea 13: clase Token ----------------

t = Token("NUMERO", "5", 1, 9)
verificar("13", "Token guarda cada dato con nombre", "Token('NUMERO', '5', 1, 9)",
          ["tipo=NUMERO", "texto=5", "linea=1", "columna=9"],
          [f"tipo={t.tipo}", f"texto={t.texto}", f"linea={t.linea}", f"columna={t.columna}"])
verificar("13", "__str__ imprime algo legible", "str(Token('NUMERO', '5', 1, 9))",
          "NUMERO('5') en 1:9", str(t))
verificar("13", "tokenizar devuelve objetos Token (un token por línea)", "x := 5",
          ["IDENTIFICADOR('x') en 1:1", "ASIGNACION(':=') en 1:3",
           "NUMERO('5') en 1:6", "EOF('') en 1:7"],
          [str(x) for x in tokenizar("x := 5")])

# ---------------- Tarea 14: ErrorLexico ----------------

entrada_error = "Pille a := 1\nPille b := 2 @"
try:
    tokenizar(entrada_error)
    obtenido_error = ["no lanzó ErrorLexico"]
except ErrorLexico as e:
    obtenido_error = [f"e.linea={e.linea}", f"e.columna={e.columna}", f"mensaje={e}"]
verificar("14", "ErrorLexico se atrapa con try/except y expone línea y columna", entrada_error,
          ["e.linea=2", "e.columna=14",
           "mensaje=Error léxico en línea 2, columna 14: carácter '@' no reconocido"],
          obtenido_error)

# ---------------- Tarea 16: ejemplo.txt ----------------

with open(RUTA_EJEMPLO, encoding="utf-8") as f:
    ejemplo = f.read()
tokens_ejemplo = tokenizar(ejemplo)
verificar("16", "ejemplo.txt tiene al menos 10 líneas y se tokeniza sin errores", "ejemplo.txt",
          ["líneas >= 10: sí", "último token: EOF"],
          [f"líneas >= 10: {'sí' if len(ejemplo.splitlines()) >= 10 else 'no'}",
           f"último token: {tokens_ejemplo[-1].tipo}"])
# Calculado a mano: la línea 1 es comentario; líneas 2 y 3 son declaraciones.
esperado_ejemplo = toks(
    ("TIPO", "Pille", 2, 1), ("IDENTIFICADOR", "edad", 2, 7), ("ASIGNACION", ":=", 2, 12), ("NUMERO", "20", 2, 15),
    ("TIPO", "Pille", 3, 1), ("IDENTIFICADOR", "temperatura", 3, 7), ("ASIGNACION", ":=", 3, 19),
    ("NUMERO", "31.5", 3, 22))
verificar("16", "los tokens de las líneas 2 y 3 coinciden con lo calculado a mano",
          "\n".join(ejemplo.splitlines()[:3]),
          esperado_ejemplo, tokens_ejemplo[:len(esperado_ejemplo)])

# ---------------- Sesión 3, punto 3: clase Parser ----------------

p = Parser(tokenizar("Pille x := 5"))
verificar("Parser", "el Parser guarda la lista de tokens y empieza en la posición 0", "Pille x := 5",
          ["len(p.tokens)=5", "p.pos=0"],
          [f"len(p.tokens)={len(p.tokens)}", f"p.pos={p.pos}"])
verificar("Parser", "actual() mira el token SIN moverse (dos llamadas dan lo mismo)", "Pille x := 5",
          ["TIPO('Pille') en 1:1", "TIPO('Pille') en 1:1", "pos=0"],
          [str(p.actual()), str(p.actual()), f"pos={p.pos}"])
devuelto = p.avanzar()
verificar("Parser", "avanzar() devuelve el token actual y pasa al siguiente", "Pille x := 5",
          ["devuelto=TIPO('Pille') en 1:1", "actual=IDENTIFICADOR('x') en 1:7", "pos=1"],
          [f"devuelto={devuelto}", f"actual={p.actual()}", f"pos={p.pos}"])

for _ in range(10):                 # muchas más veces de las que hay tokens
    p.avanzar()
verificar("Parser", "en EOF avanzar() ya no se mueve (no se sale de la lista)", "Pille x := 5",
          ["actual=EOF('') en 1:13", "pos=4"],
          [f"actual={p.actual()}", f"pos={p.pos}"])

# Pregunta de la sustentación: dos objetos Parser con listas distintas, se avanza solo uno.
p1 = Parser(tokenizar("Pille a := 1"))
p2 = Parser(tokenizar("Si a == 1 Eche b"))
p1.avanzar()
p1.avanzar()
verificar("Parser", "dos objetos Parser son independientes: avanzar p1 no mueve a p2",
          "p1: Pille a := 1   p2: Si a == 1 Eche b",
          ["p1.pos=2", "p1.actual=ASIGNACION(':=') en 1:9", "p2.pos=0", "p2.actual=RESERVADA('Si') en 1:1"],
          [f"p1.pos={p1.pos}", f"p1.actual={p1.actual()}", f"p2.pos={p2.pos}", f"p2.actual={p2.actual()}"])

# Lo que imprime main.py con programa.txt (calculado a mano)
salida = io.StringIO()
with redirect_stdout(salida):
    imprimir_tokens(Parser(tokenizar("Pille x := 5")))
verificar("Parser", "main.py recorre con el Parser e imprime TODOS los tokens, incluido EOF", "Pille x := 5",
          ["TIPO('Pille') en 1:1", "IDENTIFICADOR('x') en 1:7", "ASIGNACION(':=') en 1:9",
           "NUMERO('5') en 1:12", "EOF('') en 1:13"],
          salida.getvalue().splitlines())

# ================= 13 de noviembre: el parser construye un árbol =================

verificar("Árbol", "programa.txt de la guía: dos declaraciones", "Pille edad := 20\nPille nota := edad / 4.0",
          ["Programa",
           "  Declaracion Pille edad",
           "    Numero 20",
           "  Declaracion Pille nota",
           "    OperacionBinaria /",
           "      Variable edad",
           "      Numero 4.0"],
          correr("Pille edad := 20\nPille nota := edad / 4.0", "arbol"))
verificar("Árbol", "la resta se agrupa por la izquierda: (10 - 3) - 2", "Pille r := 10 - 3 - 2",
          ["Programa",
           "  Declaracion Pille r",
           "    OperacionBinaria -",
           "      OperacionBinaria -",
           "        Numero 10",
           "        Numero 3",
           "      Numero 2"],
          correr("Pille r := 10 - 3 - 2", "arbol"))
verificar("Árbol", "la multiplicación queda más abajo que la suma", "Pille total := a + 5 * 2",
          ["Programa",
           "  Declaracion Pille total",
           "    OperacionBinaria +",
           "      Variable a",
           "      OperacionBinaria *",
           "        Numero 5",
           "        Numero 2"],
          correr("Pille total := a + 5 * 2", "arbol"))
verificar("Árbol", "Tan queda arriba de Tin, y Tin arriba de la comparación", "Si a > 1 Tin Nel b Tan c Eche { }",
          ["Programa",
           "  Si",
           "    Logica Tan",
           "      Logica Tin",
           "        Comparacion >",
           "          Variable a",
           "          Numero 1",
           "        Negacion Nel",
           "          Variable b",
           "      Variable c",
           "    Eche"],
          correr("Si a > 1 Tin Nel b Tan c Eche { }", "arbol"))

# ================= Entregable 14 de noviembre: errores sintácticos =================

verificar("Sintaxis", "falta el valor después de :=", "Pille x :=",
          ["Error sintáctico en línea 1, columna 11: se esperaba un número, una variable o '(' y llegó el fin del archivo"],
          primera("Pille x :="))
verificar("Sintaxis", "dos operadores seguidos", "Pille y := 4 + * 2",
          ["Error sintáctico en línea 1, columna 16: se esperaba un número, una variable o '(' y llegó '*'"],
          primera("Pille y := 4 + * 2"))
verificar("Sintaxis", "paréntesis sin cerrar", "Pille z := (1 + 2\nmostrar(z)",
          ["Error sintáctico en línea 2, columna 1: se esperaba ')' y llegó 'mostrar'"],
          primera("Pille z := (1 + 2\nmostrar(z)"))
verificar("Sintaxis", "falta el nombre de la variable", "Pille := 5",
          ["Error sintáctico en línea 1, columna 7: se esperaba un IDENTIFICADOR y llegó ':='"],
          primera("Pille := 5"))
verificar("Sintaxis", "el condicional necesita Eche", "Si a > 1 { }",
          ["Error sintáctico en línea 1, columna 10: se esperaba 'Eche' y llegó '{'"],
          primera("Si a > 1 { }"))
verificar("Sintaxis", "una instrucción no puede empezar con un número", "Pille x := 5 6",
          ["Error sintáctico en línea 1, columna 14: se esperaba el inicio de una instrucción y llegó '6'"],
          primera("Pille x := 5 6"))

# ================= 14 de noviembre: el programa se ejecuta =================

verificar("Ejecución", "a + 5 * 2 con a = 3 da 13", "Pille a := 3\nPille total := a + 5 * 2\nmostrar(total)",
          ["13"], correr("Pille a := 3\nPille total := a + 5 * 2\nmostrar(total)"))
codigo_tipos = 'mostrar(7 / 2)\nmostrar(7 / 2.0)\nmostrar("ho" + "la")\nmostrar("hola" * 2)'
verificar("Ejecución", "operaciones entre tipos: se detiene en el *", codigo_tipos,
          ["3", "3.5", "hola", "Error semántico en línea 4, columna 16: no se puede usar '*' con textos"],
          correr(codigo_tipos)[:4])
verificar("Ejecución", "decisión de diseño: texto + número/booleano se unen", 'mostrar("Total: " + 3 + " " + Melo)',
          ["Total: 3 Melo"], correr('mostrar("Total: " + 3 + " " + Melo)'))
verificar("Ejecución", "la división entera corta hacia cero, como en Java", "mostrar(-7 / 2)",
          ["-3"], correr("mostrar(-7 / 2)"))
verificar("Semántica", "usar una variable no declarada", "mostrar(edad)",
          ["Error semántico en línea 1, columna 9: la variable 'edad' no ha sido declarada"],
          primera("mostrar(edad)"))
verificar("Semántica", "declarar dos veces la misma variable", "Pille x := 1\nPille x := 2",
          ["Error semántico en línea 2, columna 7: la variable 'x' ya fue declarada en la línea 1"],
          primera("Pille x := 1\nPille x := 2"))
verificar("Semántica", "guardar un valor de otro tipo", 'Pille n := 5\nn := "hola"',
          ["Error semántico en línea 2, columna 1: no se puede guardar un texto en la variable 'n' de tipo entero"],
          primera('Pille n := 5\nn := "hola"'))
verificar("Semántica", "un decimal acepta enteros (y los vuelve decimales)", "Pille p := 2.5\np := 3\nmostrar(p)",
          ["3.0"], correr("Pille p := 2.5\np := 3\nmostrar(p)"))
verificar("Semántica", "división por cero", "Pille d := 10 / 0",
          ["Error semántico en línea 1, columna 15: división por cero"],
          primera("Pille d := 10 / 0"))
verificar("Semántica", "lo anterior al error ya se mostró", "Pille a := 5\nmostrar(a)\nmostrar(b)",
          ["5", "Error semántico en línea 3, columna 9: la variable 'b' no ha sido declarada"],
          correr("Pille a := 5\nmostrar(a)\nmostrar(b)")[:2])
verificar("Errores", "main.py: mensaje, línea con ^ y línea/columna por separado", "Pille x := 5 @",
          ["Error léxico en línea 1, columna 14: carácter '@' no reconocido",
           "    Pille x := 5 @",
           "                 ^",
           "linea = 1, columna = 14"],
          correr("Pille x := 5 @"))
codigo_20 = ('Pille precio := 12000\nPille cantidad := 3\nPille total := precio * cantidad\n'
             'mostrar(total)\nPille promedio := total / 4.0\nmostrar(promedio)\n'
             'Pille mensaje := "Fin del calculo"\nmostrar(mensaje)')
verificar("Ejecución", "salida esperada del entregable del 20 de noviembre", codigo_20,
          ["36000", "9000.0", "Fin del calculo"], correr(codigo_20))

# ================= 20 de noviembre: las siete comprobaciones =================

verificar("Control", "1. el lexer separa == de := (en ColombiaScript la asignación es :=)", "a == b  /  a := b",
          ["COMPARADOR('==') en 1:3", "ASIGNACION(':=') en 1:3"],
          [correr("a == b", "tokens")[1], correr("a := b", "tokens")[1]])
verificar("Control", "2. condicional con Sino", 'Si 2 > 1 Eche { mostrar("si") } Sino { mostrar("no") }',
          ["si"], correr('Si 2 > 1 Eche { mostrar("si") } Sino { mostrar("no") }'))
verificar("Control", "3. condicional sin Sino", 'Si 1 > 2 Eche { mostrar("si") } mostrar("fin")',
          ["fin"], correr('Si 1 > 2 Eche { mostrar("si") } mostrar("fin")'))
verificar("Control", "4. ciclo Dele", "Pille n := 1 Dele n <= 3 Eche { mostrar(n) n := n + 1 }",
          ["1", "2", "3"], correr("Pille n := 1 Dele n <= 3 Eche { mostrar(n) n := n + 1 }"))
codigo_anidado = "Pille n := 1 Dele n <= 4 Eche { Si n > 2 Eche { mostrar(n) } n := n + 1 }"
verificar("Control", "5. un bloque dentro de otro", codigo_anidado, ["3", "4"], correr(codigo_anidado))
verificar("Control", "6. bloque sin cerrar", "Si 1 < 2 Eche { mostrar(1)",
          ["Error sintáctico en línea 1, columna 27: falta '}' para cerrar el bloque abierto en la línea 1"],
          primera("Si 1 < 2 Eche { mostrar(1)"))
salida_infinita = correr("Pille n := 1 Dele n <= 3 Eche { mostrar(n) }")
verificar("Control", "7. ciclo infinito: muchos 1 y después el error", "Pille n := 1 Dele n <= 3 Eche { mostrar(n) }",
          ["100000 veces '1'",
           "Error semántico en línea 1, columna 14: el ciclo superó 100000 vueltas; "
           "¿falta actualizar la variable de la condición?"],
          [f"{salida_infinita.count('1')} veces '1'", salida_infinita[100000]])
codigo_final = ("Pille n := 1\nPille suma := 0\nDele n <= 5 Eche {\n    suma := suma + n\n    n := n + 1\n}\n"
                "mostrar(suma)\nSi suma > 10 Eche {\n    mostrar(\"grande\")\n} Sino {\n    mostrar(\"pequeño\")\n}")
verificar("Control", "programa completo del 20 de noviembre", codigo_final,
          ["15", "grande"], correr(codigo_final))

# ================= Requerimientos obligatorios =================

codigo_alcance = "Si 1 < 2 Eche {\n    Pille x := 5\n}\nmostrar(x)"
verificar("Req 1", "alcance de bloques: x deja de existir al cerrar el bloque", codigo_alcance,
          ["Error semántico en línea 4, columna 9: la variable 'x' no ha sido declarada"],
          primera(codigo_alcance))
verificar("Req 1", "desde un bloque sí se ve (y se cambia) la variable de afuera",
          "Pille a := 1 Si Melo Eche { a := a + 1 } mostrar(a)",
          ["2"], correr("Pille a := 1 Si Melo Eche { a := a + 1 } mostrar(a)"))
codigo_logico = 'Pille n := 7\nSi n >= 1 Tin n <= 10 Eche {\n    mostrar("en rango")\n}'
verificar("Req 2", "Tin (y): n entre 1 y 10", codigo_logico, ["en rango"], correr(codigo_logico))
verificar("Req 2", "Tan (o) y Nel (no)", "mostrar(Paila Tan Melo) mostrar(Nel Melo) mostrar(Nel 1 > 2 Tin Melo)",
          ["Melo", "Paila", "Melo"], correr("mostrar(Paila Tan Melo) mostrar(Nel Melo) mostrar(Nel 1 > 2 Tin Melo)"))
verificar("Req 2", "Tin necesita booleanos", "mostrar(1 Tin Melo)",
          ["Error semántico en línea 1, columna 11: 'Tin' necesita una condición que dé Melo o Paila y recibió un entero"],
          primera("mostrar(1 Tin Melo)"))
codigo_negativos = "Pille x := -5\nPille y := -(x + 2)\nmostrar(y)"
verificar("Req 3", "números negativos y menos unario", codigo_negativos, ["3"], correr(codigo_negativos))
verificar("Req 3", "a - 5 sigue siendo una resta", "Pille a := 8 mostrar(a-5)", ["3"], correr("Pille a := 8 mostrar(a-5)"))
verificar("Req 4", "el error señala el código con ^", "Pille a := 1\nmostrar(edad)",
          ["Error semántico en línea 2, columna 9: la variable 'edad' no ha sido declarada",
           "    mostrar(edad)",
           "            ^",
           "linea = 2, columna = 9"],
          correr("Pille a := 1\nmostrar(edad)"))

# ================= Requerimientos electivos =================

verificar("Booleano", "una comparación se guarda en una variable", "Pille n := 5 Pille listo := n > 3 mostrar(listo)",
          ["Melo"], correr("Pille n := 5 Pille listo := n > 3 mostrar(listo)"))
verificar("Booleano", "Melo no es un entero (type y no isinstance)", "Pille n := 5 n := Melo",
          ["Error semántico en línea 1, columna 14: no se puede guardar un booleano en la variable 'n' de tipo entero"],
          primera("Pille n := 5 n := Melo"))
verificar("Booleano", "Si exige una condición booleana", "Si 5 Eche { }",
          ["Error semántico en línea 1, columna 1: 'Si' necesita una condición que dé Melo o Paila y recibió un entero"],
          primera("Si 5 Eche { }"))
verificar("Cuente", "ciclo con contador, i solo existe adentro", "Cuente i Desde 1 Hasta 3 Eche { mostrar(i) } mostrar(i)",
          ["1", "2", "3", "Error semántico en línea 1, columna 54: la variable 'i' no ha sido declarada"],
          correr("Cuente i Desde 1 Hasta 3 Eche { mostrar(i) } mostrar(i)")[:4])
verificar("Cuente", "los límites deben ser enteros", "Cuente i Desde 1 Hasta 2.5 Eche { }",
          ["Error semántico en línea 1, columna 1: Cuente necesita números enteros y recibió un decimal"],
          primera("Cuente i Desde 1 Hasta 2.5 Eche { }"))
verificar("Leer", "Pille x := leer() deduce el tipo de lo escrito", 'Pille e := leer() mostrar(e + 1)   (escribe 20)',
          ["21"], correr("Pille e := leer() mostrar(e + 1)", entradas=["20"]))
verificar("Leer", "x := leer() convierte al tipo de x, con error si no se puede", "Pille n := 0\nn := leer()   (escribe abc)",
          ["Error semántico en línea 2, columna 6: no se puede convertir 'abc' a entero"],
          correr("Pille n := 0\nn := leer()", entradas=["abc"])[:1])

# Modo interactivo: se simula lo que el usuario escribe reemplazando input()
lineas_usuario = iter(["Pille a := 2", "Dele a < 4 Eche {", "a := a + 1", "}", "mostrar(a)", "chao"])
input_original = builtins.input
builtins.input = lambda prompt="": next(lineas_usuario)
salida = io.StringIO()
try:
    with redirect_stdout(salida):
        main.modo_interactivo()
finally:
    builtins.input = input_original
verificar("Interactivo", "recuerda variables entre líneas y espera a que se cierre el bloque",
          "Pille a := 2 / Dele a < 4 Eche { / a := a + 1 / } / mostrar(a) / chao",
          ["ColombiaScript - modo interactivo. Escriba 'chao' para salir.", "4", "Nombre de Dios, nos pillamos."],
          salida.getvalue().splitlines())

# ================= Programas de muestra (presentación del lenguaje) =================

for archivo, esperado in [("tabla_del_3.txt", ["3", "6", "9", "12", "15"]),
                          ("factorial.txt", ["120"]),
                          ("promedio.txt", ["4.0", "aprueba"])]:
    with open(os.path.join(CARPETA, "programas", archivo), encoding="utf-8") as f:
        verificar("Muestras", f"programas/{archivo}", archivo, esperado, correr(f.read()))
verificar("Muestras", "programas/ejemplo.txt se ejecuta completo", "ejemplo.txt",
          ["Puede entrar", "Encendiendo el ventilador", "Saldo disponible: 45000.0", "Deuda: 0, saldo: 25000.0"],
          correr(ejemplo))

# ---------------- Resumen ----------------

print("=" * 78)
fallaron = len(resultados) - sum(resultados)
print(f"RESUMEN: {sum(resultados)} de {len(resultados)} pruebas coinciden con lo esperado a mano.")
if fallaron:
    print(f"FALLARON {fallaron} prueba(s): revisa las marcas ✗ de arriba.")
print("=" * 78)
sys.exit(1 if fallaron else 0)
