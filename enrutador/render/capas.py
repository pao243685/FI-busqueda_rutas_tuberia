from PIL import Image, ImageDraw

from ..nucleo.geometria import ALBERCA, MUROS, RIESGOS, ZONAS_BLOQUEADAS, ZONAS_COSTO


def capa_obstaculos(k, w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    esc = lambda r: [r[0] * k, r[1] * k, r[2] * k, r[3] * k]
    for _, r, _ in ZONAS_COSTO:
        d.rectangle(esc(r), fill=(0, 150, 136, 55))
    for r in ALBERCA:
        d.rectangle(esc(r), fill=(140, 60, 200, 95))
    for _, r in ZONAS_BLOQUEADAS:
        d.rectangle(esc(r), fill=(233, 30, 99, 150))
    for r in MUROS:
        d.rectangle(esc(r), fill=(215, 30, 30, 175))
    for _, r in RIESGOS:
        d.rectangle(esc(r), fill=(255, 140, 0, 150))
    return im


def capa_malla(m, k, w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    alc = m.alcanzables
    for j in range(m.ny + 1):
        for i in range(m.nx):
            if m.h[j][i] and (i, j) in alc:
                d.line([m.xs[i] * k, m.ys[j] * k, m.xs[i + 1] * k, m.ys[j] * k], fill=(0, 170, 80, 110), width=1)
    for j in range(m.ny):
        for i in range(m.nx + 1):
            if m.v[j][i] and (i, j) in alc:
                d.line([m.xs[i] * k, m.ys[j] * k, m.xs[i] * k, m.ys[j + 1] * k], fill=(0, 170, 80, 110), width=1)
    for (i, j) in alc:
        x, y = m.xs[i] * k, m.ys[j] * k
        d.ellipse([x - 1.6, y - 1.6, x + 1.6, y + 1.6], fill=(0, 140, 60, 190))
    return im
