# Paso 5 · Construir una lista con una tupla ("DIGITO", c) por cada dígito
# Pruebas sugeridas: "a1b22c" -> [('DIGITO','1'), ('DIGITO','2'), ('DIGITO','2')]
#                    "abc"    -> []

t = "a1b22c"
tokens = []                # lista vacía donde guardamos las piezas
i = 0
while i < len(t):
    c = t[i]
    if c.isdigit():
        tokens.append(("DIGITO", c))   # la tupla es la "ficha": tipo y texto
    i += 1

print(tokens)
