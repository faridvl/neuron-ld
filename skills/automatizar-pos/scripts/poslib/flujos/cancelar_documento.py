"""cancelar_documento(): F9 Cancelar Documento; si pregunta, confirma (botón check, a la izquierda). Terminó cuando el total es 0."""
from .. import base

NOMBRE = "cancelar_documento"
PANTALLA = "Principal: barra 'Cancelar Documento'; en la versión probada no pregunta (si lo hace: 2 botones sin texto)"


def ejecutar(pos):
    if pos.total() == 0:
        return {"ya_estaba": True}
    pos.pulsar_barra("cancelar documento")
    primero = base.esperar(lambda: "limpio" if pos.total() == 0 else (base.modales(pos.pid) or None), 10)
    if primero and primero != "limpio":
        base.clic_sin_texto(primero[0], 0)
        primero = base.esperar(lambda: pos.total() == 0, 10)
    if not primero:
        raise base.PasoFallido("El documento no se canceló")
    return {}
