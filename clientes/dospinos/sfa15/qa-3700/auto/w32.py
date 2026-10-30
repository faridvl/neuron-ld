"""Ayudas win32 puras (sin UIA) para el POS: ventanas, textos, clic por BM_CLICK, filas de lista."""
import sys, time, win32gui, win32con, win32process
sys.path.insert(0, r"C:\Users\fvillacis\ClaudeLocalSession\evidencias\preventa-sucursal-destino\auto")
import pos_ui
import cap

def ventanas(pid):
    r = []
    def f(h, _):
        if win32gui.IsWindowVisible(h) and win32process.GetWindowThreadProcessId(h)[1] == pid:
            a = win32gui.GetWindowRect(h)
            if a[2] - a[0] > 80: r.append(h)
        return True
    win32gui.EnumWindows(f, None); return r

def titulo(h): return win32gui.GetWindowText(h)

def por_titulo(pid, frag):
    for h in ventanas(pid):
        if frag.lower() in titulo(h).lower(): return h

def hijos(h): return pos_ui.hijos_win32(h)

def boton(h, frag):
    """Handle del boton cuyo texto (sin espacios) empieza con frag; '' busca el que no tiene texto con indice via frag=int."""
    for c in hijos(h):
        if "BUTTON" in win32gui.GetClassName(c) and win32gui.GetWindowText(c).strip().upper().startswith(frag.upper()) and win32gui.IsWindowVisible(c):
            return c

def clic(h, frag):
    b = boton(h, frag)
    if not b: raise LookupError("sin boton " + frag)
    win32gui.PostMessage(b, win32con.BM_CLICK, 0, 0); return b

def textos(h):
    return [win32gui.GetWindowText(c) for c in hijos(h) if win32gui.GetWindowText(c) and "BUTTON" not in win32gui.GetClassName(c)]

def botones(h):
    return [win32gui.GetWindowText(c).strip() for c in hijos(h) if "BUTTON" in win32gui.GetClassName(c)]

def esperar(pid, frag, seg=20):
    fin = time.time() + seg
    while time.time() < fin:
        h = por_titulo(pid, frag)
        if h: return h
        time.sleep(0.3)

def snapshot(pid, nombre):
    out = []
    for i, h in enumerate(ventanas(pid)):
        cap.capturar(h, r"C:\Users\fvillacis\ClaudeLocalSession\sfa15\qa-3700\auto\cap\%s-%d.png" % (nombre, i))
        out.append((i, hex(h), titulo(h), textos(h)[:8], botones(h)))
    return out
