# Programa principal de ColombiaScript: une las tres fases.
#
#     python main.py programa.txt            ejecuta el programa
#     python main.py --arbol programa.txt    muestra el árbol que arma el parser
#     python main.py --tokens programa.txt   muestra los tokens que entrega el lexer
#     python main.py                         modo interactivo (escriba "chao" para salir)
#
#   texto --lexer--> tokens --parser--> árbol --intérprete--> resultado
#
# Los tres errores (léxico, sintáctico y semántico) heredan de ErrorDeLenguaje,
# así que un solo except los atrapa todos.

import sys

from arbol import mostrar_arbol
from interprete import Interprete
from lexer import tokenizar
from parser import Parser
from tokens import ErrorDeLenguaje, ErrorLexico


def imprimir_tokens(parser):
    # Sesión 3: recorre los tokens con actual() y avanzar() hasta EOF (incluido).
    while parser.actual().tipo != "EOF":
        print(parser.actual())
        parser.avanzar()
    print(parser.actual())


def reportar_error(e, codigo):
    # Imprime el mensaje, la línea del programa con un ^ debajo de la columna,
    # y la línea y la columna por separado.
    print(e)
    lineas = codigo.split("\n")
    if 1 <= e.linea <= len(lineas):
        print("    " + lineas[e.linea - 1].replace("\t", " "))
        print("    " + " " * (e.columna - 1) + "^")
    print(f"linea = {e.linea}, columna = {e.columna}")


def ejecutar(codigo, interprete=None, modo="ejecutar"):
    # Pasa el código por las tres fases. Devuelve True si terminó sin errores.
    try:
        tokens = tokenizar(codigo)
        if modo == "tokens":
            imprimir_tokens(Parser(tokens))
            return True
        programa = Parser(tokens).programa()
        if modo == "arbol":
            mostrar_arbol(programa)
            return True
        (interprete or Interprete()).ejecutar_programa(programa)
        return True
    except ErrorDeLenguaje as e:
        reportar_error(e, codigo)
        return False


def bloques_abiertos(codigo):
    # Cuántas '{' faltan por cerrar (para que el modo interactivo siga pidiendo líneas)
    try:
        tokens = tokenizar(codigo)
    except ErrorLexico:
        return 0                      # el error se mostrará al ejecutar
    abiertas = sum(1 for t in tokens if t.tipo == "SIMBOLO" and t.texto == "{")
    cerradas = sum(1 for t in tokens if t.tipo == "SIMBOLO" and t.texto == "}")
    return abiertas - cerradas


def modo_interactivo():
    # Ejecuta lo que se escribe, una instrucción a la vez. El mismo intérprete se usa
    # en todas las líneas, por eso recuerda las variables. Si una línea abre un
    # bloque con '{', sigue pidiendo líneas hasta que se cierre.
    print("ColombiaScript - modo interactivo. Escriba 'chao' para salir.")
    interprete = Interprete()
    while True:
        try:
            codigo = input("cs> ")
            if codigo.strip() == "chao":
                break
            while bloques_abiertos(codigo) > 0:
                codigo += "\n" + input("... ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        ejecutar(codigo, interprete)
    print("Nombre de Dios, nos pillamos.")


def main():
    argumentos = sys.argv[1:]
    if not argumentos:
        modo_interactivo()
        return

    modo = "ejecutar"
    if argumentos[0] in ("--arbol", "--tokens"):
        modo = argumentos.pop(0)[2:]
    if len(argumentos) != 1:
        print("Uso: python main.py [--arbol | --tokens] programa.txt")
        print("     python main.py                  (modo interactivo)")
        sys.exit(1)

    ruta = argumentos[0]
    try:
        with open(ruta, encoding="utf-8") as archivo:
            codigo = archivo.read()
    except OSError as e:
        print(f"No se pudo leer '{ruta}': {e.strerror}")
        sys.exit(1)

    if not ejecutar(codigo, modo=modo):
        sys.exit(1)


if __name__ == "__main__":
    main()
