# Paso 4 · Recorrer un texto e imprimir solo los dígitos
# Pruebas sugeridas: "a1b22c" -> 1, 2, 2 | "abc" -> nada | "x9" -> 9

t = "a1b22c"
i = 0                      # posición actual (el "dedo" del lexer)
while i < len(t):          # mientras queden caracteres por leer
    if t[i].isdigit():     # Paso 3: preguntamos si es dígito
        print(t[i])
    i += 1                 # avanzamos una posición
