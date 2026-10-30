"""Pulsa por UIA (Invoke en hilo) un control de la ventana principal por auto_id o texto, y vigila ventanas nuevas.
Uso: boton.py <pid> <auto_id|texto:xxx> [segundos]"""
import os, sys, time, threading
sys.path.insert(0, r"C:\Users\fvillacis\ClaudeLocalSession\evidencias\preventa-sucursal-destino\auto")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pos_ui, win32gui, win32process, cap
pid = int(sys.argv[1]); clave = sys.argv[2]; seg = float(sys.argv[3]) if len(sys.argv) > 3 else 6
principal = pos_ui.manejador_principal(pid)
ventana = pos_ui.ventana_por_manejador(principal)
objetivo = None
for c in ventana.descendants():
    try:
        if clave.startswith("texto:"):
            if clave[6:].lower() in (c.window_text() or "").lower() and c.element_info.control_type in ("Button",):
                objetivo = c; break
        elif c.element_info.automation_id == clave:
            objetivo = c; break
    except Exception:
        pass
print("objetivo:", bool(objetivo), flush=True)
threading.Thread(target=objetivo.invoke, daemon=True).start()
vistas = set(); fin = time.time() + seg
while time.time() < fin:
    def f(h, _):
        if h != principal and win32gui.IsWindowVisible(h) and win32process.GetWindowThreadProcessId(h)[1] == pid and h not in vistas:
            r = win32gui.GetWindowRect(h)
            if r[2]-r[0] > 80:
                vistas.add(h); time.sleep(0.5)
                print("VENTANA", h, repr(win32gui.GetWindowText(h)), r, flush=True)
                cap.capturar(h, os.path.join(cap.DEST, "boton-%d.png" % h))
        return True
    win32gui.EnumWindows(f, None); time.sleep(0.25)
