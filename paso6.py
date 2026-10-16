# Paso 6 · El ejercicio anterior convertido en función

def digitos(texto):
    tokens = []
    i = 0
    while i < len(texto):
        c = texto[i]
        if c.isdigit():
            tokens.append(("DIGITO", c))
        i += 1
    return tokens          # devuelve la lista; NO la imprime adentro


# Se llama con tres textos distintos
print(digitos("a1b22c"))   # [('DIGITO', '1'), ('DIGITO', '2'), ('DIGITO', '2')]
print(digitos("abc"))      # []
print(digitos("x9"))       # [('DIGITO', '9')]
