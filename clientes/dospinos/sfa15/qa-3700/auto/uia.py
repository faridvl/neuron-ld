"""Lista/pulsa controles UIA de una ventana (por fragmento de titulo; vacio = principal).
Uso: uia.py <pid> <titulo|-> list | inv:<texto|id> | set:<id>=<valor>"""
import os, sys, time, threading
sys.path.insert(0, r"C:\Users\fvillacis\ClaudeLocalSession\evidencias\preventa-sucursal-destino\auto")
import pos_ui
pid = int(sys.argv[1]); tit = sys.argv[2]; acc = sys.argv[3]
h = pos_ui.manejador_principal(pid) if tit == "-" else pos_ui.manejador_por_titulo(pid, tit)
v = pos_ui.ventana_por_manejador(h)
ds = v.descendants()
if acc == "list":
    for c in ds:
        try:
            print(c.element_info.control_type, "|", repr(c.element_info.automation_id), "|", repr((c.window_text() or "")[:60]), flush=True)
        except Exception: pass
elif acc.startswith("inv:"):
    k = acc[4:].lower()
    for c in ds:
        try:
            if k == (c.element_info.automation_id or "").lower() or (k in (c.window_text() or "").lower() and k):
                print("invocando", c.element_info.control_type, repr(c.window_text()), flush=True)
                try:
                    threading.Thread(target=c.invoke, daemon=True).start()
                except Exception:
                    c.click_input()
                time.sleep(2); break
        except Exception: pass
elif acc.startswith("set:"):
    i, val = acc[4:].split("=", 1)
    for c in ds:
        if (c.element_info.automation_id or "") == i:
            c.set_edit_text(val); print("ok", flush=True); break
