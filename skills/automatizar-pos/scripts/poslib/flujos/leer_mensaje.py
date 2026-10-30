"""leer_mensaje(nombre='mensaje', cerrar=True): espera una ventana de mensaje (Frm_Mensaje), la captura de inmediato,
lee su texto (cuadro Txt_Mensaje) y la cierra con ESC. Terminó cuando la ventana se cerró."""
import os
import time

from .. import base

NOMBRE = "leer_mensaje"
PANTALLA = "Frm_Mensaje (620x268, se cierra sola en pocos segundos)"


def ejecutar(pos, nombre="mensaje", cerrar=True, tope=60):
    def mensaje():
        for h in base.modales(pos.pid):
            if base.textos(h) and "squeda" not in base.titulo(h):
                return h
        return None

    h = base.esperar(mensaje, tope)
    if not h:
        raise base.PasoFallido("No apareció ningún mensaje")
    time.sleep(0.25)  # que termine de pintar
    ruta = base.capturar(h, os.path.join(pos.capturas, nombre + ".png"))
    titulo = base.titulo(h)
    cuerpo = [t for t in base.textos(h) if t.strip() not in (titulo.strip(), "LDCOM - Punto de Venta")]
    if cerrar:
        base.tecla(h, base.VK_ESCAPE)
        if not base.esperar_cierre(h, 3):
            try:
                base.clic_sin_texto(h, 0)
            except base.PasoFallido:
                pass
            base.esperar_cierre(h, 5)
    return {"titulo": titulo, "texto": cuerpo, "captura": ruta}
