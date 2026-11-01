import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOMBRES = ("plano.jpg", "plano.png", "plano.jpeg")


def encontrar_imagen():
    for nombre in NOMBRES:
        ruta = os.path.join(RAIZ, nombre)
        if os.path.exists(ruta):
            return ruta
    raise FileNotFoundError("No encontré plano.jpg: ponlo en la raíz del proyecto, junto a main.py.")
