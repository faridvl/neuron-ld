"""facturar(): F5 Imprimir Documento. Terminó cuando aparece la primera ventana nueva (selección de plan, pago, mensaje...)
o, si no sale ninguna, cuando el total vuelve a 0. Devuelve el título de lo que apareció."""
from .. import base

NOMBRE = "facturar"
PANTALLA = "Principal: barra F5 'Imprimir Documento'"


def ejecutar(pos):
    pos.pulsar_barra("imprimir documento")

    def algo():
        nuevas = base.modales(pos.pid)
        if nuevas:
            return ("ventana", base.titulo(nuevas[0]))
        if pos.total() == 0:
            return ("limpio", "")
        return None

    resultado = base.esperar(algo, 20)
    if not resultado:
        raise base.PasoFallido("F5 no abrió ninguna ventana ni limpió el documento")
    return {"aparecio": resultado[1] or resultado[0]}
