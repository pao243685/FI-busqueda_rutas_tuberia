import heapq
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .config import COSTO_CODO_M, COSTO_CRUCE_MURO_M, ESCALA_PX_M
from .modelo import Modelo

SIN_DIRECCION = -1


@dataclass
class Resultado:
    explorados: List[Tuple] = field(default_factory=list)
    ruta: Optional[List[Tuple[int, int]]] = None
    costo: Optional[float] = None
    metros: float = 0.0
    codos: List[int] = field(default_factory=list)
    expandidos: int = 0


def a_estrella(modelo: Modelo, inicio, meta, costo_codo=COSTO_CODO_M) -> Resultado:
    def h(i, j):
        return (abs(i - meta[0]) * modelo.px + abs(j - meta[1]) * modelo.py) / ESCALA_PX_M

    estado_inicial = (inicio[0], inicio[1], SIN_DIRECCION)
    g, padre = {estado_inicial: 0.0}, {estado_inicial: None}
    frontera = [(h(*inicio), h(*inicio), 0, estado_inicial)]
    estados_cerrados, nodos_vistos = set(), set()
    explorados = []
    orden_insercion = 1
    while frontera:
        _, _, _, estado_actual = heapq.heappop(frontera)
        if estado_actual in estados_cerrados:
            continue
        estados_cerrados.add(estado_actual)
        i, j, dir_llegada = estado_actual
        if (i, j) not in nodos_vistos:
            nodos_vistos.add((i, j))
            estado_padre = padre[estado_actual]
            nodo_padre = (estado_padre[0], estado_padre[1]) if estado_padre else None
            explorados.append((nodo_padre, (i, j)))
        if (i, j) == tuple(meta):
            ruta, estado = [], estado_actual
            while estado is not None:
                ruta.append((estado[0], estado[1]))
                estado = padre[estado]
            ruta.reverse()
            return Resultado(explorados=explorados, ruta=ruta, costo=g[estado_actual],
                             metros=longitud_m(modelo, ruta), codos=indices_codos(ruta),
                             expandidos=len(estados_cerrados))
        for i_vecino, j_vecino, accion in modelo.vecinos(i, j):
            estado_vecino = (i_vecino, j_vecino, accion)
            if estado_vecino in estados_cerrados:
                continue
            hay_giro = dir_llegada != SIN_DIRECCION and accion != dir_llegada
            costo_tramo = modelo.costo_arista(i, j, accion)
            g_vecino = g[estado_actual] + costo_tramo + (costo_codo if hay_giro else 0.0)
            if g_vecino < g.get(estado_vecino, float("inf")):
                g[estado_vecino] = g_vecino
                padre[estado_vecino] = estado_actual
                h_vecino = h(i_vecino, j_vecino)
                heapq.heappush(frontera, (g_vecino + h_vecino, h_vecino, orden_insercion, estado_vecino))
                orden_insercion += 1
    return Resultado(explorados=explorados, expandidos=len(estados_cerrados))


def longitud_m(modelo: Modelo, ruta):
    total_m = 0.0
    for origen, destino in zip(ruta, ruta[1:]):
        total_m += (modelo.px if origen[1] == destino[1] else modelo.py) / ESCALA_PX_M
    return total_m


def indices_codos(ruta):
    indices = []
    for pos in range(1, len(ruta) - 1):
        dir_entrada = (ruta[pos][0] - ruta[pos - 1][0], ruta[pos][1] - ruta[pos - 1][1])
        dir_salida = (ruta[pos + 1][0] - ruta[pos][0], ruta[pos + 1][1] - ruta[pos][1])
        if dir_entrada != dir_salida:
            indices.append(pos)
    return indices


def cruces_muro(modelo: Modelo, ruta):
    """Número de muros interiores que cruza la ruta."""
    total = 0.0
    for (i, j), (i_vecino, j_vecino) in zip(ruta, ruta[1:]):
        if j == j_vecino:  # tramo horizontal
            total += modelo.mh[j][min(i, i_vecino)]
        else:  # tramo vertical
            total += modelo.mv[min(j, j_vecino)][i]
    return round(total / COSTO_CRUCE_MURO_M)