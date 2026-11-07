# Clases de datos del lexer de ColombiaScript (Tareas 13 y 14)

from dataclasses import dataclass


@dataclass
class Token:
    tipo: str
    texto: str
    linea: int
    columna: int

    def __str__(self):
        return f"{self.tipo}('{self.texto}') en {self.linea}:{self.columna}"


class ErrorLexico(Exception):
    def __init__(self, mensaje, linea, columna):
        super().__init__(
            f"Error léxico en línea {linea}, columna {columna}: {mensaje}"
        )
        self.linea = linea
        self.columna = columna
