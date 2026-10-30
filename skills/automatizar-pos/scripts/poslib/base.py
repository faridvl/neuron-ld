"""Biblioteca común para manejar el POS de LDCOM (WinForms) sin mover el mouse ni robar el foco.

Reglas: sondeo corto (PASO) en vez de esperas fijas, BM_CLICK/WM_SETTEXT por PostMessage/SendMessage,
capturas con PrintWindow, UIA solo para ubicar controles UNA vez por proceso (el escaneo tarda 5-10 s).
Ejecutar siempre con `python -I` y ocultos, con tope de tiempo.
"""
import ctypes
import json
import os
import re
import threading
import time

import win32con
import win32gui
import win32process
from PIL import Image

PASO = 0.12            # segundos entre sondeos
TOPE_VENTANA = 15.0    # tope para que aparezca una ventana
TOPE_PASO = 12.0       # tope para una condición de "terminó"
VK_RETURN, VK_ESCAPE, VK_F4, VK_F5, VK_F12 = 0x0D, 0x1B, 0x73, 0x74, 0x7B


class PasoFallido(Exception):
    """Un flujo no llegó a su condición de terminado."""


def esperar(condicion, tope=TOPE_PASO, paso=PASO):
    """Sondea `condicion()` hasta que devuelva algo verdadero; devuelve ese valor o None al agotar el tope."""
    limite = time.time() + tope
    while True:
        try:
            valor = condicion()
        except Exception:
            valor = None
        if valor:
            return valor
        if time.time() >= limite:
            return None
        time.sleep(paso)


# ---------------------------------------------------------------- ventanas (Win32)
def ventanas(pid, ancho_minimo=80):
    """Ventanas de nivel superior visibles del proceso."""
    lista = []

    def recolectar(h, _):
        if win32gui.IsWindowVisible(h) and win32process.GetWindowThreadProcessId(h)[1] == pid:
            izq, arr, der, aba = win32gui.GetWindowRect(h)
            if der - izq > ancho_minimo:
                lista.append(h)
        return True

    win32gui.EnumWindows(recolectar, None)
    return lista


def principal(pid):
    """La ventana visible más grande (los mensajes comparten título con la principal)."""
    def area(h):
        izq, arr, der, aba = win32gui.GetWindowRect(h)
        return (der - izq) * (aba - arr)
    candidatas = ventanas(pid, 0)
    return max(candidatas, key=area) if candidatas else None


def titulo(h):
    return win32gui.GetWindowText(h)


def modales(pid):
    """Ventanas visibles del proceso distintas de la principal."""
    pr = principal(pid)
    return [h for h in ventanas(pid) if h != pr]


def por_titulo(pid, fragmento):
    for h in modales(pid):
        if fragmento.lower() in titulo(h).lower():
            return h
    return None


def esperar_ventana(pid, fragmento, tope=TOPE_VENTANA):
    return esperar(lambda: por_titulo(pid, fragmento), tope)


def esperar_cierre(h, tope=TOPE_PASO):
    return esperar(lambda: not win32gui.IsWindow(h) or not win32gui.IsWindowVisible(h), tope)


def descendientes(h):
    """Todos los controles hijos (recursivo, a diferencia de EnumChildWindows directo)."""
    lista = []
    win32gui.EnumChildWindows(h, lambda c, _: lista.append(c) or True, None)
    return lista


def clase(h):
    return win32gui.GetClassName(h)


def botones(h):
    """Botones visibles descendientes: lista de (handle, texto sin saltos)."""
    return [(c, win32gui.GetWindowText(c).strip()) for c in descendientes(h)
            if "BUTTON" in clase(c).upper() and win32gui.IsWindowVisible(c)]


def textos(h):
    """Textos de los controles que no son botones (incluye cuadros de texto y etiquetas)."""
    return [t for t in (win32gui.GetWindowText(c) for c in descendientes(h)
                        if "BUTTON" not in clase(c).upper()) if t]


def clic_boton(h, fragmento):
    """BM_CLICK al botón cuyo texto empieza con `fragmento` (sin mayúsculas)."""
    for c, t in botones(h):
        if t.upper().startswith(fragmento.upper()):
            win32gui.PostMessage(c, win32con.BM_CLICK, 0, 0)
            return c
    raise PasoFallido("No hay botón que empiece con %r en %r (hay %s)" % (fragmento, titulo(h), [t for _, t in botones(h)]))


def clic_sin_texto(h, indice):
    """BM_CLICK al n-ésimo botón sin texto, ordenados de izquierda a derecha (lupa, check, ESC...)."""
    sin_texto = sorted((c for c, t in botones(h) if t == ""), key=lambda c: win32gui.GetWindowRect(c)[0])
    if indice >= len(sin_texto):
        raise PasoFallido("No hay botón sin texto #%d en %r" % (indice, titulo(h)))
    win32gui.PostMessage(sin_texto[indice], win32con.BM_CLICK, 0, 0)
    return sin_texto[indice]


def escribir(h_edit, texto):
    win32gui.SendMessage(h_edit, win32con.WM_SETTEXT, 0, texto)


def tecla(h, vk):
    """Tecla por PostMessage a una ventana/control (no usa el foco). Algunos paneles la ignoran: ver la skill."""
    win32gui.PostMessage(h, win32con.WM_KEYDOWN, vk, 0)
    win32gui.PostMessage(h, win32con.WM_KEYUP, vk, 0xC0000001)


def en_hilo(accion):
    """Invoke de UIA sobre un botón que abre una modal no regresa hasta cerrarla: va en un hilo."""
    hilo = threading.Thread(target=accion, daemon=True)
    hilo.start()
    return hilo


# ---------------------------------------------------------------- captura
def capturar(h, ruta):
    """Captura con PrintWindow aunque la ventana esté tapada. Devuelve la ruta o None."""
    izq, arr, der, aba = win32gui.GetWindowRect(h)
    ancho, alto = der - izq, aba - arr
    if ancho < 30 or alto < 30:
        return None
    dc = ctypes.windll.user32.GetWindowDC(h)
    mem = ctypes.windll.gdi32.CreateCompatibleDC(dc)
    bmp = ctypes.windll.gdi32.CreateCompatibleBitmap(dc, ancho, alto)
    ctypes.windll.gdi32.SelectObject(mem, bmp)
    ctypes.windll.user32.PrintWindow(h, mem, 2)

    class BIH(ctypes.Structure):
        _fields_ = [("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32), ("biHeight", ctypes.c_int32),
                    ("biPlanes", ctypes.c_uint16), ("biBitCount", ctypes.c_uint16), ("biCompression", ctypes.c_uint32),
                    ("biSizeImage", ctypes.c_uint32), ("a", ctypes.c_int32), ("b", ctypes.c_int32),
                    ("c", ctypes.c_uint32), ("d", ctypes.c_uint32)]

    enc = BIH(ctypes.sizeof(BIH), ancho, -alto, 1, 32, 0, 0, 0, 0, 0, 0)
    buf = ctypes.create_string_buffer(ancho * alto * 4)
    ctypes.windll.gdi32.GetDIBits(mem, bmp, 0, alto, buf, ctypes.byref(enc), 0)
    img = Image.frombuffer("RGBA", (ancho, alto), buf, "raw", "BGRA", 0, 1).convert("RGB")
    if ancho > 1000:
        img = img.resize((ancho // 2, alto // 2))
    os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
    img.save(ruta)
    ctypes.windll.gdi32.DeleteObject(bmp)
    ctypes.windll.gdi32.DeleteDC(mem)
    ctypes.windll.user32.ReleaseDC(h, dc)
    return ruta


def normalizar(texto):
    return re.sub(r"\s+", " ", texto or "").strip().lower()


# ---------------------------------------------------------------- la pantalla principal (UIA una vez)
IDS_CON_VENTANA = ("Text_Articulo", "Text_Cantidad", "Lbl_Monto_Total", "lblDatos", "lbl_Documento", "lbl_Vendedor",
                   "Bn_Cliente", "Bn_Documento", "Btn_Agregar_Articulo", "ListaArt", "Barra")


def _envoltura(handle):
    """Envoltura UIA de UN control con ventana propia: rápida, sin recorrer el árbol completo."""
    from pywinauto.controls.uiawrapper import UIAWrapper
    from pywinauto.uia_element_info import UIAElementInfo
    return UIAWrapper(UIAElementInfo(handle))


class Pos:
    """Una instancia por proceso del POS. `conectar()` ubica los controles; el resto es sondeo Win32.
    El escaneo UIA completo tarda 10-20 s (el panel de preventas tiene cientos de controles): los handles se
    guardan en un archivo temporal por proceso y las corridas siguientes los reutilizan (validados con IsWindow)."""

    def __init__(self, pid, capturas="capturas"):
        self.pid = pid
        self.capturas = capturas
        self._hwnd = {}
        self.conectado = False

    @property
    def _cache(self):
        return os.path.join(os.environ.get("TEMP", "."), "poslib-%d.json" % self.pid)

    def _desde_cache(self):
        try:
            datos = json.load(open(self._cache, encoding="utf-8"))
        except Exception:
            return False
        if not all(win32gui.IsWindow(h) for h in datos.values()) or set(datos) != set(IDS_CON_VENTANA):
            return False
        self._hwnd = datos
        return True

    def conectar(self, reintentos=4, forzar=False):
        if not forzar and self._desde_cache():
            self.conectado = True
            return self
        raiz = _envoltura(principal(self.pid))
        encontrados = {}
        for _ in range(reintentos):
            # El árbol UIA a veces llega incompleto al arrancar o tras cambiar de documento: se reintenta.
            encontrados = {}
            for c in raiz.descendants():
                try:
                    i = c.element_info.automation_id or ""
                    if i in IDS_CON_VENTANA and c.handle:
                        encontrados[i] = c.handle
                except Exception:
                    continue
            if set(encontrados) == set(IDS_CON_VENTANA):
                break
        faltan = [i for i in IDS_CON_VENTANA if i not in encontrados]
        if faltan:
            raise PasoFallido("No se ubicaron controles del POS: %s" % faltan)
        self._hwnd = encontrados
        json.dump(encontrados, open(self._cache, "w", encoding="utf-8"))
        self.conectado = True
        return self

    # --- lectura rápida (Win32, sin UIA)
    def texto(self, auto_id):
        h = self._hwnd[auto_id]
        if not win32gui.IsWindow(h):
            self.conectar(forzar=True)
            h = self._hwnd[auto_id]
        return win32gui.GetWindowText(h)

    def total(self):
        """Total del documento como número (₡ 32,486.65 -> 32486.65)."""
        limpio = re.sub(r"[^\d.]", "", self.texto("Lbl_Monto_Total").replace(",", ""))
        return float(limpio) if limpio else 0.0

    def filas(self):
        """Cantidad de líneas de la grilla, o -1 si no se puede leer."""
        try:
            return len(_envoltura(self._hwnd["ListaArt"]).children())
        except Exception:
            return -1

    def principal(self):
        return principal(self.pid)

    # --- acciones
    def invocar(self, auto_id):
        """Pulsa un botón con ventana propia por BM_CLICK (UIA Invoke sobre un elemento tomado por handle falla con COMError)."""
        win32gui.PostMessage(self._hwnd[auto_id], win32con.BM_CLICK, 0, 0)

    def pulsar_barra(self, texto):
        """Pulsa un botón de la barra F1..F12 por texto (p. ej. 'imprimir documento'). Los botones de la barra no tienen
        ventana propia: se leen de la barra con UIA en el momento (son pocos)."""
        clave = normalizar(texto)
        botones_barra = _envoltura(self._hwnd["Barra"]).children()
        for boton in botones_barra:
            if clave in normalizar(boton.window_text()):
                en_hilo(boton.invoke)
                return normalizar(boton.window_text())
        raise PasoFallido("No hay botón de barra %r (hay %s)" % (texto, [normalizar(b.window_text()) for b in botones_barra]))

    def captura(self, nombre, h=None):
        h = h or self.principal()
        return capturar(h, os.path.join(self.capturas, "%s.png" % nombre))
