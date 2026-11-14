# ColombiaScript — Sesión 3: por qué necesitamos clases

13 de noviembre de 2026

> **Nota:** después de esta sesión se agregaron el parser y el intérprete en la misma carpeta `lexer/`, y `main.py` pasó a ejecutar programas. El recorrido de tokens de esta sesión ahora se ve con `python main.py --tokens programa.txt`. Lo que sigue a esta sesión está en `ColombiaScript_parser_interprete.md`.

## Qué pide la guía y dónde está

| Punto de la guía | Archivo | Qué hay |
| --- | --- | --- |
| 1. Clase `Token` | `tokens.py` | `@dataclass` con `tipo`, `texto`, `linea`, `columna` y `__str__` que imprime `NUMERO('5') en 1:12` |
| 2. Clase `ErrorLexico` | `tokens.py` | Hereda de `Exception`, guarda `linea` y `columna`; `str(e)` es el mensaje completo |
| 3. Prototipo de `Parser` | `parser.py` | Atributos `tokens` y `pos`; métodos `actual()` (mira sin moverse) y `avanzar()` (devuelve y pasa al siguiente) |
| 3. Recorrido hasta EOF | `main.py` | `imprimir_tokens(parser)` imprime cada token, incluido EOF |
| 4. Archivos separados | `lexer/` | `tokens.py`, `lexer.py`, `parser.py`, `main.py` (Python 3.10 o superior) |

`lexer.py` ya devolvía objetos `Token` y lanzaba `ErrorLexico` desde la sesión anterior; lo nuevo es `parser.py`, el recorrido en `main.py` y las pruebas del Parser.

## Cómo se ejecuta

Desde la carpeta `lexer/`:

```text
$ python main.py --tokens programa.txt (contiene: Pille x := 5)
TIPO('Pille') en 1:1
IDENTIFICADOR('x') en 1:7
ASIGNACION(':=') en 1:9
NUMERO('5') en 1:12
EOF('') en 1:13

$ python main.py programa_error.txt    (contiene: Pille x := 5 @)
Error léxico en línea 1, columna 14: carácter '@' no reconocido
    Pille x := 5 @
                 ^
linea = 1, columna = 14

$ python pruebas.py                    (todas las pruebas coinciden)
```

Es el mismo ejemplo de la guía (`int x = 5;`) traducido a ColombiaScript: `Pille` en lugar de `int`, `:=` en lugar de `=`, y sin `;`, que en nuestro lenguaje es error léxico.

## Cómo fluye el programa

```text
programa.txt ──► tokenizar(texto) ──► [Token, Token, ..., Token EOF] ──► Parser(tokens) ──► imprimir_tokens
                       │
                       └── si hay un carácter desconocido: raise ErrorLexico ──► main.py lo atrapa con except
```

## Los tres problemas y cómo los resolvimos

1. **Las tuplas no dicen qué es cada dato.** Con `("NUMERO", "5", 1, 12)` había que recordar que la columna es `t[3]`. Ahora es `t.columna`. Si mañana se agrega un dato al token, los nombres no se corren como los índices.
2. **Un error que es solo un texto.** `ErrorLexico` guarda `linea` y `columna` como atributos. `main.py` imprime `e` (el mensaje) y lee `e.linea` y `e.columna` por separado, sin buscarlas dentro del texto. Más adelante se podrá distinguir de un `ErrorSintactico` con otro `except`.
3. **Varias funciones que comparten una posición.** La lista y la posición viven dentro del objeto `Parser` (`self.tokens`, `self.pos`). Cada método las lee y las cambia directamente, sin pasarlas como parámetro ni devolverlas, así que no hay un `pos =` que se pueda olvidar.

## Preguntas de la sustentación (señalando el código)

**¿Qué diferencia hay entre la clase `Parser` y un objeto `Parser`?**
La clase es la plantilla: `class Parser:` en `parser.py` dice que cada parser tendrá `tokens`, `pos`, `actual()` y `avanzar()`. Un objeto es un ejemplar concreto creado con esa plantilla: `parser = Parser(tokens)` en `main.py`. Se pueden crear muchos objetos de una misma clase.

**¿Qué es `self` y por qué no se escribe al llamar un método?**
`self` es el objeto con el que se está trabajando en ese momento. En `avanzar()`, `self.pos += 1` cambia la posición de *ese* parser. Al escribir `parser.avanzar()`, Python pasa `parser` como `self` automáticamente; es como si escribiera `Parser.avanzar(parser)`.

**¿Qué pasa si crean dos objetos `Parser` con listas distintas y avanzan solo uno?**
Solo cambia la posición del que avanzó, porque cada objeto tiene su propia copia de `tokens` y `pos`. Está probado en `pruebas.py` (sección "Parser"): después de dos `p1.avanzar()`, `p1.pos` es 2 y `p2.pos` sigue en 0.

**¿Por qué la posición es un atributo del parser y no una variable local de una función?**
Una variable local desaparece cuando la función termina, y cada función tendría la suya. El parser tendrá muchos métodos (uno por regla de la gramática) que deben leer la *misma* posición. Como atributo (`self.pos`) se conserva entre llamadas y todos los métodos la comparten. Una variable global también se compartiría, pero solo permitiría un parser a la vez y complicaría las pruebas.

**¿Qué ganaron al cambiar las tuplas por objetos `Token`?**
El código se lee solo: `token.tipo != "EOF"` en vez de `token[0] != "EOF"`. Además, gracias a `__str__` el token se imprime legible con un simple `print(token)`, y `@dataclass` genera el constructor y la comparación `==` (las pruebas comparan listas de `Token` directamente).

## Decisiones que conviene saber explicar

- **`avanzar()` no pasa de EOF.** Si se llama estando en EOF, se queda ahí. Así el parser nunca intenta leer fuera de la lista (`IndexError`). Hay una prueba que llama `avanzar()` diez veces y verifica que queda en EOF.
- **`avanzar()` devuelve el token.** No era obligatorio, pero en la sesión 4 sirve para escribir `nombre = self.avanzar()` y quedarse con el token consumido.
- **El EOF también se imprime.** El ciclo de `imprimir_tokens` termina al llegar a EOF y lo imprime después del ciclo; la rúbrica da la mitad del punto si se salta EOF.
- **`programa.txt` no termina en salto de línea**, para que la salida coincida con la de la guía (EOF en `1:13`). Si el archivo termina en `\n`, el EOF sale en `2:1`, lo cual también es correcto.
- **El nombre `parser.py` no choca con Python.** El módulo `parser` de la biblioteca estándar se eliminó en Python 3.10, por eso la guía pide 3.10 o superior.
