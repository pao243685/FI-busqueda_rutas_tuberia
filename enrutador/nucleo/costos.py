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


def estimar(resultado: Resultado, precio_metro, precio_codo) -> Presupuesto:
    n = len(resultado.codos)
    return Presupuesto(metros=resultado.metros, codos=n,
                       tubo=resultado.metros * precio_metro,
                       accesorios=n * precio_codo)
