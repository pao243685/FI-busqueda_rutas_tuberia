from .config import COSTO_CRUCE_MURO_M, ESCALA_PX_M, REF_H, REF_W, SUB
from .geometria import (ALBERCA, DESAGUES, FUERA, META_PX, MUROS_CRUZABLES, MUROS_PERIMETRO, RIESGOS,
                        ZONAS_BLOQUEADAS, ZONAS_COSTO)

N, E, S, O = 0, 1, 2, 3


class Modelo:
    def __init__(self, sub=SUB):
        self.nx, self.ny = 14 * sub, 25 * sub
        self.px, self.py = REF_W / self.nx, REF_H / self.ny
        self.xs = [i * self.px for i in range(self.nx + 1)]
        self.ys = [j * self.py for j in range(self.ny + 1)]
        self.h = [[True] * self.nx for _ in range(self.ny + 1)]
        self.v = [[True] * (self.nx + 1) for _ in range(self.ny)]
        bloqueos = (MUROS_PERIMETRO + ALBERCA + [r for _, r in RIESGOS] + [r for _, r in ZONAS_BLOQUEADAS]
                    + FUERA)
        for rx0, ry0, rx1, ry1 in bloqueos:
            for j in range(self.ny + 1):
                if ry0 < self.ys[j] < ry1:
                    for i in range(self.nx):
                        if max(self.xs[i], rx0) < min(self.xs[i + 1], rx1):
                            self.h[j][i] = False
            for i in range(self.nx + 1):
                if rx0 < self.xs[i] < rx1:
                    for j in range(self.ny):
                        if max(self.ys[j], ry0) < min(self.ys[j + 1], ry1):
                            self.v[j][i] = False
        self.mh = [[0.0] * self.nx for _ in range(self.ny + 1)]
        self.mv = [[0.0] * (self.nx + 1) for _ in range(self.ny)]
        for rect in MUROS_CRUZABLES:
            self.cruce_muro(*rect)
        self.fh = [[1.0] * self.nx for _ in range(self.ny + 1)]
        self.fv = [[1.0] * (self.nx + 1) for _ in range(self.ny)]
        for _, (rx0, ry0, rx1, ry1), f in ZONAS_COSTO:
            for j in range(self.ny + 1):
                if ry0 <= self.ys[j] <= ry1:
                    for i in range(self.nx):
                        if rx0 <= (self.xs[i] + self.xs[i + 1]) / 2 <= rx1 and f > self.fh[j][i]:
                            self.fh[j][i] = f
            for j in range(self.ny):
                if ry0 <= (self.ys[j] + self.ys[j + 1]) / 2 <= ry1:
                    for i in range(self.nx + 1):
                        if rx0 <= self.xs[i] <= rx1 and f > self.fv[j][i]:
                            self.fv[j][i] = f
        self.meta = self.ajustar(*META_PX)
        self.alcanzables = self.alcanzables_desde(self.meta)
        self.desagues = [(nom, self.ajustar(x, y, self.alcanzables)) for nom, x, y in DESAGUES]

    def vecinos(self, i, j):
        if j > 0 and self.v[j - 1][i]:
            yield i, j - 1, N
        if i < self.nx and self.h[j][i]:
            yield i + 1, j, E
        if j < self.ny and self.v[j][i]:
            yield i, j + 1, S
        if i > 0 and self.h[j][i - 1]:
            yield i - 1, j, O

    def cruce_muro(self, rx0, ry0, rx1, ry1):
        horizontal = (rx1 - rx0) >= (ry1 - ry0)
        grosor = (ry1 - ry0) if horizontal else (rx1 - rx0)
        if horizontal:
            for j in range(self.ny + 1):
                if ry0 < self.ys[j] < ry1:
                    for i in range(self.nx):
                        if max(self.xs[i], rx0) < min(self.xs[i + 1], rx1):
                            self.h[j][i] = False
            for i in range(self.nx + 1):
                if rx0 < self.xs[i] < rx1:
                    for j in range(self.ny):
                        solape = min(self.ys[j + 1], ry1) - max(self.ys[j], ry0)
                        if solape > 0:
                            self.mv[j][i] += COSTO_CRUCE_MURO_M * solape / grosor
        else:
            for i in range(self.nx + 1):
                if rx0 < self.xs[i] < rx1:
                    for j in range(self.ny):
                        if max(self.ys[j], ry0) < min(self.ys[j + 1], ry1):
                            self.v[j][i] = False
            for j in range(self.ny + 1):
                if ry0 < self.ys[j] < ry1:
                    for i in range(self.nx):
                        solape = min(self.xs[i + 1], rx1) - max(self.xs[i], rx0)
                        if solape > 0:
                            self.mh[j][i] += COSTO_CRUCE_MURO_M * solape / grosor

    def costo_arista(self, i, j, accion):
        if accion == E:
            largo, f, extra = self.px, self.fh[j][i], self.mh[j][i]
        elif accion == O:
            largo, f, extra = self.px, self.fh[j][i - 1], self.mh[j][i - 1]
        elif accion == N:
            largo, f, extra = self.py, self.fv[j - 1][i], self.mv[j - 1][i]
        else:
            largo, f, extra = self.py, self.fv[j][i], self.mv[j][i]
        return largo / ESCALA_PX_M * f + extra

    def alcanzables_desde(self, origen):
        visto, cola = {origen}, [origen]
        while cola:
            i, j = cola.pop()
            for ni, nj, _ in self.vecinos(i, j):
                if (ni, nj) not in visto:
                    visto.add((ni, nj))
                    cola.append((ni, nj))
        return visto

    def ajustar(self, x, y, permitidos=None):
        mejor, dmin = None, 1e18
        for j in range(self.ny + 1):
            for i in range(self.nx + 1):
                if permitidos is not None and (i, j) not in permitidos:
                    continue
                if permitidos is None and not any(True for _ in self.vecinos(i, j)):
                    continue
                d = (self.xs[i] - x) ** 2 + (self.ys[j] - y) ** 2
                if d < dmin:
                    mejor, dmin = (i, j), d
        return mejor

    def pos(self, nodo):
        return self.xs[nodo[0]], self.ys[nodo[1]]