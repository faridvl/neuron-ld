"""Clics físicos (mouse real) y pulsaciones por UIA en hilo, para lo que los mensajes Win32 no logran.

Un clic físico mueve el cursor del usuario y necesita el POS al frente: usarlo solo donde BM_CLICK/PostMessage no
funciona (teclado numérico de Denominaciones, barra de funciones paginada). Nunca con otro agente usando el equipo.
"""
import ctypes
import time

import win32gui

from . import base

ESCALA_CAPTURA = 1.25      # las coordenadas de las capturas (PrintWindow reducido) se multiplican por esto
ALT = 0x12
KEYEVENTF_KEYUP = 2
MOUSEEVENTF_IZQUIERDO_ABAJO = 2
MOUSEEVENTF_IZQUIERDO_ARRIBA = 4
ESPERA_FOCO = 0.4
ESPERA_CURSOR = 0.15
ESPERA_CLIC = 0.05
ESPERA_TRAS_CLIC = 0.7

_usuario = ctypes.windll.user32


def traer_al_frente(h):
    try:
        win32gui.SetForegroundWindow(h)
    except Exception:
        # Windows rechaza el foco si el proceso no lo tiene: tocar Alt lo habilita.
        _usuario.keybd_event(ALT, 0, 0, 0)
        _usuario.keybd_event(ALT, 0, KEYEVENTF_KEYUP, 0)
        _usuario.SetForegroundWindow(h)
    time.sleep(ESPERA_FOCO)


def _clic_en(x, y, espera_final):
    _usuario.SetCursorPos((int(x), int(y)))
    time.sleep(ESPERA_CURSOR)
    _usuario.mouse_event(MOUSEEVENTF_IZQUIERDO_ABAJO, 0, 0, 0, 0)
    time.sleep(ESPERA_CLIC)
    _usuario.mouse_event(MOUSEEVENTF_IZQUIERDO_ARRIBA, 0, 0, 0, 0)
    time.sleep(espera_final)


def clic_en_control(h_ventana, h_control):
    """Clic físico al centro de un control, con su ventana al frente."""
    traer_al_frente(h_ventana)
    izq, arr, der, aba = win32gui.GetWindowRect(h_control)
    _clic_en((izq + der) // 2, (arr + aba) // 2, ESPERA_TRAS_CLIC)


def clic_relativo(h_ventana, x_captura, y_captura):
    """Clic físico en coordenadas medidas sobre una captura de la ventana (se escalan por ESCALA_CAPTURA)."""
    traer_al_frente(h_ventana)
    izq, arr, _, _ = win32gui.GetWindowRect(h_ventana)
    _clic_en(izq + x_captura * ESCALA_CAPTURA, arr + y_captura * ESCALA_CAPTURA, ESPERA_TRAS_CLIC)


def pulsar_por_id(h_ventana, auto_id):
    """UIA Invoke sobre el control con ese AutomationId, en un hilo: si abre una modal, el Invoke no regresa."""
    def accion():
        from pywinauto.controls.uiawrapper import UIAWrapper
        from pywinauto.uia_element_info import UIAElementInfo
        for control in UIAWrapper(UIAElementInfo(h_ventana)).descendants():
            if control.element_info.automation_id == auto_id:
                control.invoke()
                return
    return base.en_hilo(accion)
