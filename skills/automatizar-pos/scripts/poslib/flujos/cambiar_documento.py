"""cambiar_documento(tipo, subtipo=None, esperado=None): Documento -> Tipos de Documentos -> botón del tipo -> subtipo -> Aceptar.
tipo: 'contado' | 'credito' (o el comienzo del texto del botón, p. ej. 'APARTADO').
Terminó cuando el campo Documento contiene `esperado` (por defecto, el tipo)."""
from pywinauto.controls.common_controls import ListViewWrapper

from .. import base

NOMBRE = "cambiar_documento"
PANTALLA = "Tipos de Documentos (modal); abre Bn_Documento"
BOTON_POR_TIPO = {"contado": "VENTA DE CONT", "credito": "FACTURA DE CR"}
TEXTO_ESPERADO = {"contado": "contado", "credito": "dito"}


def _lista_con_filas(dialogo):
    for h in base.descendientes(dialogo):
        if "SysListView32" in base.clase(h):
            vista = ListViewWrapper(h)
            if vista.item_count() > 0:
                return vista
    return None


def ejecutar(pos, tipo="credito", subtipo=None, esperado=None):
    esperado = (esperado or TEXTO_ESPERADO.get(tipo, tipo)).lower()
    actual = pos.texto("lbl_Documento").lower()
    if esperado in actual and (not subtipo or subtipo.lower() in actual):
        return {"ya_estaba": True}
    pos.invocar("Bn_Documento")
    dialogo = base.esperar_ventana(pos.pid, "Tipos de Documentos")
    if not dialogo:
        raise base.PasoFallido("No abrió 'Tipos de Documentos'")
    base.clic_boton(dialogo, BOTON_POR_TIPO.get(tipo, tipo))

    vista = base.esperar(lambda: _lista_con_filas(dialogo), 10)
    if vista is not None:
        textos = [vista.get_item(i).text() for i in range(vista.item_count())]
        if subtipo:
            fila = next((i for i, t in enumerate(textos) if subtipo.lower() in t.lower()), None)
        else:
            fila = 0
        if fila is None:
            raise base.PasoFallido("No hay subtipo %r entre %s" % (subtipo, textos))
        vista.select(fila)
        base.clic_boton(dialogo, "Aceptar")
    if not base.esperar(lambda: esperado in pos.texto("lbl_Documento").lower(), 15):
        raise base.PasoFallido("Documento no dice %r (dice %r)" % (esperado, pos.texto("lbl_Documento")))
    return {"documento": pos.texto("lbl_Documento")}
