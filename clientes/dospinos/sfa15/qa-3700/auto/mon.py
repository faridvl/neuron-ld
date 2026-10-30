"""Vigila ventanas nuevas N segundos (sin pulsar). Uso: mon.py <pid> <seg> [titulo_frag boton ...pares de accion automatica]"""
import sys, time
sys.path.insert(0, r"C:\Users\fvillacis\ClaudeLocalSession\sfa15\qa-3700\auto")
import w32, pos_ui, cap
pid = int(sys.argv[1]); seg = float(sys.argv[2]); pares = sys.argv[3:]
acc = list(zip(pares[0::2], pares[1::2]))
t0 = time.time(); vistas = {}
while time.time() - t0 < seg:
    pr = pos_ui.manejador_principal(pid)
    for h in w32.ventanas(pid):
        if h == pr or h in vistas: continue
        time.sleep(0.8)
        vistas[h] = 1
        try: cap.capturar(h, r"C:\Users\fvillacis\ClaudeLocalSession\sfa15\qa-3700\auto\cap\mon-%s.png" % hex(h))
        except Exception: continue
        try: print("t=%.1f" % (time.time() - t0), hex(h), repr(w32.titulo(h)), w32.textos(h)[:10], w32.botones(h), flush=True)
        except Exception: continue
        for frag, b in acc:
            if frag.lower() in w32.titulo(h).lower():
                try: w32.clic(h, b); print("   -> pulsado", b, flush=True)
                except Exception as e: print("   (no se pudo)", e, flush=True)
    time.sleep(0.25)
print("fin t=%.1f" % (time.time() - t0), flush=True)
