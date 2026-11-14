# ColombiaScript — Cambios del lexer (tareas 8 a 16)

30 de octubre de 2026

> **Nota:** este documento describe el lexer como estaba el 30 de octubre. Después se agregaron el parser y el intérprete en la misma carpeta `lexer/`, `ejemplo.txt` pasó a `programas/`, `RELACIONAL` se llama `COMPARADOR` y hay más palabras reservadas (ver `ColombiaScript_parser_interprete.md` y el `README.md`).

## Resumen

El lexer de ColombiaScript ahora cubre las tareas 8 a 16 de la guía "Clase Día de los muertos", y sus 46 pruebas coinciden con lo calculado a mano.

- **Viernes (sesión 1, tareas 8 a 12):** delimitadores, operadores de dos caracteres, palabras de control, comentarios de bloque y token EOF.
- **Sábado (sesión 2, tareas 13 a 16):** clase `Token`, excepción `ErrorLexico`, `main.py` que muestra la tabla de tokens y el programa `ejemplo.txt`.
- **Adaptación:** la guía usa Java como ejemplo; todo se reescribió con la sintaxis de ColombiaScript (`Pille`, `:=`, `Si ... Eche`).

## Estructura de archivos

El código se repartió en un archivo por responsabilidad, como sugiere la guía, dentro de la carpeta `lexer/`.

| Archivo | Estado | Contenido |
| --- | --- | --- |
| `tokens.py` | Nuevo | Clases `Token` y `ErrorLexico` |
| `lexer.py` | Renombrado desde `lexer_colombiascript.py` y reescrito | Función `tokenizar` y `es_declaracion`, sin código de pruebas |
| `main.py` | Nuevo | Lee un archivo y muestra la tabla de tokens |
| `ejemplo.txt` | Nuevo | Programa de demostración de 17 líneas |
| `pruebas.py` | Nuevo | 46 pruebas; incluye las de los puntos 4, 5, 6 y 6.1 adaptadas a `Token` |

## Sesión 1 (viernes): tareas 8 a 12

Las cinco tareas se resolvieron en `lexer.py` ampliando `SIMBOLOS` y agregando dos bloques nuevos a `tokenizar`.

| Tarea | Qué cambió | Ejemplo |
| --- | --- | --- |
| 8. Delimitadores | `( ) { } , .` se agregaron a `SIMBOLOS` como `SIMBOLO`. Un `.` solo forma parte de un número si lo sigue un dígito. | `System.out` da identificador, `.`, identificador; `3.14` es un solo `NUMERO` |
| 9. Operadores de dos caracteres | `==` y `!=` se agregaron a `SIMBOLOS`, antes que `=`, para que gane el más largo. Un `!` solo cae en el error general. | `x == 5` da 3 tokens; `x ! 5` da error en la columna 3 |
| 10. Control y booleanos | `Si Eche Tin Tan mostrar` ya eran `RESERVADA` y `Melo Paila` ya eran `BOOLEANO`. La palabra se lee completa antes de comparar. | `Sillo` y `Tin_x` son identificadores |
| 11. Comentarios de bloque | Nuevo bloque que busca `*/`, suma las líneas que atraviesa y reinicia la columna. Sin cierre lanza error en la posición donde empezó. | Un comentario de 3 líneas deja la siguiente declaración en la línea 4 |
| 12. EOF | `tokenizar` agrega al final `EOF` con la línea y columna finales. | `Pille x := 5` termina en `EOF` 1:13; el texto vacío da solo `EOF` 1:1 |

Como ahora todo termina en `EOF`, `es_declaracion` ignora ese último token al comprobar la forma `Pille <id> := <valor>`.

## Sesión 2 (sábado): tareas 13 a 16

Las tuplas se reemplazaron por objetos y el código se separó en módulos.

| Tarea | Qué cambió | Resultado |
| --- | --- | --- |
| 13. Clase `Token` | `@dataclass` con `tipo`, `texto`, `linea` y `columna`, más un `__str__` legible. Las pruebas anteriores se reescribieron con `Token` y dan lo mismo. | `NUMERO('5') en 1:9` |
| 14. `ErrorLexico` | Hereda de `Exception` y guarda `linea` y `columna`. El lexer la lanza en lugar de `SyntaxError`. | `Error léxico en línea 2, columna 14: carácter '@' no reconocido` |
| 15. `main.py` | Recibe la ruta con `sys.argv[1]`, lee el archivo en UTF-8 e imprime la tabla `LINEA COL TIPO TEXTO`. Ante un error léxico imprime el mensaje y termina con código 1, sin traza de Python. También avisa si falta el argumento o el archivo no existe. | `python main.py ejemplo.txt` |
| 16. `ejemplo.txt` | 17 líneas con comentarios `//` y `/* */`, enteros, decimales, negativos, booleanos, cadenas, operadores relacionales y reglas `Si ... Eche`. Una prueba verifica que se tokeniza sin errores y que las líneas 2 y 3 coinciden con lo calculado a mano. | Primer token: `Pille` en la línea 2, columna 1 (la línea 1 es comentario) |

## Decisiones de adaptación

Estas decisiones se apartan del texto literal de la guía; conviene confirmarlas con el grupo.

- **Ejemplos en ColombiaScript.** Los ejemplos en Java (`int x = 5;`, `(a+b)*2;`) no aplican porque el lenguaje no tiene `;` ni `+`. Se reescribieron con `Pille ... :=`, y el `;` sigue siendo error léxico.
- **Decimales válidos.** Antes `18.5` daba error. Ahora es un `NUMERO`, porque la gramática del README incluye decimales y la tarea 16 los pide.
- **Tipo de `==` y `!=`.** Salen como `RELACIONAL`, igual que `=`, en vez de `OPERADOR` como dice la guía, para ser coherentes con el lexer existente.
- **Mensajes de error.** Pasaron de `Línea 1, columna 14: carácter inesperado '@'` al formato de la guía: `Error léxico en línea 1, columna 14: carácter '@' no reconocido`.
- **Sin `else` ni `while`.** El lenguaje no los tiene, así que la tarea 10 se verificó con las palabras que sí existen.
- **Archivo renombrado.** `lexer_colombiascript.py` pasó a `lexer.py` y sus pruebas a `pruebas.py`, que es la estructura que sugiere la guía. El código de la carpeta `lexer/` aún no está en git.

## Cómo ejecutar y verificar

Todos los comandos se corren desde la carpeta `lexer/`.

```bash
python pruebas.py              # Resumen: 46 de 46 pruebas coinciden
python main.py ejemplo.txt     # tabla de tokens del programa de demostración
python main.py otro.txt        # con un error léxico imprime solo el mensaje
```

`pruebas.py` solo imprime las pruebas que no coinciden, más la línea de resumen. Los resultados esperados se calcularon a mano antes de ejecutar; la única corrección fue una columna mal contada en la prueba de la cadena sin cerrar (23, no 24).
