"""Documento -> Credito General (F4). Uso: tipodoc_credito.py <pid>"""
import sys, time, threading
sys.path.insert(0, r"C:\Users\fvillacis\ClaudeLocalSession\sfa15\qa-3700\auto")
import w32, pos_ui, win32gui
from pywinauto import Application
pid = int(sys.argv[1])
h = w32.por_titulo(pid, "Tipos de Documentos")
if not h:
    v = pos_ui.ventana_por_manejador(pos_ui.manejador_principal(pid))
    for c in v.descendants():
        if c.element_info.automation_id == "Bn_Documento":
            threading.Thread(target=c.invoke, daemon=True).start(); break
    h = w32.esperar(pid, "Tipos de Documentos", 15)
w32.clic(h, "FACTURA DE CR"); time.sleep(2)
w = Application(backend="win32").connect(process=pid).window(handle=h)
l = [c for c in w.children() if "SysListView32" in c.class_name()]
print(l[0].texts(), flush=True); l[0].select(0); time.sleep(0.5)
w32.clic(h, "Aceptar"); time.sleep(3)
for r in w32.snapshot(pid, "tipodoc"): print(r, flush=True)
