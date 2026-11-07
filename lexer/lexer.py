# Lexer de ColombiaScript
# Reconoce la declaración de variable:
#
#     <declaración> ::= "Pille" <identificador> ":=" <valor>
#     <valor>       ::= <entero> | <decimal> | <booleano>
#     <entero>      ::= <número> | "-" <número>
#
# Además reconoce el resto del vocabulario (Si, Eche, Tin, Tan, mostrar,
# operadores relacionales y aritméticos, delimitadores, cadenas y comentarios
# // y /* */).
#
# Cada token es un objeto Token (tipo, texto, linea, columna) y los errores se
# lanzan como ErrorLexico (ver tokens.py).
#
# Puntos de la guía de trabajo que cubre este archivo:
#   4   Palabras reservadas: "Pille" es el TIPO de ColombiaScript (como int en Java)
#   5   Signo de asignación (:=) y fin de instrucción (no existe ';')
#   6   Comentarios //
#   6.1 Errores léxicos con línea y columna exactas
#   8   Delimitadores ( ) { } , .
#   9   Operadores de dos caracteres == != <= >=
#       Operadores aritméticos + - * /
#   10  Palabras reservadas de control y booleanos
#   11  Comentarios de bloque /* ... */
#   12  Token de fin de archivo (EOF)
#   13  Clase Token
#   14  Excepción propia ErrorLexico

from tokens import Token, ErrorLexico

# Conjuntos guardados al principio del archivo (punto 4 y 10)
TIPOS = ["Pille"]                  # equivale a "int" en Java: abre una declaración
PALABRAS_RESERVADAS = ["Si", "Eche", "Tin", "Tan", "mostrar"]
BOOLEANOS = ["Melo", "Paila"]

# Símbolos de uno o más caracteres (puntos 5, 8 y 9). Van ordenados del MÁS LARGO
# al más corto: así ">=" se lee completo y no como ">" seguido de "=".
SIMBOLOS = [
    (":=", "ASIGNACION"),
    ("==", "RELACIONAL"),
    ("!=", "RELACIONAL"),
    (">=", "RELACIONAL"),
    ("<=", "RELACIONAL"),
    (">", "RELACIONAL"),
    ("<", "RELACIONAL"),
    ("=", "RELACIONAL"),
    ("(", "SIMBOLO"),
    (")", "SIMBOLO"),
    ("{", "SIMBOLO"),
    ("}", "SIMBOLO"),
    (",", "SIMBOLO"),
    (".", "SIMBOLO"),
    ("+", "OPERADOR"),
    ("-", "OPERADOR"),
    ("*", "OPERADOR"),
    ("/", "OPERADOR"),
]

# Tipos de token después de los cuales un "-" es RESTA y no el signo de un número:
# en "a-5" o "(a+b)-5" el "-" resta, mientras que en ":= -5" o "= -5" es un negativo.
FIN_DE_OPERANDO = ["IDENTIFICADOR", "NUMERO"]

COMENTARIO = "//"                  # punto 6
INICIO_BLOQUE = "/*"               # punto 11
FIN_BLOQUE = "*/"


def buscar_simbolo(texto, i):
    # Devuelve (símbolo, tipo) si el texto, en la posición i, empieza con alguno
    # de SIMBOLOS; si no, None. Como la lista va de largo a corto, gana el más largo.
    for simbolo, tipo in SIMBOLOS:
        if texto.startswith(simbolo, i):
            return simbolo, tipo
    return None


def despues_de_operando(tokens):
    # True si el último token termina un operando: un nombre, un número o un ")".
    # Sirve para decidir si un "-" es una resta o el signo de un número negativo.
    if not tokens:
        return False
    ultimo = tokens[-1]
    return ultimo.tipo in FIN_DE_OPERANDO or (ultimo.tipo == "SIMBOLO" and ultimo.texto == ")")


def tokenizar(texto):
    tokens = []
    i = 0
    linea = 1
    inicio_linea = 0          # posición donde empezó la línea actual (para la columna)

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

        # 3. Comentario (punto 6): se avanza hasta el \n SIN consumirlo, para que
        #    el bloque 2 siga contando las líneas. No genera ningún token.
        elif texto.startswith(COMENTARIO, i):
            while i < len(texto) and texto[i] != "\n":
                i += 1

        # 4. Comentario de bloque (punto 11): se salta hasta "*/". Cada \n que se
        #    atraviesa suma una línea y reinicia la columna. Sin cierre es un error
        #    en la línea y columna donde EMPEZÓ el comentario.
        elif texto.startswith(INICIO_BLOQUE, i):
            fin = texto.find(FIN_BLOQUE, i + 2)
            if fin == -1:
                raise ErrorLexico("comentario sin cerrar", linea, columna)
            fin += len(FIN_BLOQUE)
            saltos = texto.count("\n", i, fin)
            if saltos > 0:
                linea += saltos
                inicio_linea = texto.rfind("\n", i, fin) + 1
            i = fin

        # 5. Palabra (punto 4 y 10): se lee COMPLETA y solo después se compara con
        #    los conjuntos. Por eso "Pillesito" es un identificador y no "Pille" + "sito".
        elif c.isalpha():
            inicio = i
            while i < len(texto) and (texto[i].isalnum() or texto[i] == "_"):
                i += 1
            palabra = texto[inicio:i]
            if palabra in TIPOS:
                tokens.append(Token("TIPO", palabra, linea, columna))
            elif palabra in PALABRAS_RESERVADAS:
                tokens.append(Token("RESERVADA", palabra, linea, columna))
            elif palabra in BOOLEANOS:
                tokens.append(Token("BOOLEANO", palabra, linea, columna))
            else:
                tokens.append(Token("IDENTIFICADOR", palabra, linea, columna))

        # 6. Número, con "-" opcional pegado al primer dígito (solo si el "-" no sigue a un
        #    operando: en "a-5" es una resta, en ":= -5" es un negativo). Un "." solo es parte
        #    del número si va seguido de un dígito (3.14); entre dos nombres
        #    (System.out) sigue siendo el símbolo "." del bloque 8.
        elif c.isdigit() or (c == "-" and i + 1 < len(texto) and texto[i + 1].isdigit()
                             and not despues_de_operando(tokens)):
            inicio = i
            i += 1                                # se consume el signo o el primer dígito
            while i < len(texto) and texto[i].isdigit():
                i += 1
            if i + 1 < len(texto) and texto[i] == "." and texto[i + 1].isdigit():
                i += 1                            # se consume el punto decimal
                while i < len(texto) and texto[i].isdigit():
                    i += 1
            tokens.append(Token("NUMERO", texto[inicio:i], linea, columna))

        # 7. ":" suelto: empezó una asignación pero le falta el "="
        #    (va antes que los símbolos porque ":=" ya los gana cuando está completo)
        elif c == ":" and simbolo is None:
            raise ErrorLexico("se esperaba '=' después de ':' (la asignación se escribe :=)", linea, columna)

        # 8. Símbolos (puntos 5, 8 y 9): := == != >= <= > < = ( ) { } , . + - * /
        elif simbolo is not None:
            texto_simbolo, tipo = simbolo
            # "=" justo después de "Pille <id>" es una asignación escrita al estilo
            # Java: en ColombiaScript el "=" solo sirve para comparar.
            if (texto_simbolo == "=" and len(tokens) >= 2
                    and tokens[-2].tipo == "TIPO" and tokens[-1].tipo == "IDENTIFICADOR"):
                raise ErrorLexico("la asignación se escribe ':=' (el '=' solo sirve para comparar)", linea, columna)
            tokens.append(Token(tipo, texto_simbolo, linea, columna))
            i += len(texto_simbolo)               # se avanza tantas posiciones como mide

        # 9. Cadena entre comillas dobles (solo se usa después de mostrar)
        elif c == '"':
            inicio = i + 1
            i += 1
            while i < len(texto) and texto[i] != '"' and texto[i] != "\n":
                i += 1
            if i >= len(texto) or texto[i] != '"':
                raise ErrorLexico("cadena sin cerrar, falta la comilla final", linea, columna)
            tokens.append(Token("CADENA", texto[inicio:i], linea, columna))
            i += 1                                # se consume la comilla de cierre

        # 10. Nada lo reconoció (punto 6.1): error léxico con línea y columna exactas.
        #     Aquí caen, por ejemplo, ';' '@' '$' y un '!' sin '=' detrás.
        else:
            raise ErrorLexico(f"carácter '{c}' no reconocido", linea, columna)

    # Punto 12: el último token es EOF, en la posición final del texto
    tokens.append(Token("EOF", "", linea, i - inicio_linea + 1))
    return tokens


def es_declaracion(tokens):
    # Comprueba que una lista de tokens tenga la forma  Pille <id> := <valor>
    # (el EOF final no cuenta)
    if tokens and tokens[-1].tipo == "EOF":
        tokens = tokens[:-1]
    return (len(tokens) == 4
            and tokens[0].tipo == "TIPO"
            and tokens[1].tipo == "IDENTIFICADOR"
            and tokens[2].tipo == "ASIGNACION"
            and (tokens[3].tipo == "NUMERO" or tokens[3].tipo == "BOOLEANO"))
