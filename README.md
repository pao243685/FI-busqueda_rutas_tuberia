# Enrutador de tuberías con A*

Proyecto U2 de Fundamentos de Inteligencia Artificial (algoritmos de búsqueda).

## Estructura

```
main.py                      punto de entrada
requirements.txt
enrutador/
  cli.py                     argumentos y modo sin ventana
  recursos.py                búsqueda del archivo del plano
  nucleo/                    lógica pura, sin PIL ni tkinter
    config.py                constantes y parámetros
    geometria.py             muros, alberca, riesgos, zonas prohibidas, zonas de costo, desagües y meta
    modelo.py                retícula de nodos y aristas
    busqueda.py              A* y métricas de la ruta
    costos.py                presupuesto aproximado (metros y codos)
  render/                    capas con PIL (usables sin ventana)
    capas.py
    exportar.py
  ui/                        interfaz tkinter
    tema.py                  colores y fuentes
    vista.py                 transformación del plano a pantalla (rotado)
    widgets.py               botones, interruptores, selector, deslizador, tarjetas
    app.py                   ventana principal y animación
```

La regla es que `nucleo` no importa nada de `render` ni de `ui`. `render` solo depende de `nucleo`, y `ui` depende de las dos.

## Uso

```
pip install -r requirements.txt
python main.py
python main.py ruta/plano.jpg
python main.py --test
python main.py --png salida.png --desague 3
```

Si no pasas ruta, busca `plano.jpg` junto a `main.py`, en `assets/` o en la carpeta actual.

## Notas

- La interfaz muestra el plano girado 90 grados (acostado) y la calle queda a la derecha. La lógica sigue trabajando con las coordenadas originales del plano.
- `--desague N` reemplaza al número suelto que se pasaba después de `--png`.
- El costo aproximado es metros de tubería por precio por metro, más codos por precio por codo. Los precios por defecto están en `nucleo/config.py` (`PRECIO_METRO_MXN`, `PRECIO_CODO_MXN`) y se pueden cambiar desde el panel. Son valores de referencia, ajústalos a tu cotización real.
- Los metros salen de la escala del plano (`ESCALA_PX_M`), así que son aproximados.
- Pantalla completa con F11 o con el botón del panel, y se sale con Esc.
- `ZONAS_BLOQUEADAS` son celdas prohibidas (closets, isla y barra, escalera, autos). Se tratan igual que un muro.
- `ZONAS_COSTO` no bloquean, multiplican el costo por metro de las aristas que tocan (recámaras x4, sala, comedor y estudio x3, jardines x4, muebles grandes x8, gabinetes de cocina x6). Los factores son siempre mayores o iguales a 1, así que la heurística de Manhattan sigue siendo admisible y A* sigue dando la ruta óptima según esos costos.
- Los márgenes de 1.0 m a la cimentación perimetral (x2) y de 0.5 m a las zonas eléctricas (x3) también son zonas de costo. Se pueden cruzar, por ejemplo con camisa de protección. Se ajustan en `nucleo/config.py`.
- Las puertas no se bloquean. Los vanos siguen siendo los puntos de paso entre cuartos.
- `metros` y el costo aproximado en pesos miden tubería real. Las penalizaciones solo cambian qué ruta elige A*, no cuánto cuesta el material.
