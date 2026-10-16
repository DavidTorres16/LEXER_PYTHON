# Paso 7 · digitos(texto) lanza un error si encuentra algo que no es dígito ni letra

def digitos(texto):
    tokens = []
    i = 0
    while i < len(texto):
        c = texto[i]
        if c.isdigit():
            tokens.append(("DIGITO", c))
        elif c.isalpha():
            pass                       # las letras se aceptan, pero no se guardan
        else:
            raise SyntaxError(f"Carácter inesperado '{c}' en la posición {i}")
        i += 1
    return tokens


# Prueba sin error
try:
    print(digitos("a1b"))              # [('DIGITO', '1')]
except SyntaxError as e:
    print("Error:", e)

# Prueba con error
try:
    print(digitos("a1@"))
except SyntaxError as e:
    print("Error:", e)                 # Error: Carácter inesperado '@' en la posición 2
