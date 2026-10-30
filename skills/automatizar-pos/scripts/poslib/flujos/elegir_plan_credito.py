"""elegir_plan_credito(plan=None): 'Seleccionar Tipo De Crédito' -> (fila del plan si se indica) -> Continuar -> 'Simulador De Cuotas' -> Confirmar (F1).
Terminó cuando el simulador se cerró. El plazo lo define el plan; esta pantalla no lo pide."""
from .. import base

NOMBRE = "elegir_plan_credito"
PANTALLA = "Seleccionar Tipo De Crédito (Dgv_TiposCredito) y Simulador De Cuotas"


def _seleccionar_fila(ventana, plan):
    from pywinauto.controls.uiawrapper import UIAWrapper
    from pywinauto.uia_element_info import UIAElementInfo
    descendientes_uia = UIAWrapper(UIAElementInfo(ventana)).descendants()
    filas = {}
    for c in descendientes_uia:
        n = c.window_text() or ""
        if n.startswith("Descripci") and " Row " in n:
            filas[int(n.rsplit(" ", 1)[1])] = c
    for i in sorted(filas):
        if plan.upper() in str(filas[i].get_value()).upper():
            for c in descendientes_uia:
                if (c.window_text() or "") == "Row %d" % i:
                    c.select()
                    return i
    raise base.PasoFallido("No hay un plan que contenga %r" % plan)


def ejecutar(pos, plan=None):
    ventana = base.esperar_ventana(pos.pid, "Seleccionar Tipo", 20)
    if not ventana:
        raise base.PasoFallido("No salió 'Seleccionar Tipo De Crédito'")
    if plan:
        _seleccionar_fila(ventana, plan)
    base.clic_boton(ventana, "Continuar")
    simulador = base.esperar_ventana(pos.pid, "Simulador", 15)
    if not simulador:
        raise base.PasoFallido("No salió 'Simulador De Cuotas'")
    base.clic_boton(simulador, "Confirmar")
    if not base.esperar_cierre(simulador, 15):
        raise base.PasoFallido("El simulador no se cerró")
    return {"plan": plan}
