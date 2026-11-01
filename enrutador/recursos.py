import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOMBRES = ("plano.jpg", "plano.png", "plano.jpeg")


def encontrar_imagen(ruta=None):
    if ruta:
        if os.path.exists(ruta):
            return ruta
        raise FileNotFoundError(f"No existe el archivo: {ruta}")
    carpetas = (RAIZ, os.path.join(RAIZ, "assets"), os.getcwd(), "/mnt/user-data/uploads")
    for carpeta in carpetas:
        for nombre in NOMBRES:
            p = os.path.join(carpeta, nombre)
            if os.path.exists(p):
                return p
    raise FileNotFoundError("No encontré plano.jpg: ponlo junto a main.py o pasa la ruta como argumento.")
