"""Captura todas las ventanas visibles del POS con PrintWindow (win32 puro, sin UIA). Uso: cap.py <pid> <nombre>"""
import ctypes
import os
import sys

import win32gui
import win32process
from PIL import Image

DEST = r"C:\Users\fvillacis\ClaudeLocalSession\sfa15\qa-3700\auto\cap"


def capturar(manejador, ruta):
    izq, arr, der, aba = win32gui.GetWindowRect(manejador)
    ancho, alto = der - izq, aba - arr
    if ancho < 50 or alto < 30:
        return False
    dc = ctypes.windll.user32.GetWindowDC(manejador)
    mem = ctypes.windll.gdi32.CreateCompatibleDC(dc)
    bmp = ctypes.windll.gdi32.CreateCompatibleBitmap(dc, ancho, alto)
    ctypes.windll.gdi32.SelectObject(mem, bmp)
    ctypes.windll.user32.PrintWindow(manejador, mem, 2)

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
    img.save(ruta)
    ctypes.windll.gdi32.DeleteObject(bmp)
    ctypes.windll.gdi32.DeleteDC(mem)
    ctypes.windll.user32.ReleaseDC(manejador, dc)
    return True


if __name__ == "__main__":
    pid = int(sys.argv[1])
    nombre = sys.argv[2]
    os.makedirs(DEST, exist_ok=True)
    lista = []

    def f(h, _):
        if win32gui.IsWindowVisible(h) and win32process.GetWindowThreadProcessId(h)[1] == pid:
            lista.append(h)
        return True

    win32gui.EnumWindows(f, None)
    for i, h in enumerate(lista):
        ruta = os.path.join(DEST, "%s-%d.png" % (nombre, i))
        ok = capturar(h, ruta)
        print(i, h, repr(win32gui.GetWindowText(h)), win32gui.GetWindowRect(h), ruta if ok else "(omitida)")
