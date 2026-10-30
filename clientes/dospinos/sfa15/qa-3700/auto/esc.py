"""Escenario completo de credito. Uso: esc.py <pid> <cantidad> <tag> [seg_f5=60] [--sin-cliente]
cliente 4000010 (MATA) -> doc credito -> articulo x cantidad -> F5 (plan row0, Confirmar simulador) -> vigila ventanas."""
import sys, time, subprocess, threading
sys.path.insert(0, r"C:\Users\fvillacis\ClaudeLocalSession\sfa15\qa-3700\auto")
import w32, pos_ui, cap
pid = int(sys.argv[1]); cant = sys.argv[2]; tag = sys.argv[3]; seg = float(sys.argv[4]) if len(sys.argv) > 4 and not sys.argv[4].startswith("--") else 60
A = r"C:\Users\fvillacis\ClaudeLocalSession\sfa15\qa-3700\auto"
E = r"C:\Users\fvillacis\ClaudeLocalSession\evidencias\preventa-sucursal-destino\auto"
def run(script, *args, t=90):
    r = subprocess.run([sys.executable, "-I", script, *args], capture_output=True, text=True, timeout=t)
    return "\n".join(l for l in r.stdout.splitlines() if "arn" not in l)
SOLO = "--solo-f5" in sys.argv
if "--sin-cliente" not in sys.argv and not SOLO:
    for _i in range(3):
        r_ = run(E + r"\cambiar_cliente.py", str(pid), "MATA", "4000010").splitlines()
        print(r_[-1] if r_ else "?", flush=True)
        if r_ and "seleccionado" in r_[-1]:
            break
        time.sleep(6)
    time.sleep(12)
print(run(A + r"\tipodoc_credito.py", str(pid)).splitlines()[0:1], flush=True)
time.sleep(3)
print("agregar:", run(A + r"\agregar.py", str(pid), "20003507", cant)[-120:], flush=True)
time.sleep(2)
v = pos_ui.ventana_por_manejador(pos_ui.manejador_principal(pid))
for c in v.descendants():
    try:
        if c.element_info.control_type == "Button" and "imprimir" in (c.window_text() or "").lower():
            threading.Thread(target=c.invoke, daemon=True).start(); break
    except Exception: pass
t0 = time.time(); vistas = {}; tf5 = None
acc = {"seleccionar tipo": "Continuar", "simulador": "Confirmar"}
while time.time() - t0 < seg:
    pr = pos_ui.manejador_principal(pid)
    for h in w32.ventanas(pid):
        if h == pr or h in vistas: continue
        time.sleep(0.8); vistas[h] = 1
        try:
            tit = w32.titulo(h)
            cap.capturar(h, A + r"\cap\%s-%s.png" % (tag, hex(h)))
            print("t=%.1f" % (time.time() - t0), hex(h), repr(tit), w32.textos(h)[:6], w32.botones(h), flush=True)
            for k, b in acc.items():
                if k in tit.lower():
                    w32.clic(h, b); print("   -> pulsado", b, flush=True)
                    if k == "simulador": tf5 = time.time()
        except Exception as e:
            pass
    time.sleep(0.25)
print("fin t=%.1f; desde Confirmar: %s" % (time.time() - t0, ("%.1f s" % (time.time() - tf5)) if tf5 else "n/a"), flush=True)
