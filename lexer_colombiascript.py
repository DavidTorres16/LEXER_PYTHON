TIPOS = ["Pille"]
PALABRAS_RESERVADAS = ["Si", "Eche", "Tin", "Tan", "mostrar"]
BOOLEANOS = ["Melo", "Paila"]

SIMBOLOS = [
    (":=", "ASIGNACION"),
    (">=", "RELACIONAL"),
    ("<=", "RELACIONAL"),
    (">", "RELACIONAL"),
    ("<", "RELACIONAL"),
    ("=", "RELACIONAL"),
]

OPERADORES = ["+", "-", "*"]       # punto 6.3

COMENTARIO = "//"                  # punto 6


def buscar_simbolo(texto, i):
    for simbolo, tipo in SIMBOLOS:
        if texto.startswith(simbolo, i):
            return simbolo, tipo
    return None


def es_negativo(texto, i, tokens):
    # "-" pegado a un dígito es un número negativo, salvo que venga después de un valor:
    # en "x := -5" es negativo, en "saldo-5" es una resta
    if texto[i] != "-" or i + 1 >= len(texto) or not texto[i + 1].isdigit():
        return False
    return len(tokens) == 0 or tokens[-1][0] not in ["NUMERO", "IDENTIFICADOR"]


def tokenizar(texto):
    tokens = []
    i = 0
    linea = 1
    inicio_linea = 0

    while i < len(texto):
        c = texto[i]
        columna = i - inicio_linea + 1
        simbolo = buscar_simbolo(texto, i)

        # 1. Espacios y tabulaciones: se ignoran
        if c == " " or c == "\t":
            i += 1

        # 2. Salto de línea: se ignora, pero se cuenta para los mensajes de error
        elif c == "\n":
            linea += 1
            i += 1
            inicio_linea = i

        elif texto.startswith(COMENTARIO, i):
            while i < len(texto) and texto[i] != "\n":
                i += 1

        elif c.isalpha():
            inicio = i
            while i < len(texto) and (texto[i].isalnum() or texto[i] == "_"):
                i += 1
            palabra = texto[inicio:i]
            if palabra in TIPOS:
                tokens.append(("TIPO", palabra, linea, columna))
            elif palabra in PALABRAS_RESERVADAS:
                tokens.append(("RESERVADA", palabra, linea, columna))
            elif palabra in BOOLEANOS:
                tokens.append(("BOOLEANO", palabra, linea, columna))
            else:
                tokens.append(("IDENTIFICADOR", palabra, linea, columna))

        # 5. Número entero o decimal (punto 6.2), con "-" opcional pegado al primer dígito
        elif c.isdigit() or es_negativo(texto, i, tokens):
            inicio = i
            i += 1                                # se consume el signo o el primer dígito
            puntos = 0
            while i < len(texto) and (texto[i].isdigit() or texto[i] == "."):
                if texto[i] == ".":
                    puntos += 1
                i += 1
            numero = texto[inicio:i]
            if puntos > 1 or numero.endswith("."):
                raise SyntaxError(f"Línea {linea}, columna {columna}: decimal mal formado '{numero}' (lleva un solo punto y dígitos después)")
            tokens.append(("NUMERO", numero, linea, columna))

        # 6. Operadores aritméticos de un carácter (punto 6.3): +  -  *
        elif c in OPERADORES:
            tokens.append(("OPERADOR", c, linea, columna))
            i += 1

        # 7. Símbolos de uno o más caracteres (punto 5): :=  >=  <=  >  <  =
        elif simbolo is not None:
            texto_simbolo, tipo = simbolo
            if (texto_simbolo == "=" and len(tokens) >= 2
                    and tokens[-2][0] == "TIPO" and tokens[-1][0] == "IDENTIFICADOR"):
                raise SyntaxError(f"Línea {linea}, columna {columna}: la asignación se escribe ':=' (el '=' solo sirve para comparar)")
            tokens.append((tipo, texto_simbolo, linea, columna))
            i += len(texto_simbolo)

        # 8. ":" suelto: empezó una asignación pero le falta el "="
        elif c == ":":
            raise SyntaxError(f"Línea {linea}, columna {columna}: se esperaba '=' después de ':' (la asignación se escribe :=)")

        # 9. Cadena entre comillas dobles (punto 6.2): se lee hasta la comilla de cierre
        elif c == '"':
            inicio = i + 1
            i += 1
            while i < len(texto) and texto[i] != '"' and texto[i] != "\n":
                i += 1
            if i >= len(texto) or texto[i] != '"':
                raise SyntaxError(f"Línea {linea}, columna {columna}: cadena sin cerrar, falta la comilla final")
            tokens.append(("CADENA", texto[inicio:i], linea, columna))
            i += 1

        else:
            raise SyntaxError(f"Línea {linea}, columna {columna}: carácter inesperado '{c}'")

    return tokens


def es_declaracion(tokens):
    # Comprueba que una lista de tokens tenga la forma  Pille <id> := <valor>
    return (len(tokens) == 4
            and tokens[0][0] == "TIPO"
            and tokens[1][0] == "IDENTIFICADOR"
            and tokens[2][0] == "ASIGNACION"
            and (tokens[3][0] == "NUMERO" or tokens[3][0] == "BOOLEANO"))


# ---------------- Pruebas ----------------

print("== Declaraciones válidas ==")
print(tokenizar("Pille edad := 18"))
print(tokenizar("Pille permiso := Paila"))
print(tokenizar("Pille deuda := -20000"))
print(es_declaracion(tokenizar("Pille saldo := 50000")))        # True
print(es_declaracion(tokenizar("Si edad >= 18 Eche entrar")))   # False: es una regla

print()
print("== Programa completo del diccionario ==")
programa = """// control de acceso nocturno
Pille edad := 18
Pille hora := 23
Pille permiso := Paila
Si edad >= 18 Tin hora >= 22 Eche permiso := Melo
Si permiso = Paila Eche mostrar "Paila nea, el cucho dijo que no"
"""
for token in tokenizar(programa):
    print(token)

print()
print("== Errores léxicos ==")
pruebas_con_error = [
    "Pille edad : 18",            # falta el = de :=
    "Pille precio := 3.4.5",      # decimal con dos puntos
    "Pille saldo := $5000",       # símbolo que no existe en el lenguaje
    "Pille precio := 18.",        # decimal sin dígitos después del punto
    'Si x = 1 Eche mostrar "hola',  # cadena sin cerrar
    "Pille a := 1\nPille b := @",   # error en la línea 2
]
for prueba in pruebas_con_error:
    try:
        tokenizar(prueba)
    except SyntaxError as e:
        print("Error:", e)


# ---------------- Pruebas de los puntos 4, 5, 6, 6.1, 6.2 y 6.3 ----------------
# Lo ESPERADO se calculó a mano ANTES de ejecutar (columna = posición del primer
# carácter de la pieza, contando desde 1 en cada línea). Después se compara con la
# salida real del lexer.

resultados = []


def probar(punto, nombre, entrada, esperado):
    # esperado es una lista de tokens, o un texto si se espera un error léxico
    try:
        real = tokenizar(entrada)
    except SyntaxError as e:
        real = str(e)
    coincide = (real == esperado)
    resultados.append(coincide)
    print(f"[{punto}] {nombre}")
    print("   entrada :", repr(entrada))
    print("   esperado:", esperado)
    print("   obtenido:", real)
    print("   resultado:", "COINCIDE" if coincide else "NO COINCIDE")
    print()


print()
print("== Punto 4: palabras reservadas (TIPO vs IDENTIFICADOR) ==")
probar("4", "Pille es un TIPO y edad un IDENTIFICADOR",
       "Pille edad",
       [("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "edad", 1, 7)])
probar("4", "Pillesito NO se parte en Pille + sito",
       "Pillesito",
       [("IDENTIFICADOR", "Pillesito", 1, 1)])
probar("4", "pille en minúscula no es el tipo (distingue mayúsculas)",
       "pille edad",
       [("IDENTIFICADOR", "pille", 1, 1), ("IDENTIFICADOR", "edad", 1, 7)])

print("== Punto 5: signo de asignación y fin de instrucción ==")
probar("5", "declaración completa con espacios",
       "Pille edad := 18",
       [("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "edad", 1, 7),
        ("ASIGNACION", ":=", 1, 12), ("NUMERO", "18", 1, 15)])
probar("5", "declaración sin espacios alrededor de :=",
       "Pille edad:=18",
       [("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "edad", 1, 7),
        ("ASIGNACION", ":=", 1, 11), ("NUMERO", "18", 1, 13)])
probar("5", ">= se lee completo (el símbolo más largo primero)",
       "Si edad >= 18",
       [("RESERVADA", "Si", 1, 1), ("IDENTIFICADOR", "edad", 1, 4),
        ("RELACIONAL", ">=", 1, 9), ("NUMERO", "18", 1, 12)])
probar("5", "asignación estilo Java (=) produce error",
       "Pille edad = 18",
       "Línea 1, columna 12: la asignación se escribe ':=' (el '=' solo sirve para comparar)")
probar("5", "fin de instrucción estilo Java (;) produce error",
       "Pille edad := 18;",
       "Línea 1, columna 17: carácter inesperado ';'")

print("== Punto 6: comentarios ==")
probar("6", "comentario al final no cambia los tokens",
       "Pille edad := 18 // mayor de edad",
       [("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "edad", 1, 7),
        ("ASIGNACION", ":=", 1, 12), ("NUMERO", "18", 1, 15)])
probar("6", "la línea siguiente conserva su número de línea",
       "Pille edad := 18 // mayor de edad\nPille hora := 23",
       [("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "edad", 1, 7),
        ("ASIGNACION", ":=", 1, 12), ("NUMERO", "18", 1, 15),
        ("TIPO", "Pille", 2, 1), ("IDENTIFICADOR", "hora", 2, 7),
        ("ASIGNACION", ":=", 2, 12), ("NUMERO", "23", 2, 15)])
probar("6", "un comentario con símbolos raros se ignora completo",
       "// $ @ # ; 3.4.5",
       [])

print("== Punto 6.1: errores léxicos con línea y columna ==")
probar("6.1", "@ en la línea 1",
       "Pille x := 5 @",
       "Línea 1, columna 14: carácter inesperado '@'")
probar("6.1", "el mismo error en la línea 2 reporta línea 2",
       "Pille x := 5\nPille y := @",
       "Línea 2, columna 12: carácter inesperado '@'")
probar("6.1", "un comentario antes no descuadra la línea",
       "// nota\nPille x := $",
       "Línea 2, columna 12: carácter inesperado '$'")
probar("6.1", "la columna cuenta los espacios del comienzo",
       "  Pille x := #",
       "Línea 1, columna 14: carácter inesperado '#'")

print("== Punto 6.2: decimales y cadenas ==")
probar("6.2", "3.14 sale como un solo NUMERO",
       "Pille precio := 3.14",
       [("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "precio", 1, 7),
        ("ASIGNACION", ":=", 1, 14), ("NUMERO", "3.14", 1, 17)])
probar("6.2", "decimal con dos puntos produce error",
       "Pille precio := 3.4.5",
       "Línea 1, columna 17: decimal mal formado '3.4.5' (lleva un solo punto y dígitos después)")
probar("6.2", "cadena sin cerrar reporta la línea donde empezó",
       'Pille a := 1\nSi a = 1 Eche mostrar "hola',
       "Línea 2, columna 23: cadena sin cerrar, falta la comilla final")

print("== Punto 6.3: operadores + - * ==")
probar("6.3", "operadores con espacios",
       "Pille total := a + 5 * 2",
       [("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "total", 1, 7),
        ("ASIGNACION", ":=", 1, 13), ("IDENTIFICADOR", "a", 1, 16),
        ("OPERADOR", "+", 1, 18), ("NUMERO", "5", 1, 20),
        ("OPERADOR", "*", 1, 22), ("NUMERO", "2", 1, 24)])
probar("6.3", "operadores sin espacios",
       "Pille total:=a+5*2",
       [("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "total", 1, 7),
        ("ASIGNACION", ":=", 1, 12), ("IDENTIFICADOR", "a", 1, 14),
        ("OPERADOR", "+", 1, 15), ("NUMERO", "5", 1, 16),
        ("OPERADOR", "*", 1, 17), ("NUMERO", "2", 1, 18)])
probar("6.3", "-5 después de := es negativo, el otro - es resta",
       "Pille x := -5 - 2",
       [("TIPO", "Pille", 1, 1), ("IDENTIFICADOR", "x", 1, 7),
        ("ASIGNACION", ":=", 1, 9), ("NUMERO", "-5", 1, 12),
        ("OPERADOR", "-", 1, 15), ("NUMERO", "2", 1, 17)])

print(f"Resumen: {sum(resultados)} de {len(resultados)} pruebas coinciden con lo esperado a mano.")
