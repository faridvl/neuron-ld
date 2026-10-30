"""pagar_efectivo(): ventana 'Pago de factura' -> Enter (agrega el efectivo) + F12 (Imprimir). Si el panel ignora las teclas por
PostMessage, cae al clic del botón "+" y del botón Imprimir. Terminó cuando la ventana de pago se cierra."""
import time

import win32con
import win32gui

from .. import base

NOMBRE = "pagar_efectivo"
PANTALLA = "Pago de factura (modal, botones Efectivo/Tarjeta/Imprimir)"


def ejecutar(pos):
    pago = base.esperar_ventana(pos.pid, "Pago de factura", 20)
    if not pago:
        raise base.PasoFallido("No salió 'Pago de factura'")
    base.tecla(pago, base.VK_RETURN)
    time.sleep(0.15)
    base.tecla(pago, base.VK_F12)
    if base.esperar_cierre(pago, 2.5):
        return {"via": "teclas"}
    chicos = [c for c, t in base.botones(pago) if t == "" and
              (win32gui.GetWindowRect(c)[3] - win32gui.GetWindowRect(c)[1]) < 60]
    if chicos:
        win32gui.PostMessage(max(chicos, key=lambda c: win32gui.GetWindowRect(c)[0]), win32con.BM_CLICK, 0, 0)
        time.sleep(0.3)
    base.clic_boton(pago, "Imprimir")
    if not base.esperar_cierre(pago, 15):
        raise base.PasoFallido("'Pago de factura' no se cerró")
    return {"via": "botones"}
