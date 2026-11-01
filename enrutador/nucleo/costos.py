from dataclasses import dataclass

from .busqueda import Resultado


@dataclass(frozen=True)
class Presupuesto:
    metros: float
    codos: int
    tubo: float
    accesorios: float

    @property
    def total(self):
        return self.tubo + self.accesorios


def validar_precios(precio_metro, precio_codo):
    if precio_metro <= 0:
        raise ValueError("El precio por metro de tubería debe ser mayor que 0.")
    if precio_codo <= precio_metro:
        raise ValueError("El precio del codo debe ser mayor al precio del metro de tubería.")


def costo_codo_equivalente(precio_metro, precio_codo):
    """Penalización por codo para A*, en metros de tubería: precio_codo / precio_metro."""
    validar_precios(precio_metro, precio_codo)
    return precio_codo / precio_metro


def estimar(resultado: Resultado, precio_metro, precio_codo) -> Presupuesto:
    n = len(resultado.codos)
    return Presupuesto(metros=resultado.metros, codos=n,
                       tubo=resultado.metros * precio_metro,
                       accesorios=n * precio_codo)