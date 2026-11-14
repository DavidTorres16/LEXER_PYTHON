# Clases de datos de ColombiaScript.
#
#   Token            cada pieza del programa con sus datos CON NOMBRE: t.tipo, t.texto,
#                    t.linea, t.columna (en vez de t[0], t[1], t[2], t[3] de una tupla).
#   ErrorDeLenguaje  clase base de los errores del lenguaje: guarda mensaje, línea y
#                    columna. main.py la atrapa una sola vez y recibe cualquiera de las
#                    tres fases.
#   ErrorLexico      lo lanza el lexer      (carácter no reconocido, cadena sin cerrar...)
#   ErrorSintactico  lo lanza el parser     (los tokens no siguen la gramática)
#   ErrorSemantico   lo lanza el intérprete (variable no declarada, división por cero...)

from dataclasses import dataclass


@dataclass
class Token:
    tipo: str
    texto: str
    linea: int
    columna: int

    def __str__(self):
        return f"{self.tipo}('{self.texto}') en {self.linea}:{self.columna}"


class ErrorDeLenguaje(Exception):
    fase = "Error"                # cada clase hija solo cambia este nombre

    def __init__(self, mensaje, linea, columna):
        self.mensaje = mensaje
        self.linea = linea
        self.columna = columna
        super().__init__(f"{self.fase} en línea {linea}, columna {columna}: {mensaje}")


class ErrorLexico(ErrorDeLenguaje):
    fase = "Error léxico"


class ErrorSintactico(ErrorDeLenguaje):
    fase = "Error sintáctico"


class ErrorSemantico(ErrorDeLenguaje):
    fase = "Error semántico"
