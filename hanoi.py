"""Torres de Hanoi con interfaz gráfica (tkinter). Cada torre es un objeto Pila.

Cómo jugar: clic en la torre de origen y luego en la de destino.
También puedes pulsar "Resolver" para ver la solución automática,
que se calcula con una segunda Pila de tareas (simula la recursión).
"""
import random
import tkinter as tk

from pila import Pila

ANCHO, ALTO = 900, 560
BASE_Y = 460
ALTO_DISCO = 26
TOPE_TORRE_Y = 190
ALTURA_VUELO = 140
TORRES_X = (150, 450, 750)
NOMBRES = ("A", "B", "C")
COLORES = ["#ff6b6b", "#ff9f43", "#feca57", "#1dd1a1",
           "#48dbfb", "#54a0ff", "#a29bfe", "#f368e0"]
FONDO = "#0b1026"


# ---------------------------------------------------------------- utilidades
def mezclar(c1, c2, t):
    """Mezcla dos colores hex. t=0 -> c1, t=1 -> c2."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def rect_redondeado(c, x1, y1, x2, y2, r, **kw):
    p = [x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
         x2, y1 + r, x2, y2 - r, x2, y2 - r, x2, y2, x2 - r, y2, x2 - r, y2,
         x1 + r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y2 - r, x1, y1 + r,
         x1, y1 + r, x1, y1]
    return c.create_polygon(p, smooth=True, **kw)


class Boton(tk.Label):
    """Botón plano con efecto hover (se ve igual en Windows, Mac y Linux)."""

    def __init__(self, master, texto, color, comando, ancho):
        super().__init__(master, text=texto, bg=color, fg="white", width=ancho,
                         font=("Helvetica", 12, "bold"), pady=8, cursor="hand2")
        self.bind("<Enter>", lambda e: self.config(bg=mezclar(color, "#ffffff", 0.2)))
        self.bind("<Leave>", lambda e: self.config(bg=color))
        self.bind("<Button-1>", lambda e: comando())


# ------------------------------------------------------- solución con una Pila
def generar_movimientos(n, origen, destino, auxiliar):
    """Genera los movimientos (origen, destino) usando una Pila de tareas
    en lugar de recursión. Cada tarea es (discos, origen, destino, auxiliar)."""
    tareas = Pila()
    tareas.push((n, origen, destino, auxiliar))
    while not tareas.esta_vacia():
        k, o, d, a = tareas.pop()
        if k == 1:
            yield (o, d)
        else:
            # Se apilan al revés para que salgan en el orden correcto:
            tareas.push((k - 1, a, d, o))   # 3) n-1 discos de auxiliar a destino
            tareas.push((1, o, d, a))       # 2) el disco grande a destino
            tareas.push((k - 1, o, a, d))   # 1) n-1 discos de origen a auxiliar


# ------------------------------------------------------------------ aplicación
class HanoiApp:
    def __init__(self, root):
        self.root = root
        self._epoca = 0
        root.title("Torres de Hanoi")
        root.configure(bg=FONDO)
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=ANCHO, height=ALTO,
                                highlightthickness=0, bg=FONDO)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.al_clic)

        panel = tk.Frame(root, bg=FONDO)
        panel.pack(pady=12)
        tk.Label(panel, text="Discos:", bg=FONDO, fg="#c7d2fe",
                 font=("Helvetica", 12, "bold")).grid(row=0, column=0, padx=(0, 6))
        self.var_n = tk.StringVar(value="4")
        tk.Spinbox(panel, from_=3, to=8, width=3, textvariable=self.var_n,
                   command=self.reiniciar, state="readonly", justify="center",
                   font=("Helvetica", 13, "bold")).grid(row=0, column=1, padx=(0, 14))
        Boton(panel, "▶  Resolver", "#10b981", self.resolver_auto, 13).grid(row=0, column=2, padx=5)
        Boton(panel, "⏸  Pausar", "#f59e0b", self.pausar, 11).grid(row=0, column=3, padx=5)
        Boton(panel, "⏭  Paso", "#3b82f6", self.paso, 9).grid(row=0, column=4, padx=5)
        Boton(panel, "↺  Reiniciar", "#ef4444", self.reiniciar, 12).grid(row=0, column=5, padx=5)
        tk.Label(panel, text="Velocidad:", bg=FONDO, fg="#c7d2fe",
                 font=("Helvetica", 12, "bold")).grid(row=0, column=6, padx=(14, 4))
        self.velocidad = tk.Scale(panel, from_=1, to=10, orient="horizontal",
                                  showvalue=False, length=110, bg=FONDO,
                                  troughcolor="#312e81", highlightthickness=0)
        self.velocidad.set(6)
        self.velocidad.grid(row=0, column=7)

        random.seed(7)
        self.estrellas = [(random.randint(0, ANCHO), random.randint(0, BASE_Y - 40),
                           random.choice((1, 1, 2))) for _ in range(70)]
        self.reiniciar()

    # ------------------------------------------------------------ estado
    def reiniciar(self):
        self._epoca += 1                      # cancela animaciones pendientes
        self.auto = False
        self.gen = None
        self.animando = False
        self.seleccion = None
        self.n = int(self.var_n.get())
        self.torres = [Pila(), Pila(), Pila()]
        for tam in range(self.n, 0, -1):      # el disco más grande queda abajo
            self.torres[0].push(tam)
        self.movimientos = 0
        self.mensaje = "Clic en la torre de origen y luego en la de destino"
        self.dibujar()

    def resuelto(self):
        return len(self.torres[2]) == self.n

    def _valido(self, o, d):
        if self.torres[o].esta_vacia():
            return False
        return self.torres[d].esta_vacia() or self.torres[o].peek() < self.torres[d].peek()

    # ----------------------------------------------------------- dibujo
    def _centro_y(self, nivel):
        return BASE_Y - nivel * ALTO_DISCO - ALTO_DISCO / 2

    def _disco(self, cx, cy, tam, tag, resalte=False):
        c = self.canvas
        w = 56 + tam * 20
        h = ALTO_DISCO - 4
        color = COLORES[(tam - 1) % len(COLORES)]
        rect_redondeado(c, cx - w / 2 + 3, cy - h / 2 + 4, cx + w / 2 + 3, cy + h / 2 + 4,
                        10, fill="#050816", outline="", tags=tag)
        rect_redondeado(c, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 10,
                        fill=color, tags=tag,
                        outline="#ffffff" if resalte else mezclar(color, "#000000", 0.3),
                        width=3 if resalte else 1)
        rect_redondeado(c, cx - w / 2 + 8, cy - h / 2 + 3, cx + w / 2 - 8, cy - h / 2 + 8, 3,
                        fill=mezclar(color, "#ffffff", 0.45), outline="", tags=tag)
        c.create_text(cx, cy + 1, text=str(tam), fill="#1e1b4b",
                      font=("Helvetica", 11, "bold"), tags=tag)

    def dibujar(self):
        c = self.canvas
        c.delete("all")
        franjas = 70
        for i in range(franjas):
            c.create_rectangle(0, ALTO * i / franjas, ANCHO, ALTO * (i + 1) / franjas + 1,
                               fill=mezclar(FONDO, "#312e81", i / franjas), outline="")
        for x, y, r in self.estrellas:
            c.create_oval(x, y, x + r, y + r, fill="#c7d2fe", outline="")

        c.create_text(ANCHO / 2, 38, text="TORRES DE HANOI", fill="#e0e7ff",
                      font=("Helvetica", 28, "bold"))
        c.create_text(ANCHO / 2, 78, fill="#a5b4fc", font=("Helvetica", 14),
                      text=f"Movimientos: {self.movimientos}     •     "
                           f"Mínimo posible: {2 ** self.n - 1}")

        rect_redondeado(c, 40, BASE_Y, ANCHO - 40, BASE_Y + 26, 12, fill="#8b5a2b", outline="")
        rect_redondeado(c, 40, BASE_Y, ANCHO - 40, BASE_Y + 10, 8, fill="#a97142", outline="")

        for i, x in enumerate(TORRES_X):
            if self.seleccion == i:
                rect_redondeado(c, x - 80, TOPE_TORRE_Y - 25, x + 80, BASE_Y, 22,
                                fill="#1e1b4b", outline="#facc15", width=2)
            rect_redondeado(c, x - 7, TOPE_TORRE_Y, x + 7, BASE_Y, 6,
                            fill="#e5e7eb", outline="#9ca3af")
            c.create_text(x, BASE_Y + 50, text=NOMBRES[i], fill="#c7d2fe",
                          font=("Helvetica", 20, "bold"))

        for i, torre in enumerate(self.torres):
            for nivel, tam in enumerate(torre):
                tope = nivel == len(torre) - 1
                self._disco(TORRES_X[i], self._centro_y(nivel), tam, "disco",
                            resalte=(self.seleccion == i and tope))

        if self.resuelto():
            rect_redondeado(c, 230, 100, 670, 178, 18, fill="#064e3b", outline="#34d399", width=3)
            c.create_text(ANCHO / 2, 128, text="¡RESUELTO!", fill="#6ee7b7",
                          font=("Helvetica", 24, "bold"))
            c.create_text(ANCHO / 2, 158, fill="#d1fae5", font=("Helvetica", 13),
                          text=f"{self.movimientos} movimientos (mínimo: {2 ** self.n - 1})")
        else:
            c.create_text(ANCHO / 2, ALTO - 22, text=self.mensaje, fill="#e0e7ff",
                          font=("Helvetica", 13))

    def _avisar(self, texto):
        self.mensaje = texto
        self.dibujar()

    # ------------------------------------------------------ movimiento
    def _ruta(self, x0, y0, x1, y1, paso):
        puntos = []

        def tramo(ax, ay, bx, by):
            k = max(1, int(max(abs(bx - ax), abs(by - ay)) / paso))
            for i in range(1, k + 1):
                puntos.append((ax + (bx - ax) * i / k, ay + (by - ay) * i / k))

        tramo(x0, y0, x0, ALTURA_VUELO)
        tramo(x0, ALTURA_VUELO, x1, ALTURA_VUELO)
        tramo(x1, ALTURA_VUELO, x1, y1)
        return puntos

    def mover(self, o, d, al_terminar=None):
        epoca = self._epoca
        tam = self.torres[o].pop()
        x0, y0 = TORRES_X[o], self._centro_y(len(self.torres[o]))
        x1, y1 = TORRES_X[d], self._centro_y(len(self.torres[d]))
        self.animando = True
        self.dibujar()
        ruta = self._ruta(x0, y0, x1, y1, 6 + self.velocidad.get() * 5)

        def tick(i=0):
            if epoca != self._epoca:
                return
            self.canvas.delete("vuelo")
            if i < len(ruta):
                self._disco(ruta[i][0], ruta[i][1], tam, "vuelo", resalte=True)
                self.root.after(16, lambda: tick(i + 1))
            else:
                self.torres[d].push(tam)
                self.movimientos += 1
                self.animando = False
                self.mensaje = f"Movimiento {self.movimientos}: {NOMBRES[o]} → {NOMBRES[d]}"
                self.dibujar()
                if al_terminar:
                    al_terminar()

        tick()

    # ---------------------------------------------------------- juego manual
    def al_clic(self, ev):
        if self.animando or self.auto or self.resuelto():
            return
        idx = min(2, max(0, int(ev.x // (ANCHO / 3))))
        if self.seleccion is None:
            if self.torres[idx].esta_vacia():
                self._avisar("Esa torre está vacía, elige otra.")
            else:
                self.seleccion = idx
                self._avisar(f"Disco listo en {NOMBRES[idx]}. Elige la torre de destino.")
        elif idx == self.seleccion:
            self.seleccion = None
            self._avisar("Selección cancelada.")
        elif not self._valido(self.seleccion, idx):
            self.seleccion = None
            self._avisar("¡Movimiento inválido! No puedes poner un disco grande sobre uno pequeño.")
        else:
            origen, self.seleccion, self.gen = self.seleccion, None, None
            self.mover(origen, idx)

    # ------------------------------------------------------ solución automática
    def _nueva_solucion(self):
        self.reiniciar()
        self.gen = generar_movimientos(self.n, 0, 2, 1)

    def resolver_auto(self):
        if self.auto:
            return
        if self.gen is None:
            self._nueva_solucion()
        self.auto = True
        if not self.animando:
            self._siguiente()

    def _siguiente(self):
        if not self.auto:
            return
        try:
            o, d = next(self.gen)
        except StopIteration:
            self.auto, self.gen = False, None
            return
        self.mover(o, d, al_terminar=lambda: self.root.after(120, self._siguiente))

    def pausar(self):
        self.auto = False
        if not self.animando:
            self._avisar("Pausado. Pulsa Resolver para continuar.")

    def paso(self):
        if self.animando or self.auto:
            return
        if self.gen is None:
            self._nueva_solucion()
        try:
            o, d = next(self.gen)
        except StopIteration:
            self.gen = None
            return
        self.mover(o, d)


def main():
    root = tk.Tk()
    HanoiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
