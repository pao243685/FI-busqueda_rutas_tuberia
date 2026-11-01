import sys

FONDO = "#0b1220"
PANEL = "#111a2e"
TARJETA = "#1b2740"
BORDE = "#2c3b5a"
TEXTO = "#e6edf7"
MUTED = "#8a9bb8"
ACENTO = "#38bdf8"
CALLE = "#455a64"

FAMILIA = "Segoe UI" if sys.platform.startswith("win") else "Helvetica"

BOTONES = {
    "primario": {"normal": "#0ea5e9", "hover": "#38bdf8", "presionado": "#0284c7",
                 "texto": "#04121f", "borde": "#0ea5e9"},
    "secundario": {"normal": TARJETA, "hover": "#26365a", "presionado": "#15203a",
                   "texto": TEXTO, "borde": BORDE},
}
DESACTIVADO = {"normal": "#18233b", "texto": "#5d6c88", "borde": "#18233b"}

LEYENDA = (
    ("Muro", "#d71e1e"),
    ("Riesgo", "#ff8c00"),
    ("Alberca", "#8c3cc8"),
    ("Prohibida", "#e91e63"),
    ("Costo alto", "#009688"),
    ("Explorado", "#ffb300"),
    ("Tubería", "#29b6f6"),
    ("Registro", "#2e7d32"),
)


def fuente(tam, negrita=False):
    return (FAMILIA, tam, "bold") if negrita else (FAMILIA, tam)
