from PIL import Image

from ..nucleo.config import REF_H, REF_W


class Vista:
    def __init__(self, k, franja_px):
        self.k = k
        self.w = int(REF_W * k)
        self.h = int(REF_H * k)
        self.franja = int(franja_px * k)
        self.ancho = self.h + self.franja
        self.alto = self.w

    def punto(self, x, y):
        return y * self.k, self.w - x * self.k

    def nodo(self, modelo, nodo):
        x, y = modelo.pos(nodo)
        return self.punto(x, y)

    @staticmethod
    def girar(imagen):
        return imagen.transpose(Image.Transpose.ROTATE_90)
