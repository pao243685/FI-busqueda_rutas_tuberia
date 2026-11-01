from PIL import Image, ImageDraw

from ..nucleo.busqueda import a_estrella
from ..nucleo.config import REF_H, REF_W
from ..nucleo.modelo import Modelo
from .capas import capa_malla, capa_obstaculos


def exportar_png(img_path, salida, idx=None):
    m = Modelo()
    base = Image.open(img_path).convert("RGBA").resize((REF_W, REF_H))
    base = Image.alpha_composite(base, capa_malla(m, 1, REF_W, REF_H))
    base = Image.alpha_composite(base, capa_obstaculos(1, REF_W, REF_H))
    d = ImageDraw.Draw(base)
    for nom, nodo in m.desagues:
        x, y = m.pos(nodo)
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(25, 118, 210, 255), outline="white", width=2)
    x, y = m.pos(m.meta)
    d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(46, 125, 50, 255), outline="white", width=2)
    if idx is not None:
        res = a_estrella(m, m.desagues[idx][1], m.meta)
        if res.ruta:
            d.line([m.pos(n) for n in res.ruta], fill=(13, 71, 161, 255), width=8)
            print(m.desagues[idx][0], f"{res.metros:.1f} m", len(res.codos), "codos")
    base.convert("RGB").save(salida)
