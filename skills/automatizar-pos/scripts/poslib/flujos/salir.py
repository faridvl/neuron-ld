"""salir(): ESC Salir del POS y confirma. Terminó cuando el proceso ya no tiene ventanas."""
from .. import base

NOMBRE = "salir"
PANTALLA = "Principal: barra ESC 'Salir'; pregunta Sí/No"


def ejecutar(pos):
    pos.pulsar_barra("salir")
    pregunta = base.esperar(lambda: base.modales(pos.pid) or None, 10)
    if pregunta:
        base.clic_sin_texto(pregunta[0], 0)
    if not base.esperar(lambda: not base.ventanas(pos.pid), 15):
        raise base.PasoFallido("El POS no se cerró")
    return {}
