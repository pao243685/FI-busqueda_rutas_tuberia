import argparse
import sys

from .nucleo.busqueda import a_estrella
from .nucleo.config import ESCALA_PX_M, PRECIO_CODO_MXN, PRECIO_METRO_MXN
from .nucleo.costos import estimar
from .nucleo.modelo import Modelo
from .recursos import encontrar_imagen


def pruebas():
    m = Modelo()
    print(f"Retícula: {m.nx + 1} x {m.ny + 1} nodos  |  paso = {m.px / ESCALA_PX_M:.2f} m  |  "
          f"nodos transitables: {len(m.alcanzables)}  |  meta en nodo {m.meta}")
    for nom, nodo in m.desagues:
        res = a_estrella(m, nodo, m.meta)
        if res.ruta:
            pres = estimar(res, PRECIO_METRO_MXN, PRECIO_CODO_MXN)
            print(f"{nom:28s} {res.metros:6.1f} m   {len(res.codos):2d} codos   "
                  f"costo A* {res.costo:6.2f}   aprox ${pres.total:8,.0f} MXN   "
                  f"explorados {len(res.explorados)}")
        else:
            print(f"{nom:28s} SIN RUTA")


def construir_parser():
    p = argparse.ArgumentParser(description="Enrutador de tuberías con A*")
    p.add_argument("imagen", nargs="?", help="ruta del plano (por defecto plano.jpg)")
    p.add_argument("--test", action="store_true", help="corre A* desde todos los desagües sin abrir ventana")
    p.add_argument("--png", metavar="SALIDA", help="exporta un PNG sin abrir ventana")
    p.add_argument("--desague", type=int, metavar="N", help="índice del desagüe para dibujar su ruta en el PNG")
    return p


def main(argv=None):
    args = construir_parser().parse_args(argv)
    if args.test:
        return pruebas()
    try:
        ruta = encontrar_imagen(args.imagen)
    except FileNotFoundError as e:
        sys.exit(str(e))
    try:
        if args.png:
            from .render.exportar import exportar_png
            return exportar_png(ruta, args.png, args.desague)
        from .ui.app import lanzar
    except ImportError:
        sys.exit("Falta tkinter o Pillow. Instala con:  pip install pillow")
    lanzar(ruta)
