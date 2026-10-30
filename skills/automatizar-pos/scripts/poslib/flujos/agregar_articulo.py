"""agregar_articulo(codigo, cantidad=1): escribe el código, pulsa agregar y fija la cantidad en el diálogo "Modificar Cantidad" si sale.
Terminó cuando la grilla tiene una fila más, o el total cambió, o el campo Artículo quedó vacío otra vez; se sigue de inmediato."""
import time

import win32con
import win32gui

from .. import base

NOMBRE = "agregar_articulo"
PANTALLA = "Principal: Text_Articulo, Btn_Agregar_Articulo; modal 'Modificar Cantidad'"


def ejecutar(pos, codigo, cantidad=1):
    filas_antes, total_antes = pos.filas(), pos.total()
    base.escribir(pos._hwnd["Text_Articulo"], str(codigo))
    pos.invocar("Btn_Agregar_Articulo")

    def listo():
        dialogo = base.por_titulo(pos.pid, "Modificar Cantidad")
        if dialogo:
            return ("dialogo", dialogo)
        if filas_antes >= 0 and pos.filas() > filas_antes:
            return ("fila", None)
        if abs(pos.total() - total_antes) > 0.001:
            return ("total", None)
        return None

    primero = base.esperar(listo, 15)
    if not primero:
        raise base.PasoFallido("El artículo %s no apareció en la grilla" % codigo)
    if primero[0] == "dialogo":
        dialogo = primero[1]
        # El diálogo ignora los clics mientras carga el artículo: se espera a que muestre el código.
        if not base.esperar(lambda: str(codigo) in " ".join(base.textos(dialogo)), 8):
            raise base.PasoFallido("'Modificar Cantidad' no cargó el artículo %s" % codigo)
        time.sleep(0.15)
        mas = sorted((c for c, t in base.botones(dialogo) if t == ""), key=lambda c: win32gui.GetWindowRect(c)[0])
        for _ in range(int(cantidad) - 1):
            win32gui.PostMessage(mas[-1], win32con.BM_CLICK, 0, 0)
            time.sleep(0.08)
        time.sleep(0.25)
        base.clic_boton(dialogo, "Aceptar")

        def agregado():
            return (filas_antes >= 0 and pos.filas() > filas_antes) or abs(pos.total() - total_antes) > 0.001
        if not base.esperar(agregado, 15):
            raise base.PasoFallido("Tras aceptar la cantidad el total no cambió")
    return {"total": pos.total(), "filas": pos.filas()}
