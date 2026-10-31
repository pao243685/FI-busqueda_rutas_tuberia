import heapq
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .config import COSTO_CODO_M, ESCALA_PX_M
from .modelo import Modelo


@dataclass
class Resultado:
    explorados: List[Tuple] = field(default_factory=list)
    ruta: Optional[List[Tuple[int, int]]] = None
    costo: Optional[float] = None
    metros: float = 0.0
    codos: List[int] = field(default_factory=list)
    expandidos: int = 0


def a_estrella(m: Modelo, inicio, meta, costo_codo=COSTO_CODO_M) -> Resultado:
    def h(i, j):
        return (abs(i - meta[0]) * m.px + abs(j - meta[1]) * m.py) / ESCALA_PX_M

    ini = (inicio[0], inicio[1], -1)
    g, padre = {ini: 0.0}, {ini: None}
    abierta = [(h(*inicio), h(*inicio), 0, ini)]
    cerrados, vistos = set(), set()
    explorados = []
    cont = 1
    while abierta:
        _, _, _, act = heapq.heappop(abierta)
        if act in cerrados:
            continue
        cerrados.add(act)
        i, j, d0 = act
        if (i, j) not in vistos:
            vistos.add((i, j))
            p = padre[act]
            explorados.append(((p[0], p[1]) if p else None, (i, j)))
        if (i, j) == tuple(meta):
            ruta, e = [], act
            while e is not None:
                ruta.append((e[0], e[1]))
                e = padre[e]
            ruta.reverse()
            return Resultado(explorados=explorados, ruta=ruta, costo=g[act],
                             metros=longitud_m(m, ruta), codos=indices_codos(ruta),
                             expandidos=len(cerrados))
        for ni, nj, a in m.vecinos(i, j):
            nuevo = (ni, nj, a)
            if nuevo in cerrados:
                continue
            ng = g[act] + m.costo_arista(i, j, a) + (costo_codo if d0 != -1 and a != d0 else 0.0)
            if ng < g.get(nuevo, float("inf")):
                g[nuevo] = ng
                padre[nuevo] = act
                hh = h(ni, nj)
                heapq.heappush(abierta, (ng + hh, hh, cont, nuevo))
                cont += 1
    return Resultado(explorados=explorados, expandidos=len(cerrados))


def longitud_m(m: Modelo, ruta):
    t = 0.0
    for a, b in zip(ruta, ruta[1:]):
        t += (m.px if a[1] == b[1] else m.py) / ESCALA_PX_M
    return t


def indices_codos(ruta):
    r = []
    for k in range(1, len(ruta) - 1):
        d1 = (ruta[k][0] - ruta[k - 1][0], ruta[k][1] - ruta[k - 1][1])
        d2 = (ruta[k + 1][0] - ruta[k][0], ruta[k + 1][1] - ruta[k][1])
        if d1 != d2:
            r.append(k)
    return r
