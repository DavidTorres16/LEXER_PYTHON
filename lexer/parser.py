# Parser de ColombiaScript: recibe la lista de Token del lexer y arma el árbol.
#
# Técnica: descenso recursivo. Por cada regla de la gramática hay un método con el
# mismo nombre, y cada parte de la regla es una línea del método:
#
#   En la regla aparece                   En el método se escribe
#   un token exacto, como ':='            self.esperar("ASIGNACION", ":=")
#   un tipo de token, como IDENTIFICADOR  self.esperar("IDENTIFICADOR")
#   otra regla, como expresion            self.expresion()
#   una opción con |                      un if que mira self.actual()
#   algo que se repite con ( )*           un while que mira self.actual()
#   algo opcional con ( )?                un if que mira self.actual()
#
# Gramática de ColombiaScript en EBNF
# (lo que va entre comillas es un token exacto; lo que va en MAYÚSCULAS es un tipo
#  de token; ColombiaScript no usa ';': cada instrucción termina donde empieza otra)
#
#   programa    ::= instruccion* EOF
#   instruccion ::= declaracion | asignacion | salida | condicional | ciclo | ciclo_para
#   declaracion ::= 'Pille' IDENTIFICADOR ':=' condicion
#   asignacion  ::= IDENTIFICADOR ':=' condicion
#   salida      ::= 'mostrar' '(' condicion ')'
#   condicional ::= 'Si' condicion 'Eche' bloque ('Sino' bloque)?
#   ciclo       ::= 'Dele' condicion 'Eche' bloque
#   ciclo_para  ::= 'Cuente' IDENTIFICADOR 'Desde' expresion 'Hasta' expresion 'Eche' bloque
#   bloque      ::= '{' instruccion* '}'
#   condicion   ::= conjuncion ('Tan' conjuncion)*
#   conjuncion  ::= negacion ('Tin' negacion)*
#   negacion    ::= 'Nel' negacion | comparacion
#   comparacion ::= expresion (COMPARADOR expresion)?
#   expresion   ::= termino (('+' | '-') termino)*
#   termino     ::= factor (('*' | '/') factor)*
#   factor      ::= NUMERO | CADENA | BOOLEANO | IDENTIFICADOR | lectura
#                 | '-' factor | '(' condicion ')'
#   lectura     ::= 'leer' '(' expresion? ')'
#
# Precedencia (de lo que se calcula primero a lo último): paréntesis y menos unario,
# * /, + -, comparación, Nel, Tin, Tan. Mientras más abajo esté la regla, más abajo
# queda en el árbol y antes se calcula.

from arbol import (Asignacion, Booleano, Cadena, Comparacion, Declaracion, Leer, Logica,
                   Mientras, Mostrar, Negacion, Negativo, Numero, OperacionBinaria, Para,
                   Programa, Si, Variable)
from tokens import ErrorSintactico


def describir(t):
    # Cómo se nombra un token en un mensaje de error
    return "el fin del archivo" if t.tipo == "EOF" else f"'{t.texto}'"


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens      # la lista de objetos Token que devolvió el lexer
        self.pos = 0              # índice del token en el que va

    # ---------------- Métodos auxiliares (Sesión 3 y Tema 4) ----------------

    def actual(self):
        # El token en el que va el parser, SIN moverse.
        return self.tokens[self.pos]

    def avanzar(self):
        # Devuelve el token actual y pasa al siguiente (en EOF ya no se mueve).
        token = self.actual()
        if token.tipo != "EOF":
            self.pos += 1
        return token

    def es(self, tipo, texto=None):
        # True si el token actual es de ese tipo (y, si se da, con ese texto).
        t = self.actual()
        return t.tipo == tipo and (texto is None or t.texto == texto)

    def esperar(self, tipo, texto=None):
        # "Aquí debe venir tal token": si es el que pide la regla, avanza y lo
        # devuelve; si no, lanza ErrorSintactico en la posición del que sí llegó.
        t = self.actual()
        if not self.es(tipo, texto):
            quiero = f"'{texto}'" if texto else f"un {tipo}"
            raise ErrorSintactico(f"se esperaba {quiero} y llegó {describir(t)}",
                                  t.linea, t.columna)
        return self.avanzar()

    # ---------------- Instrucciones ----------------

    # programa ::= instruccion* EOF
    def programa(self):
        instrucciones = []
        while not self.es("EOF"):
            instrucciones.append(self.instruccion())
        return Programa(instrucciones)

    # instruccion ::= declaracion | asignacion | salida | condicional | ciclo | ciclo_para
    def instruccion(self):
        t = self.actual()
        if t.tipo == "TIPO":
            return self.declaracion()
        if t.tipo == "IDENTIFICADOR":
            return self.asignacion()
        if self.es("RESERVADA", "mostrar"):
            return self.salida()
        if self.es("RESERVADA", "Si"):
            return self.condicional()
        if self.es("RESERVADA", "Dele"):
            return self.ciclo()
        if self.es("RESERVADA", "Cuente"):
            return self.ciclo_para()
        raise ErrorSintactico(f"se esperaba el inicio de una instrucción y llegó {describir(t)}",
                              t.linea, t.columna)

    # declaracion ::= 'Pille' IDENTIFICADOR ':=' condicion
    def declaracion(self):
        tipo = self.esperar("TIPO")                   # 'Pille'
        nombre = self.esperar("IDENTIFICADOR")        # IDENTIFICADOR
        self.esperar("ASIGNACION", ":=")              # ':='
        valor = self.condicion()                      # condicion
        return Declaracion(tipo, nombre, valor)

    # asignacion ::= IDENTIFICADOR ':=' condicion
    def asignacion(self):
        nombre = self.esperar("IDENTIFICADOR")        # IDENTIFICADOR
        self.esperar("ASIGNACION", ":=")              # ':='
        valor = self.condicion()                      # condicion
        return Asignacion(nombre, valor)

    # salida ::= 'mostrar' '(' condicion ')'
    def salida(self):
        palabra = self.esperar("RESERVADA", "mostrar")
        self.esperar("SIMBOLO", "(")
        valor = self.condicion()
        self.esperar("SIMBOLO", ")")
        return Mostrar(palabra, valor)

    # condicional ::= 'Si' condicion 'Eche' bloque ('Sino' bloque)?
    def condicional(self):
        palabra = self.esperar("RESERVADA", "Si")
        condicion = self.condicion()
        self.esperar("RESERVADA", "Eche")
        entonces = self.bloque()
        sino = None
        if self.es("RESERVADA", "Sino"):              # opcional: se pregunta, no se espera
            self.avanzar()
            sino = self.bloque()
        return Si(palabra, condicion, entonces, sino)

    # ciclo ::= 'Dele' condicion 'Eche' bloque
    def ciclo(self):
        palabra = self.esperar("RESERVADA", "Dele")
        condicion = self.condicion()
        self.esperar("RESERVADA", "Eche")
        cuerpo = self.bloque()
        return Mientras(palabra, condicion, cuerpo)

    # ciclo_para ::= 'Cuente' IDENTIFICADOR 'Desde' expresion 'Hasta' expresion 'Eche' bloque
    def ciclo_para(self):
        palabra = self.esperar("RESERVADA", "Cuente")
        variable = self.esperar("IDENTIFICADOR")
        self.esperar("RESERVADA", "Desde")
        desde = self.expresion()
        self.esperar("RESERVADA", "Hasta")
        hasta = self.expresion()
        self.esperar("RESERVADA", "Eche")
        cuerpo = self.bloque()
        return Para(palabra, variable, desde, hasta, cuerpo)

    # bloque ::= '{' instruccion* '}'
    def bloque(self):
        llave = self.esperar("SIMBOLO", "{")          # se guarda para decir dónde se abrió
        instrucciones = []
        while not self.es("SIMBOLO", "}"):
            if self.es("EOF"):
                t = self.actual()
                raise ErrorSintactico(
                    f"falta '}}' para cerrar el bloque abierto en la línea {llave.linea}",
                    t.linea, t.columna)
            instrucciones.append(self.instruccion())
        self.avanzar()                                # '}'
        return instrucciones

    # ---------------- Condiciones (de la precedencia más baja a la más alta) ----------------

    # condicion ::= conjuncion ('Tan' conjuncion)*
    def condicion(self):
        izq = self.conjuncion()
        while self.es("RESERVADA", "Tan"):
            operador = self.avanzar()
            der = self.conjuncion()
            izq = Logica(izq, operador, der)
        return izq

    # conjuncion ::= negacion ('Tin' negacion)*
    def conjuncion(self):
        izq = self.negacion()
        while self.es("RESERVADA", "Tin"):
            operador = self.avanzar()
            der = self.negacion()
            izq = Logica(izq, operador, der)
        return izq

    # negacion ::= 'Nel' negacion | comparacion
    def negacion(self):
        if self.es("RESERVADA", "Nel"):
            palabra = self.avanzar()
            return Negacion(palabra, self.negacion())
        return self.comparacion()

    # comparacion ::= expresion (COMPARADOR expresion)?
    def comparacion(self):
        izq = self.expresion()
        if self.es("COMPARADOR"):
            operador = self.avanzar()
            der = self.expresion()
            return Comparacion(izq, operador, der)
        return izq

    # ---------------- Expresiones aritméticas ----------------

    # expresion ::= termino (('+' | '-') termino)*
    def expresion(self):
        izq = self.termino()                          # termino
        while self.es("OPERADOR", "+") or self.es("OPERADOR", "-"):
            operador = self.avanzar()                 # '+' o '-'
            der = self.termino()                      # termino
            izq = OperacionBinaria(izq, operador, der)
        return izq

    # termino ::= factor (('*' | '/') factor)*
    def termino(self):
        izq = self.factor()                           # factor
        while self.es("OPERADOR", "*") or self.es("OPERADOR", "/"):
            operador = self.avanzar()                 # '*' o '/'
            der = self.factor()                       # factor
            izq = OperacionBinaria(izq, operador, der)
        return izq

    # factor ::= NUMERO | CADENA | BOOLEANO | IDENTIFICADOR | lectura
    #          | '-' factor | '(' condicion ')'
    def factor(self):
        t = self.actual()
        if t.tipo == "NUMERO":
            return Numero(self.avanzar())
        if t.tipo == "CADENA":
            return Cadena(self.avanzar())
        if t.tipo == "BOOLEANO":
            return Booleano(self.avanzar())
        if t.tipo == "IDENTIFICADOR":
            return Variable(self.avanzar())
        if self.es("RESERVADA", "leer"):
            return self.lectura()
        if self.es("OPERADOR", "-"):                  # menos unario: -(x + 2)
            operador = self.avanzar()
            return Negativo(operador, self.factor())
        if self.es("SIMBOLO", "("):
            self.avanzar()                            # '('
            dentro = self.condicion()                 # condicion (aquí está la recursión)
            self.esperar("SIMBOLO", ")")              # ')'
            return dentro                             # los paréntesis no crean nodo
        raise ErrorSintactico(
            f"se esperaba un número, una variable o '(' y llegó {describir(t)}",
            t.linea, t.columna)

    # lectura ::= 'leer' '(' expresion? ')'
    def lectura(self):
        palabra = self.esperar("RESERVADA", "leer")
        self.esperar("SIMBOLO", "(")
        pregunta = None
        if not self.es("SIMBOLO", ")"):               # la pregunta es opcional
            pregunta = self.expresion()
        self.esperar("SIMBOLO", ")")
        return Leer(palabra, pregunta)
