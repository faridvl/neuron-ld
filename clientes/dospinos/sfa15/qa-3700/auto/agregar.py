"""Agrega articulo con cantidad. Uso: agregar.py <pid> <codigo> <cantidad>"""
import sys, time, threading, win32gui, win32con
sys.path.insert(0, r"C:\Users\fvillacis\ClaudeLocalSession\sfa15\qa-3700\auto")
import w32, pos_ui
pid = int(sys.argv[1]); codigo = sys.argv[2]; cant = int(sys.argv[3])
h = w32.por_titulo(pid, "Modificar Cantidad")
if not h:
    v = pos_ui.ventana_por_manejador(pos_ui.manejador_principal(pid))
    caja = boton = None
    for c in v.descendants():
        i = c.element_info.automation_id
        if i == "Text_Articulo": caja = c
        elif i == "Btn_Agregar_Articulo": boton = c
    caja.set_edit_text(codigo)
    threading.Thread(target=boton.invoke, daemon=True).start()
    h = w32.esperar(pid, "Modificar Cantidad", 15)
mas = [c for c in w32.hijos(h) if "BUTTON" in win32gui.GetClassName(c) and win32gui.GetWindowText(c) == ""]
mas.sort(key=lambda c: win32gui.GetWindowRect(c)[0])
for _ in range(cant - 1):
    win32gui.PostMessage(mas[-1], win32con.BM_CLICK, 0, 0); time.sleep(0.15)
time.sleep(0.5)
w32.clic(h, "Aceptar"); time.sleep(3)
for r in w32.snapshot(pid, "agregar"): print(r, flush=True)
