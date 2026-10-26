"""Clase Pila (estructura LIFO: el último en entrar es el primero en salir)."""


class Pila:
    def __init__(self):
        self._items = []

    def push(self, elemento):
        """Apila un elemento en el tope."""
        self._items.append(elemento)

    def pop(self):
        """Quita y devuelve el elemento del tope."""
        if self.esta_vacia():
            raise IndexError("La pila está vacía")
        return self._items.pop()

    def peek(self):
        """Devuelve el elemento del tope sin quitarlo."""
        if self.esta_vacia():
            raise IndexError("La pila está vacía")
        return self._items[-1]

    def esta_vacia(self):
        return len(self._items) == 0

    def tamanio(self):
        return len(self._items)

    def vaciar(self):
        self._items.clear()

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        """Recorre de la base hacia el tope."""
        return iter(self._items)

    def __str__(self):
        return f"{self._items}  <- tope"
