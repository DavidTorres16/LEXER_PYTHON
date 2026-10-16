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

COMENTARIO = "//"                  # punto 6


def buscar_simbolo(texto, i):
    for simbolo, tipo in SIMBOLOS:
        if texto.startswith(simbolo, i):
            return simbolo, tipo
    return None


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

        # 5. Número entero, con "-" opcional pegado al primer dígito
        elif c.isdigit() or (c == "-" and i + 1 < len(texto) and texto[i + 1].isdigit()):
            inicio = i
            i += 1                                # se consume el signo o el primer dígito
            while i < len(texto) and texto[i].isdigit():
                i += 1
            tokens.append(("NUMERO", texto[inicio:i], linea, columna))

        # 6. "-" suelto: en ColombiaScript no hay resta, el signo va pegado al número
        elif c == "-":
            raise SyntaxError(f"Línea {linea}, columna {columna}: el signo '-' debe ir pegado a un número (ej. -5)")

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

        # 9. Cadena entre comillas dobles (solo se usa después de mostrar)
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
    "Pille precio := 18.5",       # no hay decimales
    "Pille saldo := $5000",       # símbolo que no existe en el lenguaje
    "Pille frio := - 5",          # signo separado del número
    'Si x = 1 Eche mostrar "hola',  # cadena sin cerrar
    "Pille a := 1\nPille b := @",   # error en la línea 2
]
for prueba in pruebas_con_error:
    try:
        tokenizar(prueba)
    except SyntaxError as e:
        print("Error:", e)


# ---------------- Pruebas de los puntos 4, 5, 6 y 6.1 ----------------
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

print(f"Resumen: {sum(resultados)} de {len(resultados)} pruebas coinciden con lo esperado a mano.")
