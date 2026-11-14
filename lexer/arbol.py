# Nodos del árbol de ColombiaScript.
#
# Cada tipo de nodo es una clase de datos. Los nodos guardan TOKENS, no solo textos,
# para poder dar línea y columna si algo falla al ejecutar.
#
#   Hojas (guardan un solo token):  Numero, Cadena, Booleano, Variable
#   Expresiones con hijos:          OperacionBinaria, Negativo, Comparacion,
#                                   Logica, Negacion, Leer
#   Instrucciones:                  Declaracion, Asignacion, Mostrar, Si,
#                                   Mientras, Para
#   Raíz:                           Programa

from dataclasses import dataclass

from tokens import Token


# ---------------- Hojas ----------------

@dataclass
class Numero:               # 20  o  31.5
    token: Token


@dataclass
class Cadena:               # "Paila, no hay lucas"
    token: Token


@dataclass
class Booleano:             # Melo  o  Paila
    token: Token


@dataclass
class Variable:             # un nombre usado en una expresión: edad
    token: Token


# ---------------- Expresiones ----------------

@dataclass
class OperacionBinaria:     # a + 5   (operador: + - * /)
    izq: object
    operador: Token
    der: object


@dataclass
class Negativo:             # -(x + 2)   (menos unario: cambia el signo)
    operador: Token
    valor: object


@dataclass
class Comparacion:          # edad >= 18   (operador: == = != < > <= >=)
    izq: object
    operador: Token
    der: object


@dataclass
class Logica:               # a Tin b  /  a Tan b
    izq: object
    operador: Token
    der: object


@dataclass
class Negacion:             # Nel listo
    palabra: Token
    valor: object


@dataclass
class Leer:                 # leer("¿Cuántos años tiene? ")   (pregunta puede ser None)
    palabra: Token
    pregunta: object


# ---------------- Instrucciones ----------------

@dataclass
class Declaracion:          # Pille edad := 20
    tipo: Token
    nombre: Token
    valor: object


@dataclass
class Asignacion:           # edad := edad + 1
    nombre: Token
    valor: object


@dataclass
class Mostrar:              # mostrar(total)
    palabra: Token
    valor: object


@dataclass
class Si:                   # Si <condición> Eche { ... } Sino { ... }
    palabra: Token
    condicion: object
    entonces: list
    sino: object            # lista de instrucciones, o None si no hay Sino


@dataclass
class Mientras:             # Dele <condición> Eche { ... }
    palabra: Token
    condicion: object
    cuerpo: list


@dataclass
class Para:                 # Cuente i Desde 1 Hasta 5 Eche { ... }
    palabra: Token
    variable: Token
    desde: object
    hasta: object
    cuerpo: list


@dataclass
class Programa:             # todas las instrucciones del archivo
    instrucciones: list


# ---------------- Mostrar el árbol en consola ----------------

def mostrar_arbol(nodo, nivel=0):
    # Imprime el nodo con dos espacios por cada nivel de profundidad y después
    # sus hijos un nivel más adentro. Lo que queda más abajo se calcula primero.
    sangria = "  " * nivel

    def grupo(nombre, instrucciones):
        # Un grupo de instrucciones (el bloque de un Si, Dele o Cuente)
        print(f"{sangria}  {nombre}")
        for instruccion in instrucciones:
            mostrar_arbol(instruccion, nivel + 2)

    if isinstance(nodo, Programa):
        print(f"{sangria}Programa")
        for instruccion in nodo.instrucciones:
            mostrar_arbol(instruccion, nivel + 1)

    elif isinstance(nodo, Declaracion):
        print(f"{sangria}Declaracion {nodo.tipo.texto} {nodo.nombre.texto}")
        mostrar_arbol(nodo.valor, nivel + 1)

    elif isinstance(nodo, Asignacion):
        print(f"{sangria}Asignacion {nodo.nombre.texto}")
        mostrar_arbol(nodo.valor, nivel + 1)

    elif isinstance(nodo, Mostrar):
        print(f"{sangria}Mostrar")
        mostrar_arbol(nodo.valor, nivel + 1)

    elif isinstance(nodo, Si):
        print(f"{sangria}Si")
        mostrar_arbol(nodo.condicion, nivel + 1)
        grupo("Eche", nodo.entonces)
        if nodo.sino is not None:
            grupo("Sino", nodo.sino)

    elif isinstance(nodo, Mientras):
        print(f"{sangria}Dele")
        mostrar_arbol(nodo.condicion, nivel + 1)
        grupo("Eche", nodo.cuerpo)

    elif isinstance(nodo, Para):
        print(f"{sangria}Cuente {nodo.variable.texto}")
        print(f"{sangria}  Desde")
        mostrar_arbol(nodo.desde, nivel + 2)
        print(f"{sangria}  Hasta")
        mostrar_arbol(nodo.hasta, nivel + 2)
        grupo("Eche", nodo.cuerpo)

    elif isinstance(nodo, (OperacionBinaria, Comparacion, Logica)):
        print(f"{sangria}{type(nodo).__name__} {nodo.operador.texto}")
        mostrar_arbol(nodo.izq, nivel + 1)
        mostrar_arbol(nodo.der, nivel + 1)

    elif isinstance(nodo, Negativo):
        print(f"{sangria}Negativo -")
        mostrar_arbol(nodo.valor, nivel + 1)

    elif isinstance(nodo, Negacion):
        print(f"{sangria}Negacion {nodo.palabra.texto}")
        mostrar_arbol(nodo.valor, nivel + 1)

    elif isinstance(nodo, Leer):
        print(f"{sangria}Leer")
        if nodo.pregunta is not None:
            mostrar_arbol(nodo.pregunta, nivel + 1)

    elif isinstance(nodo, Cadena):
        print(f'{sangria}Cadena "{nodo.token.texto}"')

    else:  # Numero, Booleano, Variable: hojas con un solo token
        print(f"{sangria}{type(nodo).__name__} {nodo.token.texto}")
