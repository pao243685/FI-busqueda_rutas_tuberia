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