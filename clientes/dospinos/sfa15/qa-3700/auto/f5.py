"""Pulsa F5 Imprimir Documento (hilo) y registra cada ventana nueva con hora. Uso: f5.py <pid> <segundos>"""
import sys, time, threading
sys.path.insert(0, r"C:\Users\fvillacis\ClaudeLocalSession\sfa15\qa-3700\auto")
import w32, pos_ui, cap
pid = int(sys.argv[1]); seg = float(sys.argv[2])
v = pos_ui.ventana_por_manejador(pos_ui.manejador_principal(pid))
for c in v.descendants():
    try:
        if c.element_info.control_type == "Button" and "imprimir" in (c.window_text() or "").lower():
            print("F5 ->", repr(c.window_text()), flush=True)
            threading.Thread(target=c.invoke, daemon=True).start(); break
    except Exception: pass
t0 = time.time(); vistas = {}
while time.time() - t0 < seg:
    for h in w32.ventanas(pid):
        if h == pos_ui.manejador_principal(pid) or h in vistas: continue
        time.sleep(0.7)
        vistas[h] = 1
        cap.capturar(h, r"C:\Users\fvillacis\ClaudeLocalSession\sfa15\qa-3700\auto\cap\f5-%s.png" % hex(h))
        print("t=%.1f" % (time.time() - t0), hex(h), repr(w32.titulo(h)), w32.textos(h)[:10], w32.botones(h), flush=True)
    time.sleep(0.25)
