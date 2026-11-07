# Tarea 15: lee un archivo de ColombiaScript y muestra la tabla de tokens.
#
#     python main.py ejemplo.txt

import sys

from lexer import tokenizar
from tokens import ErrorLexico


def mostrar_tabla(tokens):
    print(f"{'LINEA':<7}{'COL':<5}{'TIPO':<15}TEXTO")
    for t in tokens:
        print(f"{t.linea:<7}{t.columna:<5}{t.tipo:<15}{t.texto}".rstrip())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python main.py <archivo>")
        sys.exit(1)

    ruta = sys.argv[1]
    try:
        texto = open(ruta, encoding="utf-8").read()
    except OSError as e:
        print(f"No se pudo leer '{ruta}': {e.strerror}")
        sys.exit(1)

    try:
        mostrar_tabla(tokenizar(texto))
    except ErrorLexico as e:
        print(e)
        sys.exit(1)
