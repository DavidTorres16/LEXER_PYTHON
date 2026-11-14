# ColombiaScript — Parser, intérprete y entrega final

13 de noviembre de 2026

Este documento explica cómo se resolvió la guía "Entrega Final Lenguajes Formales":
qué mostrar el 14 de noviembre, dónde está cada tema en el código y qué falta para
la entrega del 23. La ficha, la gramática y las reglas de tipos están en el `README.md`.

## Qué mostrar el sábado 14 de noviembre

Lo que pide la guía: la gramática, el árbol de cada instrucción y los errores
sintácticos con línea y columna.

1. **La gramática:** el comentario al inicio de `parser.py` (es la misma del README).
2. **El árbol:**

   ```text
   $ python main.py --arbol programas/programa.txt
   Programa
     Declaracion Pille edad
       Numero 20
     Declaracion Pille nota
       OperacionBinaria /
         Variable edad
         Numero 4.0
   ```

3. **Los errores sintácticos.** Los ejemplos de la guía, en ColombiaScript:

   | Entrada | Salida |
   | --- | --- |
   | `Pille r := 10 - 3 - 2` (con `--arbol`) | `OperacionBinaria -` con `OperacionBinaria -` (10 y 3) a la izquierda y `Numero 2` a la derecha |
   | `Pille x :=` | `Error sintáctico en línea 1, columna 11: se esperaba un número, una variable o '(' y llegó el fin del archivo` |
   | `Pille y := 4 + * 2` | `Error sintáctico en línea 1, columna 16: se esperaba un número, una variable o '(' y llegó '*'` |
   | `Pille z := (1 + 2` | `Error sintáctico en línea 1, columna 18: se esperaba ')' y llegó el fin del archivo` |

   El ejemplo de Java `int x = 5` (falta el `;`) no tiene equivalente, porque
   ColombiaScript no usa `;`. En su lugar sirve `Pille := 5`: *se esperaba un
   IDENTIFICADOR y llegó ':='*. También está `programas/errores/sintactico.txt`.

## Dónde está cada tema de la guía

| Tema de la guía | Dónde está |
| --- | --- |
| 13 nov · Tema 1: gramática | Comentario al inicio de `parser.py` |
| 13 nov · Tema 2: el árbol | `arbol.py`: una `@dataclass` por nodo, y `mostrar_arbol` |
| 13 nov · Tema 3: un error por fase | `tokens.py`: `ErrorDeLenguaje` y sus tres hijas, que solo cambian `fase` |
| 13 nov · Tema 4: descenso recursivo | `parser.py`: `esperar` y un método por regla |
| 14 nov · Tema 1: salida | Regla `salida` → método `salida()` → nodo `Mostrar` → `print` en `ejecutar` |
| 14 nov · Tema 2: entorno | `interprete.py`: clase `Entorno` (diccionario con tipo, valor y línea) |
| 14 nov · Tema 3: hacer las cuentas | `Interprete.ejecutar` (instrucciones) y `Interprete.evaluar` (expresiones) |
| 14 nov · Tema 4: tipos distintos | `Interprete.operar` y `Interprete.comparar` |
| 14 nov · Tema 5: errores semánticos | `ErrorSemantico` en `ejecutar`, `operar`, `buscar_variable` y `ajustar_tipo` |
| 14 nov · Tema 6: unir las fases | `main.py`: función `ejecutar` y un solo `except ErrorDeLenguaje` |
| 20 nov · Tema 1: comparadores | Tipo `COMPARADOR` en `lexer.py`; regla `comparacion` |
| 20 nov · Tema 2: bloques | Regla `bloque`, con el error "falta '}'..." |
| 20 nov · Tema 3: condicional | `Si ... Eche { } Sino { }` → nodo `Si` |
| 20 nov · Tema 4: ciclo | `Dele ... Eche { }` → nodo `Mientras`, con límite de 100 000 vueltas |
| Req. 1: alcance de bloques | `Entorno(padre)` y `ejecutar_bloque` (crea un entorno y lo descarta al salir) |
| Req. 2: operadores lógicos | Reglas `condicion` (`Tan`), `conjuncion` (`Tin`), `negacion` (`Nel`) |
| Req. 3: negativos | Regla `factor ::= '-' factor` → nodo `Negativo` |
| Req. 4: errores que señalan el código | `reportar_error` en `main.py` |
| Electivos | Booleano y modo interactivo (además, `Cuente` y `leer`) |

`python pruebas.py` comprueba todo lo anterior: 109 pruebas, incluidas las siete
comprobaciones del 20 de noviembre y los tres programas de muestra.

## Cómo funciona, en cuatro pasos

Con `Pille total := a + 5 * 2`:

1. **Lexer** (`tokenizar`): `TIPO('Pille')`, `IDENTIFICADOR('total')`,
   `ASIGNACION(':=')`, `IDENTIFICADOR('a')`, `OPERADOR('+')`, `NUMERO('5')`,
   `OPERADOR('*')`, `NUMERO('2')`, `EOF('')`.
2. **Parser**: `instruccion` ve un `TIPO` y llama a `declaracion`. Para el valor,
   `expresion` llama a `termino`, que arma `5 * 2` *antes* de devolver el control.
   Por eso la multiplicación queda más abajo en el árbol que la suma.
3. **Intérprete**: `evaluar` llega a la suma, evalúa primero sus dos hijos (`a` y
   `5 * 2`) y después suma. Lo de más abajo se calcula primero.
4. **Entorno**: `declarar` guarda `total` con su tipo (`entero`), su valor y su línea.

## Preguntas que pueden hacer (con dónde señalar)

**¿Por qué cada regla es un método?** Porque así el código sigue la gramática línea
por línea: `declaracion()` hace `esperar("TIPO")`, `esperar("IDENTIFICADOR")`,
`esperar("ASIGNACION", ":=")` y `condicion()`, en el mismo orden que la regla.

**¿Por qué `expresion` usa un `while` y no se llama a sí misma?** Si la regla fuera
`expresion ::= expresion '+' termino`, el método empezaría llamándose sin leer
ningún token y nunca terminaría (recursión por la izquierda). Con
`termino (('+' | '-') termino)*` es un `while`, y la resta queda agrupada por la
izquierda: `10 - 3 - 2` es `(10 - 3) - 2`.

**¿Dónde está la recursión del "descenso recursivo"?** En `factor`: cuando ve `(`,
vuelve a llamar a `condicion`, que es la regla de más arriba.

**¿Por qué los nodos guardan tokens y no textos?** Para que el intérprete pueda dar
la línea y la columna de un error que solo aparece al ejecutar, como la división
por cero (columna del `/`).

**¿Para qué sirve la herencia de errores?** `main.py` tiene un solo
`except ErrorDeLenguaje` y atrapa los tres. Cada hija solo cambia `fase`.

**¿Cómo funciona el alcance de bloques?** Cada `{ }` crea un `Entorno` cuyo padre es
el actual. `buscar` mira primero el propio y luego sube por los padres. Al cerrar
el bloque se vuelve al padre (en un `finally`), y lo declarado adentro desaparece.

**¿Por qué `Tin` está más abajo que `Tan` en la gramática?** Porque se calcula
primero, igual que `*` antes que `+`: `a Tan b Tin c` es `a Tan (b Tin c)`.

**¿Cómo sabe `Pille` el tipo?** `tipo_de(valor)` mira el tipo de Python del primer
valor (`int` → entero, `float` → decimal...). Se usa `type` y no `isinstance`,
porque `isinstance(True, int)` da `True` y un booleano pasaría por entero.

**Sin `;`, ¿cómo sabe el parser dónde termina una instrucción?** Una expresión
termina cuando el siguiente token no es un operador. En `Pille a := b` seguido de
`c := 1`, después de `b` llega un `IDENTIFICADOR`, que no puede continuar la
expresión, así que `programa` empieza una instrucción nueva.

## Pendiente para la entrega del 23 de noviembre

- [ ] Revisar la ficha del README, sobre todo **por qué se llama ColombiaScript** y
      la decisión de diseño: están redactadas por nosotros a partir del README
      anterior, y el grupo debe estar de acuerdo para explicarlas en el video.
- [ ] Integrantes con nombre completo en el README y en el correo (hoy el README
      tiene solo los usuarios de GitHub).
- [ ] Video de 7 a 15 minutos, con todos a medio cuerpo y hablando. El link va solo
      en el correo, no en el repositorio.
- [ ] Repositorio público, con todo subido a la rama principal antes del lunes 23 a
      las 23:55.
- [ ] Correo con asunto `Lenguajes Formales - Proyecto final - ColombiaScript`.
- [ ] La guía exige `tokens.py`, `lexer.py`, `arbol.py`, `parser.py`, `interprete.py` y `main.py`
      en la raíz del repositorio de la entrega. En este repo están dentro de `lexer/`:
      definir en qué repositorio y con qué estructura se entrega.
- [ ] `reglas.txt` y `palabras_reservadas.md` (en el repo ColombiaScript) tienen la sintaxis de la primera
      entrega (`Si ... Eche accion`, sin bloques). No corren en el intérprete:
      dejarlos como historia o actualizarlos.
