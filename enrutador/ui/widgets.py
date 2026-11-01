import tkinter as tk

from . import tema


def rect_redondeado(c, x0, y0, x1, y1, r, **kw):
    pts = [x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r, x1, y1 - r, x1, y1,
           x1 - r, y1, x0 + r, y1, x0, y1, x0, y1 - r, x0, y0 + r, x0, y0]
    return c.create_polygon(pts, smooth=True, **kw)


class Boton(tk.Canvas):
    def __init__(self, master, texto, comando, ancho=150, alto=40, estilo="primario",
                 fondo=tema.PANEL, tam=11):
        super().__init__(master, width=ancho, height=alto, bg=fondo, highlightthickness=0,
                         bd=0, cursor="hand2")
        self.comando = comando
        self.paleta = tema.BOTONES[estilo]
        self.activo = True
        self.adentro = False
        self.w, self.h = ancho, alto
        self.forma = rect_redondeado(self, 1, 1, ancho - 1, alto - 1, min(14, alto // 2),
                                     fill=self.paleta["normal"], outline=self.paleta["borde"])
        self.etiqueta = self.create_text(ancho / 2, alto / 2, text=texto, font=tema.fuente(tam, True),
                                         fill=self.paleta["texto"])
        self.bind("<Enter>", self.entrar)
        self.bind("<Leave>", self.salir)
        self.bind("<ButtonPress-1>", self.presionar)
        self.bind("<ButtonRelease-1>", self.soltar)

    def pintar(self, presionado=False):
        p = self.paleta
        if not self.activo:
            relleno, borde, texto = (tema.DESACTIVADO["normal"], tema.DESACTIVADO["borde"],
                                     tema.DESACTIVADO["texto"])
        else:
            clave = "presionado" if presionado else ("hover" if self.adentro else "normal")
            relleno, borde, texto = p[clave], p["borde"], p["texto"]
        self.itemconfigure(self.forma, fill=relleno, outline=borde)
        self.itemconfigure(self.etiqueta, fill=texto)

    def set_activo(self, activo):
        self.activo = activo
        self.config(cursor="hand2" if activo else "arrow")
        self.pintar()

    def set_texto(self, texto):
        self.itemconfigure(self.etiqueta, text=texto)

    def entrar(self, _):
        self.adentro = True
        self.pintar()

    def salir(self, _):
        self.adentro = False
        self.pintar()

    def presionar(self, _):
        if self.activo:
            self.pintar(True)

    def soltar(self, ev):
        if not self.activo:
            return
        self.pintar()
        if 0 <= ev.x <= self.w and 0 <= ev.y <= self.h:
            self.comando()


class Interruptor(tk.Frame):
    def __init__(self, master, texto, variable, comando=None, fondo=tema.PANEL):
        super().__init__(master, bg=fondo)
        self.var = variable
        self.comando = comando
        self.lienzo = tk.Canvas(self, width=40, height=22, bg=fondo, highlightthickness=0, cursor="hand2")
        self.lienzo.pack(side="left")
        self.rotulo = tk.Label(self, text=texto, bg=fondo, fg=tema.TEXTO, font=tema.fuente(10),
                               cursor="hand2")
        self.rotulo.pack(side="left", padx=(10, 0))
        for w in (self.lienzo, self.rotulo):
            w.bind("<Button-1>", self.alternar)
        self.dibujar()

    def alternar(self, _=None):
        self.var.set(not self.var.get())
        self.dibujar()
        if self.comando:
            self.comando()

    def dibujar(self):
        c = self.lienzo
        c.delete("all")
        on = self.var.get()
        rect_redondeado(c, 1, 1, 39, 21, 10, fill=tema.ACENTO if on else tema.BORDE, outline="")
        x = 29 if on else 11
        c.create_oval(x - 8, 3, x + 8, 19, fill="white", outline="")


class Selector(tk.Frame):
    def __init__(self, master, variable, minimo, maximo, paso, formato="{:.1f}", decimales=1,
                 comando=None, fondo=tema.PANEL):
        super().__init__(master, bg=fondo)
        self.var, self.minimo, self.maximo, self.paso = variable, minimo, maximo, paso
        self.formato, self.decimales, self.comando = formato, decimales, comando
        Boton(self, "-", lambda: self.cambiar(-1), ancho=32, alto=32, estilo="secundario",
              fondo=fondo, tam=13).pack(side="left")
        self.valor = tk.Label(self, width=8, bg=fondo, fg=tema.TEXTO, font=tema.fuente(11, True))
        self.valor.pack(side="left")
        Boton(self, "+", lambda: self.cambiar(1), ancho=32, alto=32, estilo="secundario",
              fondo=fondo, tam=13).pack(side="left")
        self.mostrar()

    def cambiar(self, signo):
        v = self.var.get() + signo * self.paso
        self.var.set(round(min(self.maximo, max(self.minimo, v)), self.decimales))
        self.mostrar()
        if self.comando:
            self.comando()

    def mostrar(self):
        self.valor.config(text=self.formato.format(self.var.get()))


class Deslizador(tk.Canvas):
    def __init__(self, master, variable, minimo, maximo, ancho=150, fondo=tema.PANEL):
        super().__init__(master, width=ancho, height=24, bg=fondo, highlightthickness=0, cursor="hand2")
        self.var, self.minimo, self.maximo, self.w = variable, minimo, maximo, ancho
        self.bind("<Button-1>", self.mover)
        self.bind("<B1-Motion>", self.mover)
        self.dibujar()

    def mover(self, ev):
        f = min(1.0, max(0.0, (ev.x - 10) / (self.w - 20)))
        self.var.set(int(round(self.minimo + f * (self.maximo - self.minimo))))
        self.dibujar()

    def dibujar(self):
        self.delete("all")
        f = (self.var.get() - self.minimo) / (self.maximo - self.minimo)
        x = 10 + f * (self.w - 20)
        self.create_line(10, 12, self.w - 10, 12, fill=tema.BORDE, width=4, capstyle="round")
        self.create_line(10, 12, x, 12, fill=tema.ACENTO, width=4, capstyle="round")
        self.create_oval(x - 8, 4, x + 8, 20, fill="white", outline=tema.ACENTO, width=2)


class Tarjeta(tk.Frame):
    def __init__(self, master, titulo, tam=16, acento=False):
        super().__init__(master, bg=tema.TARJETA, padx=14, pady=8,
                         highlightthickness=2 if acento else 0, highlightbackground=tema.ACENTO,
                         highlightcolor=tema.ACENTO)
        tk.Label(self, text=titulo, bg=tema.TARJETA, fg=tema.ACENTO if acento else tema.MUTED,
                 font=tema.fuente(8, True), anchor="w").pack(fill="x")
        self.valor = tk.Label(self, text="-", bg=tema.TARJETA, fg=tema.ACENTO if acento else tema.TEXTO,
                              font=tema.fuente(tam, True), anchor="w")
        self.valor.pack(fill="x")
        self.detalle = tk.Label(self, text="", bg=tema.TARJETA, fg=tema.MUTED, font=tema.fuente(9),
                                anchor="w")
        self.detalle.pack(fill="x")

    def fijar(self, valor, detalle=""):
        self.valor.config(text=valor)
        self.detalle.config(text=detalle)
