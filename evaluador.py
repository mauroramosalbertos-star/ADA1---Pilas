"""Evaluador de expresiones aritméticas en notación posfija y prefija usando una Pila.

Los tokens se separan con espacios. Operadores: + - * / ^
Ejemplos:
    posfija: 3 4 + 2 *      -> 14
    prefija: * + 3 4 2      -> 14
"""
import math

from pila import Pila

OPERADORES = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
    "^": lambda a, b: a ** b,
}


def formatear(n):
    """Muestra 14.0 como 14 y redondea decimales largos."""
    if float(n).is_integer():
        return str(int(n))
    return str(round(n, 6))


def a_numero(token):
    """Devuelve el token como número o None si no lo es."""
    try:
        valor = float(token)
    except ValueError:
        return None
    return valor if math.isfinite(valor) else None


def _tokens(expresion):
    tokens = expresion.split()
    if not tokens:
        raise ValueError("La expresión está vacía.")
    return tokens


def _aplicar(op, izq, der):
    if op == "/" and der == 0:
        raise ZeroDivisionError("División entre cero.")
    return OPERADORES[op](izq, der)


def _encabezado():
    print(f"\n{'Token':<8}{'Acción':<40}Pila (base → tope)")
    print("-" * 70)


def _fila(token, accion, pila):
    contenido = [formatear(x) for x in pila]
    print(f"{token:<8}{accion:<40}{contenido}")


def evaluar_posfija(expresion, mostrar_pasos=True):
    """Recorre de izquierda a derecha. Número -> push. Operador -> pop, pop, calcula, push."""
    pila = Pila()
    if mostrar_pasos:
        _encabezado()
    for token in _tokens(expresion):
        valor = a_numero(token)
        if valor is not None:
            pila.push(valor)
            accion = f"push({formatear(valor)})"
        elif token in OPERADORES:
            if pila.tamanio() < 2:
                raise ValueError(f"Faltan operandos para '{token}'.")
            der = pila.pop()          # el primero en salir es el 2.º operando
            izq = pila.pop()
            resultado = _aplicar(token, izq, der)
            pila.push(resultado)
            accion = f"{formatear(izq)} {token} {formatear(der)} = {formatear(resultado)}"
        else:
            raise ValueError(f"Símbolo no válido: '{token}'.")
        if mostrar_pasos:
            _fila(token, accion, pila)
    if pila.tamanio() != 1:
        raise ValueError("Expresión mal formada: sobran operandos.")
    return pila.pop()


def evaluar_prefija(expresion, mostrar_pasos=True):
    """Recorre de derecha a izquierda. Operador -> pop (1.º operando), pop (2.º), calcula, push."""
    pila = Pila()
    if mostrar_pasos:
        _encabezado()
    for token in reversed(_tokens(expresion)):
        valor = a_numero(token)
        if valor is not None:
            pila.push(valor)
            accion = f"push({formatear(valor)})"
        elif token in OPERADORES:
            if pila.tamanio() < 2:
                raise ValueError(f"Faltan operandos para '{token}'.")
            izq = pila.pop()          # aquí el primero en salir es el 1.er operando
            der = pila.pop()
            resultado = _aplicar(token, izq, der)
            pila.push(resultado)
            accion = f"{formatear(izq)} {token} {formatear(der)} = {formatear(resultado)}"
        else:
            raise ValueError(f"Símbolo no válido: '{token}'.")
        if mostrar_pasos:
            _fila(token, accion, pila)
    if pila.tamanio() != 1:
        raise ValueError("Expresión mal formada: sobran operandos.")
    return pila.pop()


def main():
    print("=== Evaluador de expresiones con Pila ===")
    while True:
        print("\n1) Notación posfija   (ej: 3 4 + 2 *)")
        print("2) Notación prefija   (ej: * + 3 4 2)")
        print("3) Salir")
        opcion = input("Elige una opción: ").strip()
        if opcion == "3":
            print("¡Hasta luego!")
            break
        if opcion not in ("1", "2"):
            print("Opción no válida.")
            continue
        expresion = input("Escribe la expresión (tokens separados por espacio): ")
        try:
            if opcion == "1":
                resultado = evaluar_posfija(expresion)
            else:
                resultado = evaluar_prefija(expresion)
            print(f"\nResultado = {formatear(resultado)}")
        except (ValueError, ZeroDivisionError) as error:
            print(f"\nError: {error}")


if __name__ == "__main__":
    main()
