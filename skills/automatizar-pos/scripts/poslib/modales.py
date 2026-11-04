"""Manejo de modales del POS solo con Win32 (sin UIA, que se cuelga con modales abiertas).

Tres usos: describir las ventanas abiertas, vigilar y capturar los mensajes que se cierran solos, y responder
preguntas o cuadros de error .NET sin tocar el mouse.
"""
import os

import win32con
import win32gui

from . import base

CLASE_DIALOGO_ERROR = "#32770"
TEXTOS_ACEPTAR = ("ok", "aceptar")
SONDEO_MENSAJES = 0.25   # los mensajes del POS duran pocos segundos
BOTONES_DE_PREGUNTA = 2  # check (izquierda) y ESC (derecha), ambos sin texto


def describir(h):
    """Título, textos y botones de una ventana (para reportes y diagnóstico)."""
    return {
        "titulo": base.titulo(h),
        "textos": base.textos(h),
        "botones": [t for _, t in base.botones(h)],
    }


def es_pregunta(h):
    """Pregunta Sí/No del POS: exactamente dos botones visibles sin texto."""
    return len([c for c, t in base.botones(h) if t == ""]) == BOTONES_DE_PREGUNTA


def responder_pregunta(h, afirmativa=True):
    """Pulsa el check (izquierda) o ESC (derecha). Devuelve False si la ventana no es una pregunta."""
    if not es_pregunta(h):
        return False
    base.clic_sin_texto(h, 0 if afirmativa else 1)
    return True


def cerrar_errores_dotnet(pid):
    """Pulsa OK/Aceptar en los cuadros de error .NET (#32770, sin título) del proceso. Devuelve cuántos cerró."""
    cerrados = 0
    for h in base.ventanas(pid, 0):
        if base.clase(h) != CLASE_DIALOGO_ERROR:
            continue
        for c in base.descendientes(h):
            if base.clase(c) == "Button" and win32gui.GetWindowText(c).strip().lower() in TEXTOS_ACEPTAR:
                win32gui.PostMessage(c, win32con.BM_CLICK, 0, 0)
                cerrados += 1
    return cerrados


def vigilar(pid, segundos, carpeta_capturas, prefijo="modal", sondeo=SONDEO_MENSAJES):
    """Sondea durante `segundos` y, apenas aparece una modal con título, la captura y lee su texto.
    Devuelve [{titulo, textos, botones, captura}] en orden de aparición (cada ventana se reporta una vez)."""
    vistas = set()
    reportes = []

    def sondear():
        for h in base.modales(pid):
            if h in vistas or not base.titulo(h):
                continue
            vistas.add(h)
            reporte = describir(h)
            reporte["captura"] = base.capturar(h, os.path.join(carpeta_capturas, "%s-%s.png" % (prefijo, hex(h))))
            reportes.append(reporte)

    base.esperar(lambda: sondear() or False, segundos, sondeo)
    return reportes
