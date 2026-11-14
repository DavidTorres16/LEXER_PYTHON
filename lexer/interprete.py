# Intérprete de ColombiaScript: recorre el árbol que armó el parser y lo ejecuta.
#
#   ejecutar(nodo)  para las instrucciones (declarar, asignar, mostrar, Si, Dele,
#                   Cuente). No devuelve nada: cambia el entorno o imprime.
#   evaluar(nodo)   para las expresiones. Devuelve un valor de Python.
#
# Tipos de ColombiaScript y su valor en Python:
#   entero   -> int        20, -5
#   decimal  -> float      31.5
#   texto    -> str        "hola"
#   booleano -> bool       Melo (True), Paila (False)
#
# Pille no lleva tipo: la variable toma el tipo del primer valor que recibe y desde
# ahí solo acepta valores de ese tipo (un decimal también acepta enteros).

from arbol import (Asignacion, Booleano, Cadena, Comparacion, Declaracion, Leer, Logica,
                   Mientras, Mostrar, Negacion, Negativo, Numero, OperacionBinaria, Para,
                   Si, Variable)
from tokens import ErrorSemantico

LIMITE_VUELTAS = 100_000

# Qué tipos de Python acepta cada tipo de ColombiaScript. Se usa type(valor) y no
# isinstance porque en Python True también cuenta como entero.
ACEPTA = {
    "entero": (int,),
    "decimal": (int, float),
    "texto": (str,),
    "booleano": (bool,),
}

NOMBRE_TIPO = {int: "entero", float: "decimal", str: "texto", bool: "booleano"}


def tipo_de(valor):
    return NOMBRE_TIPO[type(valor)]


def es_numero(valor):
    return type(valor) in (int, float)        # un booleano NO es número


def formatear(valor):
    # Cómo se ve un valor al mostrarlo: los booleanos con las palabras del lenguaje
    if type(valor) is bool:
        return "Melo" if valor else "Paila"
    return str(valor)


class Entorno:
    # Guarda las variables de un bloque. Si una variable no está aquí, se busca en
    # el entorno padre (el bloque que lo contiene), y así hasta el entorno global.
    def __init__(self, padre=None):
        self.variables = {}       # nombre -> {"tipo": ..., "valor": ..., "linea": ...}
        self.padre = padre

    def buscar(self, nombre):
        if nombre in self.variables:
            return self.variables[nombre]
        if self.padre is not None:
            return self.padre.buscar(nombre)
        return None

    def declarar(self, nombre, tipo, valor, linea):
        self.variables[nombre] = {"tipo": tipo, "valor": valor, "linea": linea}


class Interprete:
    def __init__(self, entrada=input):
        self.entorno = Entorno()  # entorno actual; al empezar es el global
        self.entrada = entrada    # función que lee del teclado (en las pruebas se cambia)

    def ejecutar_programa(self, programa):
        for instruccion in programa.instrucciones:
            self.ejecutar(instruccion)

    def ejecutar_bloque(self, instrucciones):
        # Un bloque { } abre un entorno nuevo cuyo padre es el actual. Al terminar
        # se vuelve al padre, así que lo declarado adentro deja de existir.
        anterior = self.entorno
        self.entorno = Entorno(anterior)
        try:
            for instruccion in instrucciones:
                self.ejecutar(instruccion)
        finally:
            self.entorno = anterior   # se restaura aunque haya un error

    # ---------------- Instrucciones ----------------

    def ejecutar(self, nodo):
        if isinstance(nodo, Declaracion):
            nombre = nodo.nombre
            existente = self.entorno.buscar(nombre.texto)
            if existente is not None:
                raise ErrorSemantico(
                    f"la variable '{nombre.texto}' ya fue declarada en la línea {existente['linea']}",
                    nombre.linea, nombre.columna)
            valor = self.evaluar(nodo.valor)
            self.entorno.declarar(nombre.texto, tipo_de(valor), valor, nombre.linea)

        elif isinstance(nodo, Asignacion):
            nombre = nodo.nombre
            variable = self.buscar_variable(nombre)
            if isinstance(nodo.valor, Leer):
                valor = self.leer(nodo.valor, variable["tipo"])
            else:
                valor = self.evaluar(nodo.valor)
            variable["valor"] = self.ajustar_tipo(valor, variable["tipo"], nombre)

        elif isinstance(nodo, Mostrar):
            print(formatear(self.evaluar(nodo.valor)))

        elif isinstance(nodo, Si):
            if self.evaluar_condicion(nodo.condicion, nodo.palabra):
                self.ejecutar_bloque(nodo.entonces)
            elif nodo.sino is not None:
                self.ejecutar_bloque(nodo.sino)

        elif isinstance(nodo, Mientras):
            vueltas = 0
            while self.evaluar_condicion(nodo.condicion, nodo.palabra):
                vueltas += 1
                if vueltas > LIMITE_VUELTAS:
                    raise ErrorSemantico(
                        f"el ciclo superó {LIMITE_VUELTAS} vueltas; "
                        "¿falta actualizar la variable de la condición?",
                        nodo.palabra.linea, nodo.palabra.columna)
                self.ejecutar_bloque(nodo.cuerpo)

        elif isinstance(nodo, Para):
            self.ejecutar_para(nodo)

    def ejecutar_para(self, nodo):
        # Cuente i Desde a Hasta b Eche { ... }: i toma a, a+1, ..., b (incluido).
        # i solo existe dentro del ciclo.
        nombre = nodo.variable
        existente = self.entorno.buscar(nombre.texto)
        if existente is not None:
            raise ErrorSemantico(
                f"la variable '{nombre.texto}' ya fue declarada en la línea {existente['linea']}",
                nombre.linea, nombre.columna)
        desde = self.evaluar(nodo.desde)
        hasta = self.evaluar(nodo.hasta)
        for limite in (desde, hasta):
            if type(limite) is not int:
                raise ErrorSemantico(
                    f"Cuente necesita números enteros y recibió un {tipo_de(limite)}",
                    nodo.palabra.linea, nodo.palabra.columna)

        anterior = self.entorno
        self.entorno = Entorno(anterior)              # entorno del ciclo: solo tiene a i
        self.entorno.declarar(nombre.texto, "entero", desde, nombre.linea)
        try:
            valor = desde
            while valor <= hasta:
                self.entorno.variables[nombre.texto]["valor"] = valor
                self.ejecutar_bloque(nodo.cuerpo)
                valor += 1
        finally:
            self.entorno = anterior

    # ---------------- Expresiones ----------------

    def evaluar(self, nodo):
        if isinstance(nodo, Numero):
            texto = nodo.token.texto
            return float(texto) if "." in texto else int(texto)

        if isinstance(nodo, Cadena):
            return nodo.token.texto

        if isinstance(nodo, Booleano):
            return nodo.token.texto == "Melo"

        if isinstance(nodo, Variable):
            return self.buscar_variable(nodo.token)["valor"]

        if isinstance(nodo, OperacionBinaria):
            izq = self.evaluar(nodo.izq)              # primero los hijos...
            der = self.evaluar(nodo.der)
            return self.operar(izq, nodo.operador, der)   # ...después la operación

        if isinstance(nodo, Negativo):
            valor = self.evaluar(nodo.valor)
            if not es_numero(valor):
                raise ErrorSemantico(f"no se puede usar '-' con un {tipo_de(valor)}",
                                     nodo.operador.linea, nodo.operador.columna)
            return -valor

        if isinstance(nodo, Comparacion):
            izq = self.evaluar(nodo.izq)
            der = self.evaluar(nodo.der)
            return self.comparar(izq, nodo.operador, der)

        if isinstance(nodo, Logica):
            # Tin y Tan evalúan el lado derecho solo si hace falta
            izq = self.exigir_booleano(self.evaluar(nodo.izq), nodo.operador)
            if nodo.operador.texto == "Tin" and not izq:
                return False
            if nodo.operador.texto == "Tan" and izq:
                return True
            return self.exigir_booleano(self.evaluar(nodo.der), nodo.operador)

        if isinstance(nodo, Negacion):
            return not self.exigir_booleano(self.evaluar(nodo.valor), nodo.palabra)

        if isinstance(nodo, Leer):
            return self.leer(nodo)

    # ---------------- Reglas de operaciones entre tipos ----------------

    def operar(self, izq, operador, der):
        op = operador.texto
        if isinstance(izq, str) or isinstance(der, str):
            if op == "+":                             # texto + lo que sea: se unen
                return formatear(izq) + formatear(der)
            raise ErrorSemantico(f"no se puede usar '{op}' con textos",
                                 operador.linea, operador.columna)
        if type(izq) is bool or type(der) is bool:
            raise ErrorSemantico(f"no se puede usar '{op}' con booleanos",
                                 operador.linea, operador.columna)
        if op == "+":
            return izq + der
        if op == "-":
            return izq - der
        if op == "*":
            return izq * der
        # op == "/"
        if der == 0:
            raise ErrorSemantico("división por cero", operador.linea, operador.columna)
        if type(izq) is int and type(der) is int:
            # entero / entero = división entera, cortando hacia cero como en Java
            cociente = abs(izq) // abs(der)
            return cociente if (izq < 0) == (der < 0) else -cociente
        return izq / der

    def comparar(self, izq, operador, der):
        op = operador.texto
        if op in ("==", "=", "!="):
            mismo_tipo = (es_numero(izq) and es_numero(der)) or type(izq) is type(der)
            if not mismo_tipo:
                raise ErrorSemantico(
                    f"no se puede comparar un {tipo_de(izq)} con un {tipo_de(der)}",
                    operador.linea, operador.columna)
            return (izq == der) if op != "!=" else (izq != der)
        if not (es_numero(izq) and es_numero(der)):
            raise ErrorSemantico(f"'{op}' solo compara números",
                                 operador.linea, operador.columna)
        if op == "<":
            return izq < der
        if op == ">":
            return izq > der
        if op == "<=":
            return izq <= der
        return izq >= der

    # ---------------- Auxiliares ----------------

    def buscar_variable(self, token):
        variable = self.entorno.buscar(token.texto)
        if variable is None:
            raise ErrorSemantico(f"la variable '{token.texto}' no ha sido declarada",
                                 token.linea, token.columna)
        return variable

    def ajustar_tipo(self, valor, tipo, nombre):
        # Revisa que la variable acepte el valor. Un entero guardado en un decimal
        # se vuelve decimal (5 -> 5.0), como en Java.
        if type(valor) not in ACEPTA[tipo]:
            raise ErrorSemantico(
                f"no se puede guardar un {tipo_de(valor)} en la variable "
                f"'{nombre.texto}' de tipo {tipo}",
                nombre.linea, nombre.columna)
        return float(valor) if tipo == "decimal" else valor

    def exigir_booleano(self, valor, token):
        if type(valor) is not bool:
            raise ErrorSemantico(
                f"'{token.texto}' necesita una condición que dé Melo o Paila "
                f"y recibió un {tipo_de(valor)}",
                token.linea, token.columna)
        return valor

    def evaluar_condicion(self, condicion, palabra):
        return self.exigir_booleano(self.evaluar(condicion), palabra)

    def leer(self, nodo, tipo=None):
        # Pide un valor por teclado. Si se sabe el tipo de la variable que lo recibe
        # (x := leer()), se convierte a ese tipo; si no (Pille x := leer()), el tipo
        # se deduce de lo escrito: Melo/Paila, entero, decimal o texto.
        pregunta = "" if nodo.pregunta is None else formatear(self.evaluar(nodo.pregunta))
        try:
            texto = self.entrada(pregunta).strip()
        except EOFError:
            raise ErrorSemantico("no hay más datos para leer",
                                 nodo.palabra.linea, nodo.palabra.columna) from None

        if tipo is None:
            for convertir in (convertir_booleano, int, float):
                try:
                    return convertir(texto)
                except ValueError:
                    pass
            return texto

        conversores = {"entero": int, "decimal": float, "texto": str,
                       "booleano": convertir_booleano}
        try:
            return conversores[tipo](texto)
        except ValueError:
            raise ErrorSemantico(f"no se puede convertir '{texto}' a {tipo}",
                                 nodo.palabra.linea, nodo.palabra.columna) from None


def convertir_booleano(texto):
    if texto == "Melo":
        return True
    if texto == "Paila":
        return False
    raise ValueError(texto)
