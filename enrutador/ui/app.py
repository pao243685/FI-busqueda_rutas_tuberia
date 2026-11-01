import tkinter as tk

from PIL import Image, ImageTk

from ..nucleo.busqueda import a_estrella
from ..nucleo.config import COSTO_CODO_M, PRECIO_CODO_MXN, PRECIO_METRO_MXN, REF_H, REF_W
from ..nucleo.costos import estimar
from ..nucleo.modelo import Modelo
from ..render.capas import capa_malla, capa_obstaculos
from . import tema
from .vista import Vista
from .widgets import Boton, Deslizador, Interruptor, Selector, Tarjeta

MSG_INICIAL = "Elige el punto de desagüe para colocar el drenaje"
TXT_PANTALLA = "Pantalla completa"
TXT_SALIR = "Salir de pantalla completa"


def dinero(x):
    return f"${x:,.0f}"


class App:
    FRANJA = 46
    ANCHO_PANEL = 340
    BARRA = 120
    PAD = 20

    def __init__(self, root, ruta_imagen):
        self.root = root
        self.ruta_imagen = ruta_imagen
        root.title("Enrutador de tuberías - A*")
        root.configure(bg=tema.FONDO)
        self.m = Modelo()
        self.completa = False
        self.vista = Vista(self.calcular_escala(), self.FRANJA)
        self.cargar_imagenes()
        self.construir_panel()
        self.construir_lienzo()
        root.bind("<F11>", self.alternar_pantalla)
        root.bind("<Escape>", self.salir_pantalla)
        self.animando = False
        self.mostrando = False
        self._job = None
        self.res = None
        self.sel = None
        self.dibujar_base()

    def calcular_escala(self):
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        mx, my, tope = (40, 40, 1.5) if self.completa else (60, 130, 1.0)
        return min(tope,
                   (sw - self.ANCHO_PANEL - mx) / (REF_H + self.FRANJA),
                   (sh - my - self.BARRA) / REF_W)

    def cargar_imagenes(self):
        v = self.vista
        base = Image.open(self.ruta_imagen).convert("RGB").resize((v.w, v.h), Image.Resampling.LANCZOS)
        tenue = Image.blend(base, Image.new("RGB", base.size, "white"), 0.55)
        self.img_normal = ImageTk.PhotoImage(v.girar(base))
        self.img_tenue = ImageTk.PhotoImage(v.girar(tenue))
        self.img_obst = ImageTk.PhotoImage(v.girar(capa_obstaculos(v.k, v.w, v.h)))
        self.img_malla = ImageTk.PhotoImage(v.girar(capa_malla(self.m, v.k, v.w, v.h)))

    def seccion(self, padre, texto):
        tk.Label(padre, text=texto.upper(), font=tema.fuente(8, True), bg=tema.PANEL, fg=tema.MUTED,
                 anchor="w").pack(fill="x", padx=self.PAD, pady=(16, 6))

    def fila(self, padre, texto):
        f = tk.Frame(padre, bg=tema.PANEL)
        f.pack(fill="x", padx=self.PAD, pady=2)
        tk.Label(f, text=texto, font=tema.fuente(10), bg=tema.PANEL, fg=tema.TEXTO).pack(side="left")
        return f

    def construir_panel(self):
        p = tk.Frame(self.root, bg=tema.PANEL, width=self.ANCHO_PANEL)
        p.pack(side="left", fill="y")
        p.pack_propagate(False)
        ancho_interno = self.ANCHO_PANEL - 2 * self.PAD

        tk.Label(p, text="Enrutador de tuberías", font=tema.fuente(17, True), bg=tema.PANEL,
                 fg=tema.TEXTO, anchor="w").pack(fill="x", padx=self.PAD, pady=(20, 0))
        tk.Label(p, text="Por búsqueda A* ", font=tema.fuente(9), bg=tema.PANEL,
                 fg=tema.MUTED, anchor="w").pack(fill="x", padx=self.PAD)

        self.lbl_msg = tk.Label(p, text=MSG_INICIAL, font=tema.fuente(10), bg=tema.TARJETA, fg=tema.TEXTO,
                                wraplength=ancho_interno - 24, justify="left", anchor="w",
                                padx=12, pady=10, height=3)
        self.lbl_msg.pack(fill="x", padx=self.PAD, pady=(14, 12))

        self.btn_iniciar = Boton(p, "Iniciar búsqueda", self.iniciar, ancho=ancho_interno, alto=44,
                                 estilo="primario")
        self.btn_iniciar.pack(padx=self.PAD, pady=(0, 8))
        Boton(p, "Limpiar ruta", self.limpiar_ruta, ancho=ancho_interno, alto=38,
              estilo="secundario").pack(padx=self.PAD, pady=(0, 8))
        self.btn_pantalla = Boton(p, TXT_PANTALLA, self.alternar_pantalla, ancho=ancho_interno, alto=38,
                                  estilo="secundario")
        self.btn_pantalla.pack(padx=self.PAD)

        self.seccion(p, "Búsqueda")
        self.costo_codo = tk.DoubleVar(value=COSTO_CODO_M)
        self.velocidad = tk.IntVar(value=10)
        Selector(self.fila(p, "Costo por codo"), self.costo_codo, 0.0, 5.0, 0.1,
                 formato="{:.1f} m").pack(side="right")
        Deslizador(self.fila(p, "Velocidad"), self.velocidad, 1, 60, ancho=150).pack(side="right")

        self.seccion(p, "Precios (MXN)")
        self.precio_m = tk.DoubleVar(value=PRECIO_METRO_MXN)
        self.precio_codo = tk.DoubleVar(value=PRECIO_CODO_MXN)
        Selector(self.fila(p, "Tubería por metro"), self.precio_m, 0, 5000, 5, formato="${:,.0f}",
                 decimales=0, comando=self.actualizar_resultado).pack(side="right")
        Selector(self.fila(p, "Codo de 90°"), self.precio_codo, 0, 5000, 5, formato="${:,.0f}",
                 decimales=0, comando=self.actualizar_resultado).pack(side="right")

        self.seccion(p, "Capas")
        self.ver_obst = tk.BooleanVar(value=True)
        self.ver_malla = tk.BooleanVar(value=False)
        Interruptor(p, "Muros y riesgos", self.ver_obst, self.aplicar_capas).pack(
            fill="x", padx=self.PAD, pady=3)
        Interruptor(p, "Rejilla transitable", self.ver_malla, self.aplicar_capas).pack(
            fill="x", padx=self.PAD, pady=3)

        self.seccion(p, "Leyenda")
        cuadro = tk.Frame(p, bg=tema.PANEL)
        cuadro.pack(fill="x", padx=self.PAD)
        for n, (texto, color) in enumerate(tema.LEYENDA):
            f = tk.Frame(cuadro, bg=tema.PANEL)
            f.grid(row=n // 3, column=n % 3, sticky="w", padx=(0, 14), pady=2)
            tk.Frame(f, bg=color, width=12, height=12).pack(side="left")
            tk.Label(f, text=texto, bg=tema.PANEL, fg=tema.TEXTO, font=tema.fuente(9)).pack(
                side="left", padx=(6, 0))

    def construir_lienzo(self):
        v = self.vista
        zona = tk.Frame(self.root, bg=tema.FONDO)
        zona.pack(side="left", fill="both", expand=True, padx=16, pady=16)
        centro = tk.Frame(zona, bg=tema.FONDO)
        centro.pack(expand=True)
        self.canvas = tk.Canvas(centro, width=v.ancho, height=v.alto, highlightthickness=0, bg=tema.CALLE)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.clic)
        self.canvas.bind("<Motion>", self.hover)
        self.construir_barra(centro)

    def construir_barra(self, padre):
        barra = tk.Frame(padre, bg=tema.FONDO)
        barra.pack(fill="x", pady=(12, 0))
        for col, peso in enumerate((3, 2, 2, 3)):
            barra.columnconfigure(col, weight=peso, uniform="b")
        self.t_total = Tarjeta(barra, "COSTO APROXIMADO", tam=26, acento=True)
        self.t_metros = Tarjeta(barra, "TUBERÍA")
        self.t_codos = Tarjeta(barra, "CODOS DE 90°")
        self.t_origen = Tarjeta(barra, "DESDE", tam=13)
        for col, t in enumerate((self.t_total, self.t_metros, self.t_codos, self.t_origen)):
            t.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 6, 0))
        self.reiniciar_resultado()

    def reiniciar_resultado(self):
        self.t_total.fijar("-", "Elige inicio y meta para iniciar la búsqueda")
        self.t_metros.fijar("-")
        self.t_codos.fijar("-")
        self.t_origen.fijar("-")

    def actualizar_resultado(self):
        if not self.mostrando:
            return
        r = self.res
        pm, pc = self.precio_m.get(), self.precio_codo.get()
        pres = estimar(r, pm, pc)
        self.t_total.fijar(dinero(pres.total), "MXN  ·  tubería + codos")
        self.t_metros.fijar(f"{pres.metros:.1f} m", f"{dinero(pres.tubo)}  a {dinero(pm)} por metro")
        self.t_codos.fijar(str(pres.codos), f"{dinero(pres.accesorios)}  a {dinero(pc)} c/u")
        self.t_origen.fijar(self.m.desagues[self.sel][0], f"{len(r.explorados)} nodos explorados")

    def alternar_pantalla(self, _=None):
        self.completa = not self.completa
        self.root.attributes("-fullscreen", self.completa)
        if not self.completa:
            self.root.geometry("")
        self.btn_pantalla.set_texto(TXT_SALIR if self.completa else TXT_PANTALLA)
        self.aplicar_escala()

    def salir_pantalla(self, _=None):
        if self.completa:
            self.alternar_pantalla()

    def aplicar_escala(self):
        if self.animando:
            self.limpiar_ruta()
        self.vista = Vista(self.calcular_escala(), self.FRANJA)
        self.cargar_imagenes()
        self.canvas.config(width=self.vista.ancho, height=self.vista.alto)
        self.dibujar_base()
        if self.mostrando:
            self.redibujar_resultado()

    def pt(self, nodo):
        return self.vista.nodo(self.m, nodo)

    def dibujar_base(self):
        c, v = self.canvas, self.vista
        c.delete("all")
        self.bg = c.create_image(0, 0, image=self.img_normal, anchor="nw")
        self.it_malla = c.create_image(0, 0, image=self.img_malla, anchor="nw")
        self.it_obst = c.create_image(0, 0, image=self.img_obst, anchor="nw")
        c.create_rectangle(v.h, 0, v.ancho, v.alto, fill=tema.CALLE, outline="")
        c.create_text(v.h + v.franja / 2, v.alto / 2, text="CALLE  ·  RED DE DRENAJE MUNICIPAL",
                      angle=90, fill="white", font=tema.fuente(9, True))
        mx, my = self.pt(self.m.meta)
        c.create_line(mx, my, v.h, my, fill="#2e7d32", width=3, dash=(5, 3))
        self.aplicar_capas()
        self.dibujar_marcas()

    def aplicar_capas(self):
        self.canvas.itemconfigure(self.it_obst, state="normal" if self.ver_obst.get() else "hidden")
        self.canvas.itemconfigure(self.it_malla, state="normal" if self.ver_malla.get() else "hidden")

    def dibujar_marcas(self):
        c = self.canvas
        c.delete("marcas")
        r = max(6, int(self.vista.k * 15))
        mx, my = self.pt(self.m.meta)
        c.create_oval(mx - r, my - r, mx + r, my + r, fill="#2e7d32", outline="white", width=2, tags="marcas")
        c.create_text(mx, my, text="R", fill="white", font=tema.fuente(max(7, r - 1), True), tags="marcas")
        c.create_text(mx - r - 4, my - 2, text="Registro (meta)", anchor="e", fill="#1b5e20",
                      font=tema.fuente(8, True), tags="marcas")
        for idx, (nom, nodo) in enumerate(self.m.desagues):
            x, y = self.pt(nodo)
            col = "#00c853" if idx == self.sel else "#1976d2"
            c.create_polygon(x - r * 0.75, y - r * 0.3, x + r * 0.75, y - r * 0.3, x, y - r * 1.9,
                             fill=col, outline="white", tags="marcas")
            c.create_oval(x - r * 0.9, y - r * 0.9, x + r * 0.9, y + r * 0.9, fill=col,
                          outline="white", width=2, tags="marcas")
            c.create_oval(x - r * 0.3, y - r * 0.3, x + r * 0.3, y + r * 0.3, fill="white", outline="",
                          tags="marcas")
        c.tag_raise("marcas")

    def cercano(self, ev, radio=None):
        radio = radio or max(12, int(self.vista.k * 26))
        mejor, dmin = None, radio ** 2
        for idx, (_, nodo) in enumerate(self.m.desagues):
            x, y = self.pt(nodo)
            d = (x - ev.x) ** 2 + (y - ev.y) ** 2
            if d <= dmin:
                mejor, dmin = idx, d
        return mejor

    def hover(self, ev):
        if self.animando or self.sel is not None:
            return
        idx = self.cercano(ev)
        self.canvas.config(cursor="hand2" if idx is not None else "")
        self.lbl_msg.config(text=("Desagüe: " + self.m.desagues[idx][0] + " ")
                            if idx is not None else MSG_INICIAL)

    def clic(self, ev):
        if self.animando:
            return
        idx = self.cercano(ev)
        if idx is None:
            self.lbl_msg.config(text="Solo puedes elegir un área de desagüe (gotas azules). " + MSG_INICIAL)
            return
        self.limpiar_ruta()
        self.sel = idx
        self.dibujar_marcas()
        self.lbl_msg.config(text=f"Inicio: {self.m.desagues[idx][0]}  \nmeta: registro de la calle. "
                            )

    def limpiar_ruta(self):
        self.cancelar()
        self.mostrando = False
        self.canvas.delete("expl", "tubo")
        self.canvas.itemconfig(self.bg, image=self.img_normal)
        self.reiniciar_resultado()

    def cancelar(self):
        self.animando = False
        self.btn_iniciar.set_activo(True)
        if self._job:
            self.root.after_cancel(self._job)
            self._job = None

    def iniciar(self):
        if self.animando:
            return
        if self.sel is None:
            self.lbl_msg.config(text=MSG_INICIAL)
            return
        self.limpiar_ruta()
        try:
            codo = float(self.costo_codo.get())
        except (ValueError, tk.TclError):
            codo = COSTO_CODO_M
        self.res = a_estrella(self.m, self.m.desagues[self.sel][1], self.m.meta, codo)
        self.animando = True
        self.btn_iniciar.set_activo(False)
        self.canvas.itemconfig(self.bg, image=self.img_tenue)
        self.lbl_msg.config(text="Explorando el plano con A*…")
        self.animar_exploracion(0)

    def animar_exploracion(self, i):
        if not self.animando:
            return
        ev = self.res.explorados
        for _ in range(max(1, int(self.velocidad.get()))):
            if i >= len(ev):
                break
            padre, nodo = ev[i]
            x, y = self.pt(nodo)
            if padre:
                px, py = self.pt(padre)
                self.canvas.create_line(px, py, x, y, fill="#ffb300", width=2, tags="expl")
            self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="#ff8f00", outline="", tags="expl")
            i += 1
        self.canvas.tag_raise("marcas")
        if i < len(ev):
            self._job = self.root.after(25, self.animar_exploracion, i)
        else:
            self._job = self.root.after(350, self.preparar_tubo)

    def calcular_tubo(self):
        self.pts = [self.pt(n) for n in self.res.ruta]
        self.segs = [abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in zip(self.pts, self.pts[1:])]
        self.acum = [0.0]
        for s in self.segs:
            self.acum.append(self.acum[-1] + s)
        self.grosor = max(5, int(self.vista.k * 20))

    def preparar_tubo(self):
        if not self.animando:
            return
        if not self.res.ruta:
            self.cancelar()
            self.lbl_msg.config(text="No existe ruta posible desde ese desagüe.")
            return
        self.calcular_tubo()
        self.lbl_msg.config(text="Instalando la tubería…")
        self.canvas.itemconfigure("expl", fill="#ffe082")
        self.animar_tubo(0.0)

    def dibujar_tubo(self, L, cabeza=True):
        pts = []
        for idx, p in enumerate(self.pts):
            if self.acum[idx] <= L:
                pts.append(p)
            else:
                a, b = self.pts[idx - 1], p
                f = (L - self.acum[idx - 1]) / self.segs[idx - 1]
                pts.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
                break
        c = self.canvas
        c.delete("tubo")
        if len(pts) >= 2:
            flat = [v for p in pts for v in p]
            g = self.grosor
            c.create_line(*flat, fill="#0b2a4a", width=g + 4, capstyle="round", joinstyle="round", tags="tubo")
            c.create_line(*flat, fill="#29b6f6", width=g, capstyle="round", joinstyle="round", tags="tubo")
            c.create_line(*flat, fill="#b3e5fc", width=max(2, g // 4), capstyle="round", joinstyle="round",
                          tags="tubo")
            for k in self.res.codos:
                if self.acum[k] <= L:
                    x, y = self.pts[k]
                    rr = g * 0.85
                    c.create_oval(x - rr, y - rr, x + rr, y + rr, fill="#0b2a4a", outline="#eceff1",
                                  width=2, tags="tubo")
                    c.create_oval(x - rr * 0.45, y - rr * 0.45, x + rr * 0.45, y + rr * 0.45,
                                  fill="#29b6f6", outline="", tags="tubo")
            if cabeza:
                hx, hy = pts[-1]
                c.create_oval(hx - g * 0.7, hy - g * 0.7, hx + g * 0.7, hy + g * 0.7, fill="#e1f5fe",
                              outline="#0b2a4a", width=2, tags="tubo")
        c.tag_raise("marcas")

    def animar_tubo(self, L):
        if not self.animando:
            return
        total = self.acum[-1]
        if L < total:
            self.dibujar_tubo(L)
            self._job = self.root.after(30, self.animar_tubo, L + 4 + self.velocidad.get() * 0.5)
        else:
            self.terminar()

    def redibujar_resultado(self):
        c = self.canvas
        c.itemconfig(self.bg, image=self.img_tenue)
        for padre, nodo in self.res.explorados:
            x, y = self.pt(nodo)
            if padre:
                px, py = self.pt(padre)
                c.create_line(px, py, x, y, fill="#ffe082", width=2, tags="expl")
            c.create_oval(x - 2, y - 2, x + 2, y + 2, fill="#ffe082", outline="", tags="expl")
        self.calcular_tubo()
        self.dibujar_tubo(self.acum[-1], cabeza=False)

    def terminar(self):
        self.dibujar_tubo(self.acum[-1], cabeza=False)
        self.animando = False
        self.mostrando = True
        self.btn_iniciar.set_activo(True)
        self.lbl_msg.config(text="La ruta fue creada, los círculos oscuros son los codos de 90°.")
        self.actualizar_resultado()


def lanzar(ruta_imagen):
    root = tk.Tk()
    App(root, ruta_imagen)
    root.mainloop()
