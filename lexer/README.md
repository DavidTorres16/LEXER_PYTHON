# ColombiaScript

Lenguaje de programación interpretado, con palabras de la jerga colombiana,
desarrollado como proyecto final del curso de Lenguajes Formales.

## 1. Integrantes

- [@bcaceres19](https://github.com/bcaceres19)
- [@DavidTorres16](https://github.com/DavidTorres16)
- [@ItzMarlon2](https://github.com/ItzMarlon2)
- [@sams0ft](https://github.com/sams0ft)

## 2. Cómo ejecutar

Requiere Python 3.10 o superior. No usa librerías externas. Todo el proyecto está
en la carpeta `lexer/`, así que los comandos se corren desde ahí:

```bash
cd lexer
```

```bash
python main.py programa.txt            # ejecuta un programa
python main.py --arbol programa.txt    # muestra el árbol que arma el parser
python main.py --tokens programa.txt   # muestra los tokens que entrega el lexer
python main.py                         # modo interactivo (escriba chao para salir)
python pruebas.py                      # corre las 109 pruebas del proyecto
```

En la carpeta `programas/` están los tres programas de muestra, un ejemplo más
largo (`ejemplo.txt`), uno con los electivos (`electivos.txt`) y, en
`programas/errores/`, un ejemplo de cada tipo de error.

| Archivo | Qué hace |
| --- | --- |
| `tokens.py` | Clase `Token` y los errores `ErrorDeLenguaje`, `ErrorLexico`, `ErrorSintactico`, `ErrorSemantico` |
| `lexer.py` | `tokenizar(texto)`: convierte el texto en una lista de `Token` |
| `arbol.py` | Los nodos del árbol (`Numero`, `Declaracion`, `Si`, ...) y `mostrar_arbol` |
| `parser.py` | Clase `Parser`: un método por cada regla de la gramática; arma el árbol |
| `interprete.py` | Clases `Entorno` e `Interprete`: recorren el árbol y lo ejecutan |
| `main.py` | Une las tres fases, muestra los errores y tiene el modo interactivo |
| `pruebas.py` | Pruebas con la salida esperada calculada a mano |
| `programas/` | Programas de ejemplo en ColombiaScript |
| `docs/notas/` | Explicación del lexer, de la Sesión 3 y del parser e intérprete |

## 3. Ficha del lenguaje

### Nombre

**ColombiaScript**: "Colombia" porque todas sus palabras clave salen del habla
colombiana (*Pille*, *Eche*, *Melo*, *Paila*, *Dele*...), y "Script" porque es un
lenguaje de scripts interpretado, que se ejecuta línea por línea sin compilar.

### Tabla de traducción desde Java

| Qué | Java | ColombiaScript |
| --- | --- | --- |
| Tipos | `int edad = 20;` `double t = 31.5;` `String s = "hola";` `boolean b = true;` | `Pille edad := 20` `Pille t := 31.5` `Pille s := "hola"` `Pille b := Melo` (el tipo se deduce del valor) |
| Asignación | `edad = edad + 1;` | `edad := edad + 1` |
| Fin de instrucción | `;` | No hay: cada instrucción termina donde empieza la siguiente |
| Salida | `System.out.println(total);` | `mostrar(total)` |
| Condicional | `if (n >= 3) { ... } else { ... }` | `Si n >= 3 Eche { ... } Sino { ... }` |
| Ciclo | `while (n <= 5) { ... }` | `Dele n <= 5 Eche { ... }` |
| Ciclo con contador | `for (int i = 1; i <= 5; i++) { ... }` | `Cuente i Desde 1 Hasta 5 Eche { ... }` |
| Lógicos | `&&` `\|\|` `!` | `Tin` `Tan` `Nel` |
| Booleanos | `true` `false` | `Melo` `Paila` |
| Comparar igualdad | `==` | `==` o `=` |
| Lectura | `scanner.nextInt()` | `leer("pregunta")` |
| Comentario | `// ...` y `/* ... */` | `// ...` y `/* ... */` |

### Decisión de diseño: una sola palabra para declarar

En Java hay que escribir el tipo de cada variable (`int`, `double`, `String`). En
ColombiaScript todas se declaran con **`Pille`** ("¡pille!", fíjese en esto) y el
tipo se deduce del primer valor: `Pille edad := 20` es entero y `Pille saldo :=
45000.0` es decimal. El tipo no se pierde: desde ahí la variable solo acepta
valores de ese tipo, y `edad := "hola"` es un error.

Lo hicimos así porque el lenguaje nació como un motor de reglas para la vida
diaria (*"Si el saldo es menor o igual a cero, Eche mostrar Paila, no hay lucas"*),
y queríamos que se leyera casi como una frase. Por la misma razón la asignación es
`:=` y el `=` queda solo para comparar (`Si tiene_permiso = Melo`), y no hay `;`.

## 4. Gramática en EBNF

`::=` se lee "está formado por", `|` es "o", `*` es "cero o más veces" y `?` es
"cero o una vez". Lo que va entre comillas es un token exacto y lo que va en
MAYÚSCULAS es un tipo de token.

```ebnf
programa    ::= instruccion* EOF
instruccion ::= declaracion | asignacion | salida | condicional | ciclo | ciclo_para
declaracion ::= 'Pille' IDENTIFICADOR ':=' condicion
asignacion  ::= IDENTIFICADOR ':=' condicion
salida      ::= 'mostrar' '(' condicion ')'
condicional ::= 'Si' condicion 'Eche' bloque ('Sino' bloque)?
ciclo       ::= 'Dele' condicion 'Eche' bloque
ciclo_para  ::= 'Cuente' IDENTIFICADOR 'Desde' expresion 'Hasta' expresion 'Eche' bloque
bloque      ::= '{' instruccion* '}'
condicion   ::= conjuncion ('Tan' conjuncion)*
conjuncion  ::= negacion ('Tin' negacion)*
negacion    ::= 'Nel' negacion | comparacion
comparacion ::= expresion (COMPARADOR expresion)?
expresion   ::= termino (('+' | '-') termino)*
termino     ::= factor (('*' | '/') factor)*
factor      ::= NUMERO | CADENA | BOOLEANO | IDENTIFICADOR | lectura
              | '-' factor | '(' condicion ')'
lectura     ::= 'leer' '(' expresion? ')'
```

Tipos de token del lexer: `TIPO` (`Pille`), `RESERVADA` (`Si Eche Sino Dele
Cuente Desde Hasta Tin Tan Nel mostrar leer`), `BOOLEANO` (`Melo Paila`),
`IDENTIFICADOR`, `NUMERO`, `CADENA`, `ASIGNACION` (`:=`), `COMPARADOR` (`== = !=
< > <= >=`), `OPERADOR` (`+ - * /`), `SIMBOLO` (`( ) { } , .`) y `EOF`.

Precedencia, de lo que se calcula primero a lo último: paréntesis y menos unario,
`* /`, `+ -`, comparación, `Nel`, `Tin`, `Tan`.

## 5. Reglas de operaciones entre tipos

Los tipos son **entero**, **decimal**, **texto** y **booleano** (`Melo`/`Paila`).

| Operador | entero con entero | con al menos un decimal | texto con texto | texto con número o booleano | booleano con número |
| --- | --- | --- | --- | --- | --- |
| `+` | entero | decimal | une los textos | une los textos: `"Total: " + 5` da `Total: 5` | error |
| `-` `*` | entero | decimal | error | error | error |
| `/` | división entera, cortando hacia cero como Java: `7 / 2` da `3` | decimal: `7 / 2.0` da `3.5` | error | error | error |
| `-` unario | entero | decimal | error | error | error |

- Dividir por cero es error.
- `< > <= >=` solo comparan números. `== = !=` comparan valores del mismo tipo
  (un entero y un decimal sí se pueden comparar); `1 == "1"` es error.
- `Tin`, `Tan`, `Nel` y las condiciones de `Si` y `Dele` necesitan booleanos:
  `Si 5 Eche { }` es error.
- Una variable guarda siempre el tipo de su primer valor. Un decimal acepta enteros
  (`p := 3` guarda `3.0`); un entero no acepta decimales, y un booleano no es un
  número.

Errores semánticos que detecta el intérprete: variable no declarada, variable
declarada dos veces, valor de un tipo que la variable no acepta, división por
cero, operación no permitida entre tipos y ciclo de más de 100 000 vueltas.

Todos los errores muestran la fase, la línea, la columna y señalan el código:

```text
Error semántico en línea 3, columna 9: la variable 'saldo' no ha sido declarada
    mostrar(saldo)
            ^
linea = 3, columna = 9
```

## 6. Requerimientos electivos

1. **Tipo booleano.** `Melo` y `Paila` se guardan en variables y se usan en
   condiciones: `Pille listo := n > 3` y luego `Si listo Eche { ... }`. Un booleano
   no se acepta como número (se compara con `type`, no con `isinstance`).
2. **Modo interactivo.** `python main.py` sin archivo abre el prompt `cs>`, que
   ejecuta cada línea y recuerda las variables. Si una línea abre un bloque con
   `{`, sigue pidiendo líneas (`...`) hasta que se cierre. Los errores se muestran
   y el prompt sigue. Se sale con `chao` o Ctrl+D.

   ```text
   cs> Pille a := 2
   cs> mostrar(a * 3)
   6
   ```

Además, el intérprete tiene el **ciclo con contador** (`Cuente i Desde 1 Hasta 5
Eche { ... }`, donde `i` solo existe dentro del ciclo) y la **lectura de datos**
(`Pille edad := leer("¿Cuántos años tiene? ")` deduce el tipo de lo escrito, y
`edad := leer()` lo convierte al tipo de `edad`, con error si no se puede).
